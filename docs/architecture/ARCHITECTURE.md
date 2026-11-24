# CloudOps Architecture & Technical Design

## 1. High-Level System Architecture

CloudOps is designed around four key pillars:
1. **Containerized Microservice Application**: FastAPI Python 3.11 service.
2. **Infrastructure-as-Code (IaC)**: Modular Terraform managing AWS networking, security, IAM, and compute.
3. **Automated CI/CD**: Zero-secret GitHub Actions pipeline using AWS OIDC federation.
4. **Site Reliability Engineering (SRE) & Observability**: Prometheus metrics collection, alerting rules, and Grafana telemetry dashboards.

```
                           +------------------------+
                           |  GitHub Actions CI/CD  |
                           +-----------+------------+
                                       |
                   OIDC Federated Auth | (No static AWS keys)
                                       v
                                 +-----------+
                                 | AWS IAM   |
                                 +-----+-----+
                                       |
                   Push Image Tag      v
                 +-----------------> [ Amazon ECR ]
                 |                     |
                 |                     | Pull by Commit SHA
                 |                     v
+----------------+-------------------------------------------------+
| AWS VPC (10.0.0.0/16)                                            |
|                                                                  |
|   +------------------------------------------------------------+ |
|   | Public Subnet (10.0.1.0/24)                                | |
|   |                                                            | |
|   |   +------------------------------------------------------+ | |
|   |   | EC2 Host (Amazon Linux 2023)                         | | |
|   |   |                                                      | | |
|   |   |   Security Group: Ingress Port 8000 only             | | |
|   |   |   IAM Role: SSM Managed Core + ECR ReadOnly          | | |
|   |   |                                                      | | |
|   |   |   +------------------------------------------------+ | | |
|   |   |   | Docker Container: cloudops-app:sha            | | | |
|   |   |   |   - /          (App Info)                      | | | |
|   |   |   |   - /health    (Liveness Probe)                | | | |
|   |   |   |   - /ready     (Readiness Probe)               | | | |
|   |   |   |   - /metrics   (Prometheus Scrape Endpoint)    | | | |
|   |   |   +------------------------------------------------+ | | |
|   |   +------------------------------------------------------+ | |
|   +------------------------------------------------------------+ |
|                                                                  |
|   Internet Gateway <==== Internet Traffic on Port 8000           |
+------------------------------------------------------------------+
```

---

## 2. Component Breakdown

### 2.1 Compute & Networking
- **VPC & Subnet**: Single VPC (`10.0.0.0/16`) with an internet-accessible public subnet (`10.0.1.0/24`). To preserve AWS budget, no NAT Gateway is created (saving ~$32/month).
- **Security Group**:
  - Ingress: Port 8000 allowed for HTTP traffic.
  - SSH (Port 22): Explicitly **closed**. Admin access is managed via AWS Systems Manager (SSM) Session Manager.
  - Egress: Unrestricted to allow OS patching and container image pulls.

### 2.2 Identity & Access Management (IAM)
- **Least-Privilege Role**: EC2 instance is granted only `AmazonSSMManagedInstanceCore` and `AmazonEC2ContainerRegistryReadOnly`.
- **Zero-Secret GitHub Actions**: GitHub Actions authenticates via AWS STS `AssumeRoleWithWebIdentity` using OIDC. No AWS access keys are committed or stored in GitHub Secrets.

### 2.3 Application & Metrics Instrumentation
- Built with **FastAPI** and instrumented with `prometheus_client`.
- Implements the **RED Method**:
  - **Rate**: `http_requests_total` counter.
  - **Errors**: `status_code` labels on `http_requests_total`.
  - **Duration**: `http_request_duration_seconds` histogram.
