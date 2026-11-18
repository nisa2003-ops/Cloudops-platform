output "ec2_public_ip" {
  description = "Public IP address of the CloudOps server"
  value       = module.ec2.public_ip
}

output "application_url" {
  description = "Live HTTP URL for the CloudOps API"
  value       = "http://${module.ec2.public_ip}:8000"
}

output "metrics_url" {
  description = "Live Prometheus metrics endpoint"
  value       = "http://${module.ec2.public_ip}:8000/metrics"
}

output "ecr_repository_url" {
  description = "ECR repository URL for publishing Docker images"
  value       = module.ecr.repository_url
}

output "ssm_connect_command" {
  description = "AWS CLI command to connect securely without SSH keys or exposed port 22"
  value       = "aws ssm start-session --target ${module.ec2.instance_id}"
}

output "github_actions_role_arn" {
  description = "IAM Role ARN for GitHub Actions OIDC deployment"
  value       = module.iam.github_actions_role_arn
}