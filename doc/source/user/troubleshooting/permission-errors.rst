Permission errors
=================

Symptoms
--------
- Files or sockets owned by wrong user, services failing to start due to permission denied

Troubleshooting steps
---------------------
1. Check file ownership and permissions in `/etc/kolla` and container volumes.
2. Ensure `CONFIG_OWNER_USER` / `CONFIG_OWNER_GROUP` are set as expected.
3. Validate that generated files are created with correct modes (e.g., `0600` for certs).
4. Inspect container startup logs for permission denied errors.

Recovery examples
-----------------
- Fix ownership (`chown`) and modes (`chmod`), re-run relevant tasks or re-deploy the container.
