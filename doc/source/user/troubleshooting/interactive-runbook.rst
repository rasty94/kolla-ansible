Interactive Troubleshooting Runbook
===================================


This runbook provides step-by-step interactive troubleshooting guides for common Kolla-Ansible issues.

Common Deployment Issues
------------------------

Issue: Services fail to start after deployment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Symptoms:**
- Services show as failed in systemctl/docker
- Logs show connection errors

**Interactive Steps:**

1. Check service logs::

    docker logs <container_name>

2. Verify network connectivity::

    docker exec -it <container_name> ping <database_host>

3. Check configuration files::

    docker exec -it <container_name> cat /etc/<service>/<service>.conf

4. Validate passwords::

    grep <service>_database_password /etc/kolla/passwords.yml

**If issue persists:**
- Check firewall rules
- Verify DNS resolution
- Review Ansible deployment logs

Issue: OpenSearch/Kibana not accessible
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Symptoms:**
- Cannot access dashboards via web interface
- Connection refused errors

**Interactive Steps:**

1. Check if services are running::

    docker ps | grep opensearch

2. Verify port bindings::

    docker port opensearch-dashboards

3. Check logs::

    docker logs opensearch-dashboards

4. Test connectivity::

    curl -I http://localhost:5601

**Common solutions:**
- Check firewall settings
- Verify VIP configuration
- Review TLS certificates

Performance Issues
------------------

Issue: High CPU usage on control nodes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Symptoms:**
- System load > 5.0
- Slow response times

**Interactive Steps:**

1. Identify top processes::

    top -c

2. Check Docker container usage::

    docker stats

3. Review OpenSearch cluster health::

    curl -X GET "localhost:9200/_cluster/health?pretty"

4. Analyze network traffic::

    nload

**Optimization steps:**
- Increase node resources
- Tune JVM settings for OpenSearch
- Implement resource limits

Database Issues
---------------

Issue: MariaDB Galera cluster split-brain
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Symptoms:**
- Database connections fail
- Inconsistent data across nodes

**Interactive Steps:**

1. Check cluster status::

    docker exec -it mariadb mysql -u root -p -e "SHOW STATUS LIKE 'wsrep_cluster_status';"

2. Verify node connectivity::

    docker exec -it mariadb mysql -u root -p -e "SHOW STATUS LIKE 'wsrep_connected';"

3. Review logs::

    docker logs mariadb

**Recovery steps:**
- Bootstrap cluster from healthy node
- Check network partitioning
- Validate configuration consistency