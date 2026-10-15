# Demo runbook

Run the whole demo end to end at least three times before the presentation.
URLs: Jenkins `http://localhost:8082`, SonarQube `http://localhost:9000`, app `http://localhost:8081`.

## Before the demo

1. Start the stack from `infra/`: `docker compose up -d`, then confirm both containers are running with `docker ps`.
2. Confirm the NVD key reached Jenkins (prints only its length, it should be 36):
   `docker exec jenkins sh -c 'echo "length=${#NVD_API_KEY}"'`
3. Make sure the Dependency-Check database is already downloaded. Run one full build the day before.
   Do not demo on a cold database: the first download takes well over an hour.
4. Sign in to Jenkins and SonarQube in the browser, and open the job page.
5. Confirm that the `sonar-token` credential exists in Jenkins.
6. Keep screenshots of a passing run, a blocked run and a remediated run as a backup.

## Scenario A: clean build

1. Check out `main`, which contains the clean `requirements.txt`.
2. Click **Build Now** (or push a trivial change and wait for the one-minute poll).
3. Show every stage going green, then open `http://localhost:8081` and `/health`.
4. Expected end of the log: `SECURITY GATE: PASSED`, then the smoke test passes.

## Scenario B: vulnerable dependency is blocked

1. On a branch, change `requirements.txt` to pin the vulnerable versions chosen by the team
   (see "Dependency pair" below), commit and push.
2. Jenkins builds automatically. Open the run and show:
   - the Dependency-Check HTML report listing the vulnerable package and its CVE,
   - the console ending in `SECURITY GATE: FAILED - deployment blocked`.
3. Show that Deploy and Smoke Test were skipped and that the previous container is still serving.

## Scenario C: remediation

1. Change `requirements.txt` back to the fixed versions, commit and push.
2. Show the build going green end to end, the gate passing and the new container serving.
3. Conclude with the build history: pass, blocked, pass.

## Dependency pair

The vulnerable and fixed versions must be chosen and tested before the demo. They are only valid
once Dependency-Check has actually flagged them in this pipeline. Record the pair here after it
has been verified:

| | Version pins | Result |
|---|---|---|
| Vulnerable | _to fill after verification_ | _gate fails_ |
| Fixed | _to fill after verification_ | _gate passes_ |

## If something goes wrong

| Symptom | Likely cause | Fix |
|---|---|---|
| Dependency-Check stage fails with `Invalid API Key` | `NVD_API_KEY` is empty in the Jenkins container | Put the key in `infra/.env`, run `docker compose up -d` in `infra/`, then check the length again |
| Jenkins page shows the sign-in form after a restart | Restarting the container ends the session | Sign in again; jobs and credentials are kept in the volume |
| Sonar stage fails with a missing `report-task.txt` | Scanner wrote its report outside the workspace | The `Jenkinsfile` passes the working directory and metadata path explicitly; check it was not edited |
| Smoke test fails | Port 8081 is taken by something else | Stop the other process or free the port, then rebuild |
| Build stuck waiting | Another build is running (one at a time) | Wait for it, or abort it from the build page |
