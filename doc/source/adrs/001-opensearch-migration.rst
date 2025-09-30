ADR 001: Migration from ELK Stack to OpenSearch
===============================================

Date: 2025-09-30

Status: Accepted

Context
-------
The ELK stack (Elasticsearch, Logstash, Kibana) has reached end-of-life for many components.
OpenSearch provides a viable, open-source alternative with better licensing and community support.
Kolla-Ansible needs to migrate to maintain security and functionality.

Decision
--------
Migrate from ELK to OpenSearch stack, including:
- Replace Elasticsearch with OpenSearch
- Replace Kibana with OpenSearch Dashboards
- Update all configuration variables and documentation
- Maintain backward compatibility where possible

Consequences
------------
Positive:
- Improved security with regular updates
- Better community support
- Compatible API for most use cases

Negative:
- Migration effort required for existing deployments
- Some plugins may need replacement

Implementation
--------------
- Update Ansible roles to deploy OpenSearch instead of Elasticsearch
- Modify configuration variables (e.g., opensearch_* instead of elasticsearch_*)
- Update documentation and examples
- Provide migration guides for users