Template rendering errors
=========================

Symptoms
--------
- Jinja2 template render errors during playbook runs

Troubleshooting steps
---------------------
1. Inspect template and variable usage for undefined variables.
2. Run `ansible-playbook ... -vvv` and look for the template traceback.
3. Check for recent changes in defaults that may have introduced incompatible structures.
4. Validate Jinja2 expressions with a small script or unit test.

Recovery examples
-----------------
- Add missing variables, default values, or defensive checks in templates and re-run.
