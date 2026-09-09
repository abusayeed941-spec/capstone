# Security Groups Module

variable "vpc_id" {
  type = string
}

variable "alb_sg_name" {
  type = string
}

variable "alb_ssh_cidr" {
  type = string
}

variable "alb_http_cidrs" {
  type = list(string)
}

variable "alb_https_cidrs" {
  type = list(string)
}

variable "bastion_sg_name" {
  type    = string
  default = "bastion-sg"
}

variable "bastion_ssh_cidr" {
  type = string
}

variable "ec2_sg_name" {
  type = string
}

variable "ec2_ssh_cidr" {
  type = string
}

variable "ec2_app_ports" {
  type = list(number)
  default = [5000]
}

variable "ec2_k8s_ports" {
  type = list(number)
  default = [6443, 8080]
}

variable "db_sg_name" {
  type    = string
  default = "db-sg"
}

variable "db_cidr" {
  type = string
}

variable "db_port" {
  type    = number
  default = 3306
}

variable "k8s_sg_name" {
  type    = string
  default = "k8s-sg"
}

variable "k8s_node_cidrs" {
  type = string
}

# --- ALB Security Group ---
resource "aws_security_group" "alb" {
  name        = var.alb_sg_name
  description = "ALB security group — HTTP/HTTPS from internet"
  vpc_id      = var.vpc_id

  ingress {
    description = "HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = var.alb_http_cidrs
  }

  ingress {
    description = "HTTPS from internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = var.alb_https_cidrs
  }

  ingress {
    description = "SSH from bastion"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.alb_ssh_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = var.alb_sg_name
  }
}

# --- Bastion Security Group ---
resource "aws_security_group" "bastion" {
  name        = var.bastion_sg_name
  description = "Bastion host — SSH from your IP only"
  vpc_id      = var.vpc_id

  ingress {
    description = "SSH from your IP"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.bastion_ssh_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = var.bastion_sg_name
  }
}

# --- EC2 Instances Security Group ---
resource "aws_security_group" "ec2" {
  name        = var.ec2_sg_name
  description = "EC2 instances — SSH from bastion, app ports open"
  vpc_id      = var.vpc_id

  ingress {
    description = "SSH from bastion (private subnet)"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ec2_ssh_cidr]
  }

  dynamic "ingress" {
    for_each = var.ec2_app_ports
    content {
      description = "App port ${ingress.value}"
      from_port   = ingress.value
      to_port     = ingress.value
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }

  dynamic "ingress" {
    for_each = var.ec2_k8s_ports
    content {
      description = "K8s port ${ingress.value}"
      from_port   = ingress.value
      to_port     = ingress.value
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = var.ec2_sg_name
  }
}

# --- Database Security Group ---
resource "aws_security_group" "db" {
  name        = var.db_sg_name
  description = "Database — MySQL from EC2 instances only"
  vpc_id      = var.vpc_id

  ingress {
    description = "MySQL from private subnet"
    from_port   = var.db_port
    to_port     = var.db_port
    protocol    = "tcp"
    cidr_blocks = [var.db_cidr]
  }

  ingress {
    description = "MySQL from EC2 SG (self-reference)"
    from_port   = var.db_port
    to_port     = var.db_port
    protocol    = "tcp"
    security_groups = [aws_security_group.ec2.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = var.db_sg_name
  }
}

# --- Kubernetes Security Group ---
resource "aws_security_group" "k8s" {
  name        = var.k8s_sg_name
  description = "Kubernetes — node-to-node communication"
  vpc_id      = var.vpc_id

  ingress {
    description = "All traffic from K8s nodes"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = [var.k8s_node_cidrs]
  }

  ingress {
    description = "K8s API server"
    from_port   = 6443
    to_port     = 6443
    protocol    = "tcp"
    cidr_blocks = [var.k8s_node_cidrs]
  }

  ingress {
    description = "Kubelet"
    from_port   = 10250
    to_port     = 10250
    protocol    = "tcp"
    cidr_blocks = [var.k8s_node_cidrs]
  }

  ingress {
    description = "Ingress/NodePort"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = [var.k8s_node_cidrs]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = var.k8s_sg_name
  }
}

# ============================================
# Outputs
# ============================================

output "alb_sg_id" {
  value = aws_security_group.alb.id
}

output "bastion_sg_id" {
  value = aws_security_group.bastion.id
}

output "ec2_sg_id" {
  value = aws_security_group.ec2.id
}

output "db_sg_id" {
  value = aws_security_group.db.id
}

output "k8s_sg_id" {
  value = aws_security_group.k8s.id
}
