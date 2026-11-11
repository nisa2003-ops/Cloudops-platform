output "state_bucket_name" {
  description = "The name of the remote state S3 bucket"
  value       = aws_s3_bucket.terraform_state.id
}

output "dynamodb_table_name" {
  description = "The name of the DynamoDB lock table"
  value       = aws_dynamodb_table.terraform_locks.id
}