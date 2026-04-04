Image pull failures
===================

Symptoms
--------
- Containers fail to start due to image pull errors

Troubleshooting steps
---------------------
1. Verify registry address and credentials in `globals.yml`.
2. Try pulling the image manually on host: `docker pull <image>` or `podman pull <image>`.
3. Check network/DNS and firewall rules that may block registry access.
4. Validate image tag and existence in registry.

Recovery examples
-----------------
- Fix registry credentials or image tags and retry the operation.
