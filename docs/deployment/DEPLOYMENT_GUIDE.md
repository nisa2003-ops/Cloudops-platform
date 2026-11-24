# CloudOps Deployment Guide

This guide covers local development, containerized deployment with Docker Compose, and cloud deployment via Terraform on AWS.

---

## 1. Local Development (Fast Feedback Loop)

### Prerequisites
- Python 3.11+
- Virtual environment (`.venv`)

### Execution
```powershell
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# 3. Run automated tests
pytest -v

# 4. Start local development server
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 2. Local Container Stack (App + Prometheus + Grafana)

Verify the full microservice and observability stack locally using Docker Compose before touching the cloud.

```powershell
# 1. Build and launch all services in background
docker compose up --build -d

# 2. Verify running containers
docker compose ps

# 3. View live application logs
docker compose logs -f app

# 4. Run traffic simulation in a separate terminal
python scripts/simulate_traffic.py
```

### Access URLs:
- **Application API**: `http://localhost:8000`
- **Application Metrics**: `http://localhost:8000/metrics`
- **Prometheus UI**: `http://localhost:9090` (Check Targets at `http://localhost:9090/targets`)
- **Grafana Dashboard**: `http://localhost:3000` (Login: `admin` / `admin`, Navigate to Dashboards -> CloudOps Platform)

To tear down:
```powershell
docker compose down -v
```

---

## 3. Cloud Deployment (AWS & Terraform)

### Step 1: AWS Credentials & CLI Check
Ensure AWS CLI is configured with your deployment account:
```powershell
aws sts get-caller-identity
```

### Step 2: Provision Remote State Backend (Optional/Recommended)
```powershell
cd terraform/bootstrap
terraform init
terraform apply -auto-approve
cd ../..
```

### Step 3: Provision Dev Infrastructure
```powershell
cd terraform/environments/dev
terraform init
terraform plan
terraform apply
```

### Step 4: Verification
After `terraform apply` finishes, inspect the output variables:
- `application_url`: Direct HTTP URL of your server.
- `ssm_connect_command`: Command to open a secure shell session on the EC2 host.

Run the verification script against your cloud instance:
```powershell
python scripts/health_check.py http://<YOUR_EC2_PUBLIC_IP>:8000
```

---

## 4. Teardown & Cost Cleanup (Budget Guardrail)

To avoid incurring AWS bills after testing:
```powershell
cd terraform/environments/dev
terraform destroy -auto-approve
```
Verify that all EC2 instances, ECR repositories, and VPC resources have been terminated in the AWS console.
