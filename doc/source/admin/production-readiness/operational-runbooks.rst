Operational Runbooks
===================

Standard Operating Procedures for Kolla-Ansible Management

Daily Operations
----------------

System Health Checks
^^^^^^^^^^^^^^^^^^^^

**Morning Health Check:**

1. Verify all services are running::

    kolla-ansible -i inventory/multinode services

2. Check cluster status::

    docker exec -it opensearch curl -X GET "localhost:9200/_cluster/health?pretty"

3. Monitor resource usage::

    docker stats --no-stream

4. Review overnight logs::

    find /var/log/kolla -name "*.log" -mtime -1 -exec tail -50 {} \;

**Automated Monitoring:**
- Prometheus alerts
- System load averages
- Disk space usage
- Network connectivity

Backup Procedures
^^^^^^^^^^^^^^^^^

**Database Backup:**

1. Create backup directory::

    mkdir -p /backup/$(date +%Y%m%d)

2. Backup MariaDB::

    kolla-ansible -i inventory/multinode mariadb_backup

3. Backup configurations::

    cp -r /etc/kolla /backup/$(date +%Y%m%d)/

4. Verify backup integrity::

    ls -la /backup/$(date +%Y%m%d)/

**OpenSearch Backup:**

1. Create snapshot repository::

    curl -X PUT "localhost:9200/_snapshot/backup_repo" -H 'Content-Type: application/json' -d'
    {
      "type": "fs",
      "settings": {
        "location": "/backup/opensearch"
      }
    }'

2. Create snapshot::

    curl -X PUT "localhost:9200/_snapshot/backup_repo/snapshot_$(date +%Y%m%d)?wait_for_completion=true"

Weekly Maintenance
------------------

System Updates
^^^^^^^^^^^^^^

1. Check for available updates::

    apt update && apt list --upgradable

2. Schedule maintenance window::

    echo "Maintenance scheduled for $(date -d 'next Sunday' +%Y-%m-%d)"

3. Update control nodes::

    kolla-ansible -i inventory/multinode prechecks
    kolla-ansible -i inventory/multinode upgrade

4. Update compute nodes::

    kolla-ansible -i inventory/multinode prechecks
    kolla-ansible -i inventory/multinode upgrade

Log Rotation
^^^^^^^^^^^^

1. Check current log sizes::

    du -sh /var/log/kolla/*

2. Rotate OpenSearch indices::

    curl -X POST "localhost:9200/_opendistro/_ism/policies/log_retention_policy/_rollover"

3. Clean old logs::

    find /var/log/kolla -name "*.log.*" -mtime +30 -delete

Monthly Procedures
------------------

Capacity Planning Review
^^^^^^^^^^^^^^^^^^^^^^^^

1. Analyze resource usage trends::

    # Check Prometheus metrics for the last month
    promql: avg_over_time(cpu_usage[30d])

2. Review scaling requirements::

    # Check VM density and performance
    openstack hypervisor stats show

3. Plan capacity upgrades::

    # Document recommendations for next quarter

Security Audits
^^^^^^^^^^^^^^^

1. Run vulnerability scans::

    # Use OpenSCAP or similar tools
    oscap oval eval --results scan-results.xml /usr/share/xml/scap/ssg/content/ssg-rhel8-oval.xml

2. Review access logs::

    # Check for suspicious activity
    grep "FAILED" /var/log/kolla/keystone/keystone.log

3. Update security policies::

    # Review and update firewall rules, password policies, etc.

Emergency Procedures
--------------------

Service Failure Response
^^^^^^^^^^^^^^^^^^^^^^^^

**Immediate Actions:**

1. Identify failed service::

    kolla-ansible -i inventory/multinode services | grep failed

2. Check service logs::

    docker logs <failed_container>

3. Attempt restart::

    docker restart <failed_container>

4. If restart fails, check dependencies::

    # Check database connectivity, network, etc.

**Escalation:**
- Notify on-call engineer
- Create incident ticket
- Communicate with stakeholders

Node Failure Recovery
^^^^^^^^^^^^^^^^^^^^^

**Control Node Failure:**

1. Assess damage::

    # Check if node is recoverable
    ping <failed_node>

2. If recoverable::

    kolla-ansible -i inventory/multinode prechecks
    kolla-ansible -i inventory/multinode deploy

3. If not recoverable::

    # Remove from inventory
    # Provision replacement node
    # Rejoin cluster

**Compute Node Failure:**

1. Migrate instances::

    openstack server migrate <instance> --live <target_host>

2. Remove failed node::

    openstack compute service delete <service_id>

3. Provision replacement::

    kolla-ansible -i inventory/multinode deploy

Disaster Recovery
^^^^^^^^^^^^^^^^^

**Complete System Recovery:**

1. Assess backup integrity::

    # Verify recent backups exist and are uncorrupted

2. Prepare recovery environment::

    # Provision new infrastructure if needed

3. Restore databases::

    kolla-ansible -i inventory/multinode mariadb_recovery

4. Restore configurations::

    cp -r /backup/latest/kolla /etc/

5. Redeploy services::

    kolla-ansible -i inventory/multinode deploy

6. Validate system functionality::

    # Run comprehensive tests
    kolla-ansible -i inventory/multinode post-deploy