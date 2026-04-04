Data Flow
=========

High-level deployment data flow example:

1. `kolla-ansible` CLI validates globals and inventory
2. Playbooks render templates and push configuration to containers
3. Services register endpoints in Keystone
4. Healthchecks and monitoring collect metrics and logs

Add sequence diagrams and workflows here as they are produced.
