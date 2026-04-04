Role Default Variable Documentation Template
=============================================

Use this template to document variables in `defaults/main.yml` for roles.

Example entry
-------------

# Port for Nova API service
# Type: integer
# Default: 8774
# Notes: Port used by nova-api for public API; can be overridden by HAProxy external port.
nova_api_port: 8774

Guidelines
----------
- Provide a short description of the variable.
- State the type (string, integer, boolean, list, dict).
- Provide the default value and an example if applicable.
- Mention related variables and any constraints (e.g., acceptable ranges).
- If sensitive, note security considerations (e.g., secrets should not be checked into repos).

Automation
----------
Consider adding `meta/argument_specs.yml` alongside `defaults/main.yml` to enable Ansible to validate input types automatically.
