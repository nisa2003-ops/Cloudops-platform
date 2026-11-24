# CloudOps Operational Troubleshooting Guide

This guide outlines diagnostic procedures for Site Reliability Engineers (SREs) and DevOps engineers responding to platform anomalies.

---

## 1. Diagnosing a Failed Health Check (`/health` or `/ready`)

### Symptom:
`GET /health` or `GET /ready` returns non-200 (e.g. 503 Service Unavailable or timeout).

### Diagnostic Steps:
1. **Check Container Status**:
   ```bash
   docker ps -a --filter "name=cloudops"
   ```
   If container is exited or restarting continuously, inspect exit codes (e.g., Code 137 indicates Out of Memory / OOMKilled).

2. **Inspect Structured Application Logs**:
   ```bash
   docker logs --tail 100 cloudops-app
   ```
   Filter for JSON log level `ERROR` or unhandled exceptions.

3. **Verify Process Internals via Shell**:
   ```bash
   docker exec -it cloudops-app python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/ready').read().decode())"
   ```

---

## 2. Investigating High HTTP 5xx Error Rates

### Symptom:
Prometheus alert `HighHttpErrorRate` triggers in Grafana or Alertmanager.

### Diagnostic Steps:
1. **Query Prometheus Expression**:
   In Prometheus UI (`http://localhost:9090`):
   ```promql
   sum(rate(http_requests_total{status_code=~"5.."}[5m])) by (endpoint, status_code)
   ```
   This immediately identifies which specific endpoints are generating 5xx errors.

2. **Correlate with Chaos Testing Endpoints**:
   Check if `/chaos/error` was invoked or if an external dependency timeout caused failures.

---

## 3. Investigating Latency Degradation (SLO Breach)

### Symptom:
`HighRequestLatencyP95` alert firing; users experiencing slow responses.

### Diagnostic Steps:
1. **Identify Percentile Latencies**:
   In Prometheus UI:
   ```promql
   histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, endpoint))
   ```
   Check which endpoint breaches the 500ms threshold.

2. **Check Host CPU / Memory Starvation**:
   On EC2 host:
   ```bash
   top
   free -m
   docker stats --no-stream
   ```

---

## 4. Recovering from a Failed Cloud Deployment

### Scenario:
A new commit was deployed to EC2, but fails the post-deployment health check.

### Rollback Procedure:
1. Run rollback command via AWS SSM:
   ```bash
   # Stop failed container
   docker stop cloudops-app
   docker rm cloudops-app
   # Run previous known-good tag
   docker run -d --name cloudops-app --restart unless-stopped -p 8000:8000 <ECR_REGISTRY>/cloudops-dev-app:<PREVIOUS_KNOWN_GOOD_SHA>
   ```
2. Verify restoration:
   ```bash
   curl -f http://localhost:8000/health
   ```
