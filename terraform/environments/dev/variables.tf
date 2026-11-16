variable "aws_region" {
  description = "AWS deployment region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "dev"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidr" {
  description = "CIDR block for the public subnet"
  type        = string
  default     = "10.0.1.0/24"
}

variable "availability_zone" {
  description = "AWS availability zone"
  type        = string
  default     = "us-east-1a"
}

variable "allowed_ingress_cidrs" {
  description = "Allowed CIDR blocks for HTTP ingress (e.g. your IP address /32 or 0.0.0.0/0)"
  type        = list(string)
  default     = ["0.0.0.0/0"]
}

variable "instance_type" {
  description = "EC2 instance size (Free tier eligible)"
  type        = string
  default     = "t3.micro"
}

variable "enable_github_oidc" {
  description = "Whether to provision GitHub Actions OIDC deployment role"
  type        = bool
  default     = false
}

variable "github_repository" {
  description = "GitHub repository identifier in format 'username/repo-name'"
  type        = string
  default     = ""
}