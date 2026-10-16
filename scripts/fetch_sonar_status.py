#!/usr/bin/env python3
"""Wait for the SonarQube analysis task and save its quality gate status as JSON."""
import base64
import json
import os
import sys
import time
import urllib.request

REPORT_TASK = ".scannerwork/report-task.txt"
OUTPUT = "reports/sonar-gate.json"
TIMEOUT_SECONDS = 180


def read_properties(path):
    props = {}
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            key, sep, value = line.strip().partition("=")
            if sep:
                props[key] = value
    return props


def get_json(url, token):
    credentials = base64.b64encode(f"{token}:".encode()).decode()
    request = urllib.request.Request(url, headers={"Authorization": f"Basic {credentials}"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def main():
    token = os.environ["SONAR_TOKEN"]
    props = read_properties(REPORT_TASK)
    deadline = time.time() + TIMEOUT_SECONDS
    while True:
        task = get_json(props["ceTaskUrl"], token)["task"]
        if task["status"] == "SUCCESS":
            break
        if task["status"] in ("FAILED", "CANCELED") or time.time() > deadline:
            print(f"SonarQube analysis task ended with status {task['status']}")
            return 1
        time.sleep(3)

    gate_url = f"{props['serverUrl']}/api/qualitygates/project_status?analysisId={task['analysisId']}"
    status = get_json(gate_url, token)
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as handle:
        json.dump(status, handle, indent=2)
    print(f"SonarQube quality gate: {status['projectStatus']['status']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
