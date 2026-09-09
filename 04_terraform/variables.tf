# ============================================
# Terraform Variables — E-Commerce Infrastructure
# ============================================

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "dev"
}

variable "owner" {
  description = "Project owner name"
  type        = string
  default     = "student"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets"
  type        = list(string)
  default = [
    "10.0.1.0/24",
    "10.0.2.0/24",
  ]
}

variable "private_subnet_cidrs" {
  description = "CIDR blocks for private subnets"
  type        = list(string)
  default = [
    "10.0.10.0/24",
    "10.0.11.0/24",
  ]
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
  default = [
    "us-east-1a",
    "us-east-1b",
  ]
}

variable "key_pair_name" {
  description = "EC2 key pair name for SSH access"
  type        = string
  default     = "ecommerce-key"
}

variable "your_ip_cidr" {
  description = "Your IP address CIDR for bastion SSH access (e.g. 203.0.113.5/32)"
  type        = string
  default     = "0.0.0.0/0"  # WARNING: Change this to your actual IP in production!
}

variable "bastion_cidr" {
  description = "CIDR for bastion subnet (used for ALB SSH allowlist)"
  type        = string
  default     = "10.0.1.0/24"
}

variable "app_port" {
  description = "Backend application port"
  type        = number
  default     = 5000
}
