Capacity Planning Guide
======================

This guide helps operators plan resource requirements for Kolla-Ansible deployments.

Resource Estimation
-------------------

Control Plane Requirements
^^^^^^^^^^^^^^^^^^^^^^^^^^

**Minimum Requirements (All-in-One):**
- CPU: 4 cores
- RAM: 16 GB
- Storage: 100 GB SSD
- Network: 1 Gbps

**Production Control Node:**
- CPU: 8+ cores
- RAM: 32-64 GB
- Storage: 500 GB SSD
- Network: 10 Gbps

Compute Node Requirements
^^^^^^^^^^^^^^^^^^^^^^^^^

**Per Compute Node:**
- CPU: 8-16 cores per node
- RAM: 64-128 GB per node
- Storage: 1-2 TB SSD per node
- Network: 10-25 Gbps

**Scaling Formula:**
- VMs per core: 4-8 (depending on workload)
- RAM per VM: 2-4 GB base + application requirements

Storage Planning
----------------

Database Storage
^^^^^^^^^^^^^^^^

**MariaDB:**
- Data volume: 100-500 GB initial
- Growth rate: 10-20% monthly
- Backup storage: 2x data volume

**OpenSearch:**
- Data volume: 200-1000 GB initial
- Retention: 30-90 days logs
- Growth rate: 5-15% monthly

Network Planning
----------------

Bandwidth Requirements
^^^^^^^^^^^^^^^^^^^^^^

**Internal Network:**
- Control plane: 1-10 Gbps
- Storage: 10-40 Gbps
- Tenant networks: 10-100 Gbps (depending on VM density)

**External Network:**
- Internet access: 1-10 Gbps
- API access: 100 Mbps - 1 Gbps

High Availability Considerations
--------------------------------

**Minimum HA Setup:**
- 3 control nodes
- 2 compute nodes minimum
- Shared storage for databases
- Load balancers for API endpoints

**Resource Overhead for HA:**
- +50% CPU for redundancy
- +30% RAM for failover capacity
- +100% storage for backups

Monitoring and Alerting
-----------------------

**Recommended Monitoring Stack:**
- Prometheus: 4 GB RAM, 100 GB storage
- Grafana: 2 GB RAM, 50 GB storage
- Alertmanager: 1 GB RAM, 20 GB storage

**Alert Thresholds:**
- CPU > 80% sustained
- RAM > 85% sustained
- Storage > 90% used
- Network saturation > 70%