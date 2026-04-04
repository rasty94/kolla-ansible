Documenting Role Variables
==========================

Use the `doc/templates/role-default-var-template.md` file as the standard for documenting variables included in a role's `defaults/main.yml`.

Recommended workflow
---------------------

1. Add or update the variable in `ansible/roles/<role>/defaults/main.yml`.
2. Add a comment block above the variable using the template format (description, type, default, notes).
3. Add an example `meta/argument_specs.yml` in the role's `meta/` to enable validation.
4. Update role documentation if necessary and open a PR describing the change.

Example
-------

See `ansible/roles/nova/defaults/main.yml` for examples of documented variables.

Automation
----------

Consider adding CI checks that validate comment format or that `meta/argument_specs.yml` is present for prioritized roles.
