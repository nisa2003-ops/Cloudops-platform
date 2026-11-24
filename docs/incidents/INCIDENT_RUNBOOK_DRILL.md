# Incident Simulation & Post-Incident Review (PIR) Drill

## 1. Drill Overview

This runbook documents a controlled Chaos Engineering and Incident Recovery simulation conducted on the CloudOps platform to test alert responsiveness and SRE procedures.

---

## 2. Simulation Steps (Hands-on Drill)

### Scenario A: Service Readiness Outage
1. **Trigger Outage**:
   Send a request to disable service readiness:
   ```powershell
   curl -X POST http://localhost:8000/chaos/toggle-readiness -H "Content-Type: application/json" -d '{"ready": false}'
   ```
2. **Verify Alert & Symptoms**:
   - Hit `http://localhost:8000/ready` -> Receives `HTTP 503 Service Unavailable`.
   - In Grafana, the readiness and status code breakdown graphs show immediate 503 spikes.
3. **Execute Recovery**:
   ```powershell
   curl -X POST http://localhost:8000/chaos/toggle-readiness -H "Content-Type: application/json" -d '{"ready": true}'
   ```
   - Hit `http://localhost:8000/ready` -> Receives `HTTP 200 OK`.

---

### Scenario B: High Error Rate & Alert Triggering
1. **Trigger Error Wave**:
   Generate bursts of HTTP 500 errors:
   ```powershell
   for ($i=1; $i -le 50; $i++) { curl http://localhost:8000/chaos/error | Out-Null }
   ```
2. **Observe Prometheus Alert**:
   - Navigate to `http://localhost:9090/alerts`.
   - Alert `HighHttpErrorRate` transitions from `Inactive` -> `Pending` -> `Firing`.
3. **Verify Grafana Dashboard**:
   - `5xx Error Percentage` panel spikes past the 5% threshold.
4. **Resolution**:
   Traffic simulator returns to normal 200 endpoints (`/`, `/health`). The alert clears automatically once the error rate falls below 5%.

---

## 3. Incident Post-Mortem Report (Interview Template)

| Field | Detail |
|---|---|
| **Incident ID** | INC-2026-001 |
| **Severity** | SEV-2 (High Error Rate & Readiness Degradation) |
| **Time to Detect (TTD)** | 30 seconds (Prometheus evaluation interval) |
| **Time to Mitigate (TTM)** | 1 minute 15 seconds |
| **Root Cause** | Deliberate chaos injection on readiness and 500 endpoints to validate SLO alerting. |
| **Corrective Action** | Alert rules verified sensitive and accurate. Automated rollback pipeline confirmed operational. |
