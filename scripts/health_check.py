"""Automated post-deployment verification script for CloudOps API."""

import sys
import time
import urllib.request
import json

DEFAULT_HOST = "http://localhost:8000"


def check_endpoint(base_url: str, path: str, expected_code: int = 200) -> bool:
    url = f"{base_url}{path}"
    start = time.perf_counter()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "CloudOps-HealthCheck/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            latency = (time.perf_counter() - start) * 1000
            if response.status == expected_code:
                data = json.loads(response.read().decode())
                print(f"[PASS] {path} returned {response.status} in {latency:.2f}ms. Body: {data}")
                return True
            else:
                print(f"[FAIL] {path} returned unexpected status: {response.status}")
                return False
    except Exception as exc:
        print(f"[FAIL] {path} request failed: {exc}")
        return False


def main():
    target_host = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HOST
    print(f"Executing CloudOps Health Verification on target: {target_host}")

    endpoints_to_test = ["/", "/health", "/ready"]
    all_passed = True

    for ep in endpoints_to_test:
        if not check_endpoint(target_host, ep):
            all_passed = False

    if not all_passed:
        print("\nDeployment verification FAILED.")
        sys.exit(1)

    print("\nAll health probes PASSED successfully.")
    sys.exit(0)


if __name__ == "__main__":
    main()