Debugging Guide
================

Tips for debugging Kolla-Ansible code:

- Use `-vvv` with `ansible-playbook` for detailed logs
- Use `kolla-ansible debug` (TBD) to collect environment information
- For Python code, run individual modules with pytest and pdb

Add debugging recipes for common failure modes.