# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.0] - 2025-01-10

### Fixed

- **Ansible Deprecation Warnings**: Replaced deprecated `with_` loop syntax with modern `loop` syntax
  - Updated `with_items` to `loop` in multiple playbooks
  - Updated `with_inventory_hostnames` to `loop` with `groups['all']`
  - Updated `with_dict` to `loop` with `dict2items` filter
  - Fixed `.yamllint` configuration for ansible-lint compatibility

### Changed

- **Code Quality**: Improved Ansible playbook maintainability and future compatibility

## [0.4.0] - 2025-09-30

### Added

- **Architecture Decision Records (ADRs)**:
  - ADR 001: Migration from ELK Stack to OpenSearch
  - ADR 002: Enhanced Password Generation Security
- **Interactive Troubleshooting Runbook**:
  - Step-by-step guides for common deployment issues
  - Performance troubleshooting procedures
  - Database recovery procedures
- **Production Readiness Guides**:
  - Capacity planning guide with resource estimation formulas
  - Security hardening checklist with pre/post-deployment tasks
  - Operational runbooks for daily, weekly, and monthly maintenance
  - Emergency procedures for service failures and disaster recovery

### Documentation

- Expanded documentation structure with new sections for ADRs and production guides
- Added interactive elements to troubleshooting guides

## [0.3.0] - 2025-09-30

### Changed

- Removed unused `timezone` import from `tools/generate_passwords.py` after JWT functionality removal.

### Fixed

- Ensured all documentation variables match Ansible playbook variables for OpenSearch migration.

## [0.2.0] - 2025-09-30

### Changed

- Updated documentation in `doc/source/` to replace Elasticsearch references with OpenSearch:
  - `central-logging-guide.rst`: Changed retention variables and log forwarding references.
  - `grafana-guide.rst`: Updated data source examples.
  - `cloudkitty-guide.rst`: Modified backend configuration examples.
  - `advanced-configuration.rst`: Updated external logging environment section.
  - `adding-a-new-service.rst`: Changed service logging instructions.
  - `multinode.rst`: Updated Ansible inventory groups.
  - `osprofiler-guide.rst`: Modified enable flags and connection strings.
  - `troubleshooting.rst`: Updated user interface access instructions.
- Marked OpenSearch migration tasks as completed in `TODO.md`.

### Added

- Added `venv/` to `.gitignore` for virtual environment exclusion.

## [0.1.0] - 2025-09-30

### Added

- Enhanced password generation in `tools/generate_passwords.py`:
  - Switched from `random.SystemRandom()` to `secrets` module for cryptographically secure random generation.
  - Implemented guaranteed complexity: minimum 1 uppercase, 1 lowercase, 1 digit, 1 symbol from `+-.*`.
  - Added configurable CLI arguments: `--password-length`, `--include-symbols`, etc.
  - Set default password length to 40 characters with required complexity.
- Added PyJWT to `requirements.txt` (later removed as JWT functionality was not implemented).
- Created virtual environment setup with all dependencies installed.

### Changed

- Modified password generation algorithm to ensure minimum character requirements are met.
- Updated default password policies to enforce stronger security.

### Removed

- Eliminated JWT token generation functionality from `tools/generate_passwords.py` due to complexity concerns.
- Removed PyJWT dependency from `requirements.txt`.

### Fixed

- Corrected deprecation warnings in password generation by using proper random shuffling.
