variable "aws_region" {
  description = "AWS region for provisioning"
  type        = string
  default     = "us-east-1"
}

variable "state_bucket_name" {
  description = "Globally unique name for the remote state S3 bucket"
  type        = string
  default     = "cloudops-tfstate-nisadu"
}

variable "lock_table_name" {
  description = "DynamoDB table name for state locking"
  type        = string
  default     = "cloudops-tf-locks"
}