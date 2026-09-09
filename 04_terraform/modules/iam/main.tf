# IAM Module — Users, Groups, Roles, Policies

variable "project_name" {
  type = string
  default = "ecommerce-capstone"
}

variable "admin_users" {
  type    = list(string)
  default = []
}

variable "developer_users" {
  type    = list(string)
  default = []
}

variable "create_ec2_role" {
  type    = bool
  default = true
}

variable "ec2_role_name" {
  type    = string
  default = "ecommerce-ec2-role"
}

variable "ec2_policy_arns" {
  type    = list(string)
  default = []
}

# --- Admin Group ---
resource "aws_iam_group" "admin" {
  count = length(var.admin_users) > 0 ? 1 : 0
  name  = "${var.project_name}-admins"

  tags = {
    Project = var.project_name
  }
}

resource "aws_iam_group_policy_attachment" "admin_full" {
  count      = length(var.admin_users) > 0 ? 1 : 0
  group      = aws_iam_group.admin[0].name
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

# --- Developer Group ---
resource "aws_iam_group" "developers" {
  count = length(var.developer_users) > 0 ? 1 : 0
  name  = "${var.project_name}-developers"

  tags = {
    Project = var.project_name
  }
}

resource "aws_iam_group_policy_attachment" "developers_readonly" {
  count      = length(var.developer_users) > 0 ? 1 : 0
  group      = aws_iam_group.developers[0].name
  policy_arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
}

# --- Admin Users ---
resource "aws_iam_user" "admin" {
  count = length(var.admin_users)
  name  = var.admin_users[count.index]

  tags = {
    Project = var.project_name
  }
}

resource "aws_iam_user_group_membership" "admin_membership" {
  count = length(var.admin_users) > 0 ? 1 : 0
  user  = aws_iam_user.admin[0].name
  groups = [aws_iam_group.admin[0].name]
}

# --- Developer Users ---
resource "aws_iam_user" "developer" {
  count = length(var.developer_users)
  name  = var.developer_users[count.index]

  tags = {
    Project = var.project_name
  }
}

resource "aws_iam_user_group_membership" "developer_membership" {
  count = length(var.developer_users) > 0 ? 1 : 0
  user  = aws_iam_user.developer[0].name
  groups = [aws_iam_group.developers[0].name]
}

# --- EC2 Instance Role ---
resource "aws_iam_role" "ec2_role" {
  count = var.create_ec2_role ? 1 : 0
  name  = var.ec2_role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Project = var.project_name
  }
}

resource "aws_iam_role_policy_attachment" "ec2_policies" {
  count      = var.create_ec2_role ? length(var.ec2_policy_arns) : 0
  role       = aws_iam_role.ec2_role[0].name
  policy_arn = var.ec2_policy_arns[count.index]
}

resource "aws_iam_instance_profile" "ec2_profile" {
  count = var.create_ec2_role ? 1 : 0
  name  = "${var.ec2_role_name}-profile"

  role = aws_iam_role.ec2_role[0].name
}

# ============================================
# Outputs
# ============================================

output "admin_user_names" {
  value     = aws_iam_user.admin[*].name
  ephemeral = true
  description = "Admin IAM user names (passwords not stored)"
}

output "developer_user_names" {
  value     = aws_iam_user.developer[*].name
  ephemeral = true
  description = "Developer IAM user names"
}

output "ec2_role_arn" {
  value       = var.create_ec2_role ? aws_iam_role.ec2_role[0].arn : ""
  description = "EC2 instance role ARN"
}

output "ec2_instance_profile_name" {
  value       = var.create_ec2_role ? aws_iam_instance_profile.ec2_profile[0].name : ""
  description = "EC2 instance profile name for attaching to instances"
}
