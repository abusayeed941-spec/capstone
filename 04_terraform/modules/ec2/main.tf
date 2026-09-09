# EC2 Module — Bastion + K8s Master + K8s Workers

variable "vpc_id" {
  type = string
}

variable "public_subnet_ids" {
  type = list(string)
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "security_group_ids" {
  type = list(string)
}

variable "k8s_security_group" {
  type    = string
  default = ""
}

variable "bastion_ami" {
  type = string
}

variable "bastion_instance_type" {
  type    = string
  default = "t2.micro"
}

variable "bastion_key_name" {
  type    = string
  default = ""
}

variable "bastion_count" {
  type    = number
  default = 1
}

variable "bastion_user_data" {
  type    = string
  default = ""
}

variable "k8s_master_ami" {
  type = string
}

variable "k8s_master_instance_type" {
  type    = string
  default = "t2.micro"
}

variable "k8s_master_key_name" {
  type    = string
  default = ""
}

variable "k8s_master_count" {
  type    = number
  default = 1
}

variable "k8s_master_user_data" {
  type    = string
  default = ""
}

variable "k8s_worker_ami" {
  type = string
}

variable "k8s_worker_instance_type" {
  type    = string
  default = "t3.micro"
}

variable "k8s_worker_key_name" {
  type    = string
  default = ""
}

variable "k8s_worker_count" {
  type    = number
  default = 2
}

variable "k8s_worker_user_data" {
  type    = string
  default = ""
}

variable "iam_instance_profile" {
  type    = string
  default = ""
}

variable "tags" {
  type    = map(string)
  default = {}
}

# --- Bastion Host ---
resource "aws_instance" "bastion" {
  count                  = var.bastion_count
  ami                    = var.bastion_ami
  instance_type          = var.bastion_instance_type
  subnet_id              = var.public_subnet_ids[0]
  vpc_security_group_ids = var.security_group_ids
  key_name               = var.bastion_key_name
  iam_instance_profile   = var.iam_instance_profile != "" ? var.iam_instance_profile : null
  user_data              = var.bastion_user_data != "" ? var.bastion_user_data : null

  associate_public_ip_address = true

  tags = merge({
    Name = "ecommerce-bastion"
    Role = "bastion"
  }, var.tags)

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 10
    delete_on_termination = true
    encrypted             = true
  }
}

# --- K8s Master ---
resource "aws_instance" "k8s_master" {
  count                  = var.k8s_master_count
  ami                    = var.k8s_master_ami
  instance_type          = var.k8s_master_instance_type
  subnet_id              = var.private_subnet_ids[0]
  vpc_security_group_ids = concat(var.security_group_ids, [var.k8s_security_group != "" ? var.k8s_security_group : aws_security_group.k8s[0].id])
  key_name               = var.k8s_master_key_name
  iam_instance_profile   = var.iam_instance_profile != "" ? var.iam_instance_profile : null
  user_data              = var.k8s_master_user_data != "" ? var.k8s_master_user_data : null

  associate_public_ip_address = false

  tags = merge({
    Name = "ecommerce-k8s-master"
    Role = "k8s-master"
  }, var.tags)

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 20
    delete_on_termination = true
    encrypted             = true
  }
}

# --- K8s Workers ---
resource "aws_instance" "k8s_worker" {
  count                  = var.k8s_worker_count
  ami                    = var.k8s_worker_ami
  instance_type          = var.k8s_worker_instance_type
  subnet_id              = var.private_subnet_ids[count.index % length(var.private_subnet_ids)]
  vpc_security_group_ids = concat(var.security_group_ids, [var.k8s_security_group != "" ? var.k8s_security_group : aws_security_group.k8s[0].id])
  key_name               = var.k8s_worker_key_name
  iam_instance_profile   = var.iam_instance_profile != "" ? var.iam_instance_profile : null
  user_data              = var.k8s_worker_user_data != "" ? var.k8s_worker_user_data : null

  associate_public_ip_address = false

  tags = merge({
    Name = "ecommerce-k8s-worker-${count.index + 1}"
    Role = "k8s-worker"
  }, var.tags)

  root_block_device {
    volume_type           = "gp3"
    volume_size           = 20
    delete_on_termination = true
    encrypted             = true
  }
}

# --- EBS Volumes for K8s PVs ---
resource "aws_ebs_volume" "k8s_data" {
  count             = var.k8s_worker_count
  availability_zone = var.private_subnet_ids[count.index % length(var.private_subnet_ids)]
  size              = 20
  type              = "gp3"
  encrypted         = true

  tags = {
    Name = "ecommerce-k8s-data-${count.index + 1}"
    Role = "k8s-pv"
  }
}

resource "aws_volume_attachment" "k8s_data_attach" {
  count       = var.k8s_worker_count
  device_name = "/dev/xvdf"
  volume_id   = aws_ebs_volume.k8s_data[count.index].id
  instance_id = aws_instance.k8s_worker[count.index].id
}

# --- ALB ---
# (Referenced in main.tf — simplified here)
# resource "aws_lb" "alb" { ... }
# resource "aws_lb_target_group" "alb_tg" { ... }
# resource "aws_lb_target_group_attachment" "alb_tg_attach" { ... }

# ============================================
# Outputs
# ============================================

output "bastion_public_ip" {
  value = aws_instance.bastion[0].public_ip
  description = "Bastion host public IP"
}

output "bastion_private_ip" {
  value = aws_instance.bastion[0].private_ip
  description = "Bastion host private IP"
}

output "k8s_master_public_ip" {
  value = aws_instance.k8s_master[0].public_ip
  description = "K8s master public IP (if assigned)"
}

output "k8s_master_private_ip" {
  value = aws_instance.k8s_master[0].private_ip
  description = "K8s master private IP"
}

output "k8s_worker_public_ips" {
  value     = aws_instance.k8s_worker[*].public_ip
  ephemeral = true
  description = "K8s worker public IPs (if assigned)"
}

output "k8s_worker_private_ips" {
  value = aws_instance.k8s_worker[*].private_ip
  description = "K8s worker private IPs"
}

output "k8s_worker_instance_ids" {
  value = aws_instance.k8s_worker[*].id
  description = "K8s worker instance IDs"
}

output "ebs_volume_ids" {
  value = aws_ebs_volume.k8s_data[*].id
  description = "EBS volume IDs for K8s PVs"
}
