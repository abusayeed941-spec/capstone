# ============================================
# Terraform Outputs
# ============================================

output "vpc_id" {
  value       = module.vpc.vpc_id
  description = "ID of the VPC"
}

output "public_subnet_ids" {
  value       = module.vpc.public_subnet_ids
  description = "IDs of public subnets"
}

output "private_subnet_ids" {
  value       = module.vpc.private_subnet_ids
  description = "IDs of private subnets"
}

output "alb_dns_name" {
  value       = module.alb.alb_dns_name
  description = "ALB DNS name"
}

output "bastion_public_ip" {
  value       = module.ec2.bastion_public_ip
  description = "Bastion host public IP"
}

output "k8s_master_public_ip" {
  value       = module.ec2.k8s_master_public_ip
  description = "K8s master public IP"
}

output "k8s_worker_public_ips" {
  value       = module.ec2.k8s_worker_public_ips
  description = "K8s worker public IPs"
}

output "product_images_bucket" {
  value       = aws_s3_bucket.product_images.bucket
  description = "S3 bucket for product images"
}

output "ecommerce_db_endpoint" {
  value       = module.db.rds_endpoint
  description = "Database endpoint"
}
