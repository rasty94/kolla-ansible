Healthcheck failures
====================

Symptoms
--------
- Services reported as unhealthy by healthchecks

Troubleshooting steps
---------------------
1. Check container logs for process crashes or errors.
2. Verify healthcheck commands (`curl`, `port check`) and endpoints inside container.
3. Confirm service configuration files were rendered correctly.
4. Increase healthcheck retries/timeouts during debugging if appropriate.

Recovery examples
-----------------
- Redeploy the service after fixing the underlying issue or adjust healthcheck logic temporarily.
