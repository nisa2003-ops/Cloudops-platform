# CloudOps Security, IAM, and Compliance Guide

## 1. Zero-Trust Access Strategy

### 1.1 Why No SSH (Port 22)?
In standard novice deployments, EC2 instances expose SSH on port 22 with `.pem` key pairs. This introduces significant risks:
- Key leakage or improper storage in Git.
- Exposure to brute-force automated scanning on the public internet.
- Lack of centralized audit logging.

**CloudOps Solution**:
- Port 22 is **closed** in the AWS Security Group.
- Instance access is governed by **AWS Systems Manager (SSM) Session Manager**.
- All admin sessions are authenticated through IAM, encrypted via TLS, and logged to CloudWatch/CloudTrail.

### 1.2 GitHub Actions OIDC Authentication
Instead of creating static `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` credentials in GitHub repository secrets, CloudOps uses **OIDC (OpenID Connect) federation**:
1. When a GitHub Actions workflow executes, GitHub generates an ephemeral OIDC JWT token.
2. The workflow exchanges this token with AWS STS (`AssumeRoleWithWebIdentity`).
3. AWS validates the cryptographic signature and checks the subject claim condition:
   `repo:nisa03-cloud/Cloudops:*`
4. AWS issues temporary credentials valid for 1 hour.
5. No static credentials ever exist to be compromised.

---

## 2. Container Image Hardening

1. **Multi-Stage Build**: Development dependencies and build tools (`build-essential`) are isolated to the build stage and excluded from the production image.
2. **Non-Root Execution**: Container runs under user `cloudops` (UID 10001). This prevents container breakout exploits from escalating privileges on the Linux host.
3. **Automated Vulnerability Scanning**:
   - **CI Scanning**: Trivy scans images for OS package and Python library CVEs before pushing to registry.
   - **Registry Scanning**: Amazon ECR scans every image tag upon push (`scan_on_push = true`).

---

## 3. Terraform State Security

- State files contain sensitive metadata (resource IDs, IP addresses, configurations).
- In the `terraform/bootstrap` module:
  - S3 bucket versioning is enabled for audit recovery.
  - Server-Side Encryption (`AES256`) is enforced.
  - Public access block is strictly enforced on all 4 settings.
  - State locks are maintained in DynamoDB to prevent concurrent pipeline write corruption.
