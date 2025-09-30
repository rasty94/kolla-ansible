ADR 002: Enhanced Password Generation Security
==============================================

Date: 2025-09-30

Status: Accepted

Context
-------
Default password generation in Kolla-Ansible used basic random generation.
Security requirements demand stronger passwords with guaranteed complexity.
The secrets module provides cryptographically secure random generation.

Decision
--------
Implement enhanced password generation with:
- Use Python's secrets module for secure randomness
- Guarantee minimum complexity (uppercase, lowercase, digits, symbols)
- Configurable policies via CLI arguments
- Default 40-character passwords with required complexity

Consequences
------------
Positive:
- Significantly improved password security
- Meets modern security standards
- Backward compatible with existing deployments

Negative:
- Slight performance impact (minimal)
- CLI complexity increased

Implementation
--------------
- Modify tools/generate_passwords.py to use secrets module
- Add complexity validation and minimum requirements
- Update default password length and policies
- Add CLI arguments for customization