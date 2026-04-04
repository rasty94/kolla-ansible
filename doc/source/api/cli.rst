CLI Reference
=============

This page documents `kolla-ansible` CLI commands and their intended usage.

Commands
--------

Kolla-Ansible exposes a Cliff-based CLI under `kolla_ansible`.

.. py:class:: KollaAnsibleApp

   A Cliff App that registers commands under `kolla_ansible.cli`.

Public entrypoints
~~~~~~~~~~~~~~~~~~

- `kolla-ansible` main application (see `kolla_ansible/cmd/kolla_ansible.py`)
  - `main(argv=...)` - CLI entry point. Creates and runs `KollaAnsibleApp`.

Common subcommands (examples)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- `setup-wizard` - Interactive setup assistant (see `kolla_ansible/cli/commands.py`).
- `validate-setup` - Validate configuration and prerequisites.
- `dev-setup` - Developer environment bootstrap (TBD).

Notes
~~~~~
- Add examples showing input/output, exit codes, and common failure cases. Link to tests that cover behavior.

