Filters API
===========

This page documents custom Jinja2 filters provided by Kolla-Ansible.

Available filters
-----------------

The `filters` module provides Jinja2 filters used by templates.

- `service_enabled(context, service)`
  - Return whether a service is enabled (evaluates boolean/templated values).
- `extract_haproxy_services(context, services)`
  - Return a dictionary of haproxy service configuration (raises on duplicates).
- `service_mapped_to_host(context, service)`
  - Return whether a service is mapped to the current host (by group or expression).
- `service_enabled_and_mapped_to_host(context, service)`
  - Combine `service_enabled` and `service_mapped_to_host`.
- `select_services_enabled_and_mapped_to_host(context, services)`
  - Select services filtered by enabled & mapped criteria.

Usage example
-------------

.. code-block:: jinja

   {% for name, svc in services | select_services_enabled_and_mapped_to_host %}
     {{ name }}
   {% endfor %}

Implementation notes
--------------------
- Filters live in `kolla_ansible/filters.py` and are registered via `get_filters()`.
- Add unit tests for filter edge cases (undefined attributes, invalid types) in `tests/`.

