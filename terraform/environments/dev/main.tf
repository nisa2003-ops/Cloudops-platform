terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # NOTE: To enable remote state after running terraform/bootstrap, uncomment this backend block:
  # backend "s3" {
  #   bucket         = "cloudops-tfstate-nisadu"
  #   key            = "dev/terraform.tfstate"
  #   region         = "us-east-1"
  #   dynamodb_table = "cloudops-tf-locks"
  #   encrypt        = true
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "CloudOps"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# 1. Networking (VPC, Subnet, Route Table, IGW)
module "vpc" {
  source             = "../../modules/vpc"
  vpc_cidr           = var.vpc_cidr
  public_subnet_cidr = var.public_subnet_cidr
  availability_zone  = var.availability_zone
  environment        = var.environment
}

# 2. Security Groups (Application Port 8000 + Egress)
module "security_groups" {
  source                = "../../modules/security_groups"
  vpc_id                = module.vpc.vpc_id
  environment           = var.environment
  allowed_ingress_cidrs = var.allowed_ingress_cidrs
}

# 3. IAM (Instance profile for SSM + ECR access, optional GitHub Actions OIDC)
module "iam" {
  source             = "../../modules/iam"
  environment        = var.environment
  enable_github_oidc = var.enable_github_oidc
  github_repository  = var.github_repository
}

# 4. Amazon ECR (Container image registry with automated vulnerability scanning)
module "ecr" {
  source      = "../../modules/ecr"
  environment = var.environment
}

# 5. EC2 Server Host (Amazon Linux 2023 with Docker & SSM Agent)
module "ec2" {
  source               = "../../modules/ec2"
  environment          = var.environment
  instance_type        = var.instance_type
  subnet_id            = module.vpc.public_subnet_id
  security_group_id    = module.security_groups.app_security_group_id
  iam_instance_profile = module.iam.instance_profile_name
}