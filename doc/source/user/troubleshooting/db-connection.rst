Database connection failures
============================

Symptoms
--------
- Playbooks fail on database tasks
- Services cannot connect to MariaDB/ProxySQL

Troubleshooting steps
---------------------
1. Verify `database_address`, `database_user`, and `database_password` in `globals.yml`.
2. Check network connectivity to the DB host (`telnet <host> <port>` / `nc -vz`).
3. Ensure the database user has required privileges.
4. Inspect MariaDB logs for connection errors.

Recovery examples
-----------------
- Fix credentials and re-run `kolla-ansible -v deploy` for the affected role.
