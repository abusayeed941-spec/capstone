# ============================================
# Terraform Main — E-Commerce Cloud Infrastructure
# AWS Provider — Production-Ready Setup
# ============================================

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # Uncomment for remote state (recommended for team collaboration)
  # backend "s3" {
  #   bucket = "ecommerce-capstone-tf-state"
  #   key    = "infrastructure/terraform.tfstate"
  #   region = var.aws_region
  #   dynamodb_table = "terraform-locks"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "E-Commerce Capstone"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Owner       = var.owner
    }
  }
}

# ============================================
# Module: VPC & Networking
# ============================================

module "vpc" {
  source = "./modules/vpc"

  vpc_cidr           = var.vpc_cidr
  public_subnet_cidrs = var.public_subnet_cidrs
  private_subnet_cidrs = var.private_subnet_cidrs
  availability_zones  = var.availability_zones
  environment         = var.environment

  enable_nat_gateway = true
  single_nat_gateway = true  # Cost optimization: 1 NAT GW for non-production
}

# ============================================
# Module: Security Groups
# ============================================

module "security_groups" {
  source = "./modules/security_groups"

  vpc_id = module.vpc.vpc_id

  # ALB security group — allow HTTP/HTTPS from internet
  alb_sg_name        = "alb-sg"
  alb_ssh_cidr       = var.bastion_cidr
  alb_http_cidrs     = ["0.0.0.0/0"]
  alb_https_cidrs    = ["0.0.0.0/0"]

  # Bastion security group — SSH from your IP only
  bastion_sg_name    = "bastion-sg"
  bastion_ssh_cidr   = var.your_ip_cidr  # Set to your IP: e.g., "203.0.113.0/32"

  # EC2 instances security group — SSH from bastion only, app ports
  ec2_sg_name        = "ec2-sg"
  ec2_ssh_cidr       = module.vpc.public_subnet_cidrs
  ec2_app_ports      = [var.app_port, 3000, 9090]
  ec2_k8s_ports      = [6443, 8080, 10250]

  # Database security group — MySQL from EC2 instances only
  db_sg_name         = "db-sg"
  db_cidr            = module.vpc.private_subnet_cidrs
  db_port            = 3306

  # Kubernetes node-to-node communication
  k8s_sg_name        = "k8s-sg"
  k8s_node_cidrs     = module.vpc.private_subnet_cidrs
}

# ============================================
# Module: IAM
# ============================================

module "iam" {
  source = "./modules/iam"

  project_name = "ecommerce-capstone"

  # IAM users for team members
  admin_users = ["admin-user"]
  developer_users = ["dev-user"]

  # IAM role for EC2 instances (instance profile)
  create_ec2_role = true
  ec2_role_name   = "ecommerce-ec2-role"

  # Policies attached to EC2 role
  ec2_policy_arns = [
    "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy",
    "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore",
  ]
}

# ============================================
# Module: EC2 Instances
# ============================================

module "ec2" {
  source = "./modules/ec2"

  vpc_id              = module.vpc.vpc_id
  public_subnet_ids   = module.vpc.public_subnet_ids
  private_subnet_ids  = module.vpc.private_subnet_ids
  security_group_ids  = module.security_groups.ec2_sg_id
  k8s_security_group  = module.security_groups.k8s_sg_id

  bastion_ami         = data.aws_ami.rhel8.id
  bastion_instance_type = "t2.micro"
  bastion_key_name    = var.key_pair_name
  bastion_count       = 1

  k8s_master_ami      = data.aws_ami.rhel8.id
  k8s_master_instance_type = "t2.micro"
  k8s_master_key_name = var.key_pair_name
  k8s_master_count    = 1

  k8s_worker_ami      = data.aws_ami.rhel8.id
  k8s_worker_instance_type = "t3.micro"
  k8s_worker_key_name = var.key_pair_name
  k8s_worker_count    = 2

  iam_instance_profile = module.iam.ec2_instance_profile_name

  # User data for K8s nodes
  bastion_user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y git wget curl
              EOF

  k8s_master_user_data = <<-EOF
              #!/bin/bash
              setenforce 0
              yum update -y
              yum install -y docker kubernetes kubelet kubeadm
              systemctl enable --now docker kubelet
              EOF

  k8s_worker_user_data = <<-EOF
              #!/bin/bash
              setenforce 0
              yum update -y
              yum install -y docker kubernetes kubelet kubeadm
              systemctl enable --now docker kubelet
              EOF

  tags = {
    Role = "ecommerce-infra"
  }
}

# ============================================
# S3 Bucket for Product Images
# ============================================

resource "aws_s3_bucket" "product_images" {
  bucket = "ecommerce-${var.environment}-product-images-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_public_access_block" "product_images" {
  bucket = aws_s3_bucket.product_images.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "product_images" {
  bucket = aws_s3_bucket.product_images.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "product_images" {
  bucket = aws_s3_bucket.product_images.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_logging" "product_images" {
  bucket = aws_s3_bucket.product_images.id
  target_bucket = aws_s3_bucket.access_logs.id
  target_prefix = "product-images/"
}

# Access logs bucket
resource "aws_s3_bucket" "access_logs" {
  bucket = "ecommerce-${var.environment}-access-logs-${data.aws_caller_identity.current.account_id}"
}

# ============================================
# Data sources
# ============================================

data "aws_caller_identity" "current" {}

data "aws_ami" "rhel8" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["RHEL-8.*/x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# ============================================
# Outputs
# ============================================

output "vpc_id" {
  value = module.vpc.vpc_id
  description = "VPC ID"
}

output "public_subnet_ids" {
  value = module.vpc.public_subnet_ids
  description = "Public subnet IDs"
}

output "private_subnet_ids" {
  value = module.vpc.private_subnet_ids
  description = "Private subnet IDs"
}

output "bastion_public_ip" {
  value = module.ec2.bastion_public_ip
  description = "Bastion host public IP"
}

output "k8s_master_public_ip" {
  value = module.ec2.k8s_master_public_ip
  description = "K8s master public IP"
}

output "k8s_worker_public_ips" {
  value = module.ec2.k8s_worker_public_ips
  description = "K8s worker public IPs"
}

output "product_images_bucket_name" {
  value = aws_s3_bucket.product_images.bucket
  description = "S3 bucket for product images"
}

output "account_id" {
  value = data.aws_caller_identity.current.account_id
}
