"""Simulate continuous web traffic and chaos events for Prometheus & Grafana testing."""

import random
import time
import urllib.request
import urllib.error

BASE_URL = "http://localhost:8000"


def send_request(path: str) -> None:
    url = f"{BASE_URL}{path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "CloudOps-TrafficSimulator/1.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            print(f"[OK] {path} -> {resp.status}")
    except urllib.error.HTTPError as err:
        print(f"[WARN] {path} -> HTTP {err.code}")
    except Exception as exc:
        print(f"[FAIL] {path} -> {exc}")


def main():
    print("Starting CloudOps Traffic Generator... (Press Ctrl+C to stop)")
    endpoints = ["/", "/health", "/ready"]

    while True:
        # Normal traffic (85% probability)
        if random.random() < 0.85:
            target = random.choice(endpoints)
            send_request(target)
        else:
            # 15% error or 404 simulation to test error rate metrics & alerts
            target = random.choice(["/chaos/error", "/unknown-route"])
            send_request(target)

        time.sleep(random.uniform(0.1, 0.5))


if __name__ == "__main__":
    main()