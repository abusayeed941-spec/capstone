# VPC Module — E-Commerce Infrastructure
# Creates VPC, subnets, route tables, NAT gateway, IGW

variable "vpc_cidr" {
  type = string
}

variable "public_subnet_cidrs" {
  type = list(string)
}

variable "private_subnet_cidrs" {
  type = list(string)
}

variable "availability_zones" {
  type = list(string)
}

variable "environment" {
  type = string
}

variable "enable_nat_gateway" {
  type    = bool
  default = true
}

variable "single_nat_gateway" {
  type    = bool
  default = true
}

data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "ecommerce-${var.environment}-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "ecommerce-${var.environment}-igw"
  }
}

# Elastic IP for NAT Gateway
resource "aws_eip" "nat" {
  count = var.enable_nat_gateway && var.single_nat_gateway ? 1 : 0
  domain = "vpc"

  tags = {
    Name = "ecommerce-${var.environment}-nat-eip"
  }
}

# NAT Gateway
resource "aws_nat_gateway" "nat" {
  count = var.enable_nat_gateway && var.single_nat_gateway ? 1 : 0
  allocation_id = aws_eip.nat[0].id
  subnet_id     = aws_subnet.public[0].id

  tags = {
    Name = "ecommerce-${var.environment}-nat"
  }

  depends_on = [aws_internet_gateway.igw]
}

# Public Subnets
resource "aws_subnet" "public" {
  count                   = length(var.public_subnet_cidrs)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index % length(var.availability_zones)]
  map_public_ip_on_launch = true

  tags = {
    Name = "ecommerce-${var.environment}-public-${count.index + 1}"
    Tier = "public"
  }
}

# Private Subnets
resource "aws_subnet" "private" {
  count             = length(var.private_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index % length(var.availability_zones)]

  tags = {
    Name = "ecommerce-${var.environment}-private-${count.index + 1}"
    Tier = "private"
  }
}

# Route Table — Public (via IGW)
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "ecommerce-${var.environment}-public-rt"
  }
}

# Route Table — Private (via NAT)
resource "aws_route_table" "private" {
  count  = var.enable_nat_gateway ? 1 : 0
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat[0].id
  }

  tags = {
    Name = "ecommerce-${var.environment}-private-rt"
  }

  depends_on = [aws_nat_gateway.nat]
}

# Route Table Associations — Public
resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Route Table Associations — Private
resource "aws_route_table_association" "private" {
  count          = length(aws_subnet.private)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private[0].id
}

# Network ACLs — allow standard traffic
resource "aws_network_acl" "main" {
  vpc_id = aws_vpc.main.id

  ingress {
    protocol   = -1
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 0
    to_port    = 0
  }

  egress {
    protocol   = -1
    rule_no    = 100
    action     = "allow"
    cidr_block = "0.0.0.0/0"
    from_port  = 0
    to_port    = 0
  }

  tags = {
    Name = "ecommerce-${var.environment}-nacl"
  }
}

resource "aws_network_acl_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  network_acl_id = aws_network_acl.main.id
}

resource "aws_network_acl_association" "private" {
  count          = length(aws_subnet.private)
  subnet_id      = aws_subnet.private[count.index].id
  network_acl_id = aws_network_acl.main.id
}

# ============================================
# Outputs
# ============================================

output "vpc_id" {
  value = aws_vpc.main.id
}

output "public_subnet_ids" {
  value = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  value = aws_subnet.private[*].id
}

output "public_subnet_cidrs" {
  value = aws_subnet.public[*].cidr_block
}

output "private_subnet_cidrs" {
  value = aws_subnet.private[*].cidr_block
}
