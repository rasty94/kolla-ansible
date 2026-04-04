Vault authentication failures
=============================

Symptoms
--------
- Tasks interacting with Vault fail with authentication errors

Troubleshooting steps
---------------------
1. Check Vault server availability and address in configuration.
2. Verify Vault token validity or AppRole credentials.
3. Check Vault audit logs for denied requests.
4. Ensure `kolla_ansible/hashi_vault.py` configuration matches Vault server settings.

Recovery examples
-----------------
- Renew or rotate Vault token and re-run the playbook.
