# TODO - Kolla-Ansible Core

> **Nota**: Para tareas relacionadas con el portal web Kolla-Control, ver `kolla-control/TODO.md`

Este documento se enfoca en mejoras y tareas pendientes para el core de Kolla-Ansible.

---

## ✅ Tareas Completadas

### Seguridad y Autenticación

- [x] **Gestión de Secretos Mejorada**
  - [x] Migración a `secrets` module en `tools/generate_passwords.py`
  - [x] Políticas de complejidad configurables (40 chars, mayúsculas, números, símbolos)
  - [x] Argumentos CLI para personalización

### Observabilidad

- [x] **Migración a OpenSearch**
  - [x] Actualización de documentación (referencias a Elasticsearch → OpenSearch)
  - [x] Optimización de configuraciones por defecto
  - [x] Implementación de retention policies automáticas

### Documentación

- [x] **Modernización de Documentación**
  - [x] Actualización de ejemplos obsoletos
  - [x] Creación de ADRs (Architecture Decision Records)
  - [x] Runbooks interactivos para troubleshooting
  - [x] Guías de capacity planning
  - [x] Security hardening checklists
  - [x] Operational runbooks (daily/weekly/monthly)

### Calidad de Código

- [x] **Ansible Best Practices**
  - [x] Eliminación de warnings de deprecation
  - [x] Reemplazo de `with_*` loops con sintaxis `loop`

### Usabilidad

- [x] **Mejora de Configuración Inicial**
  - [x] Wizard interactivo (`setup-wizard` command)
  - [x] Validación automática de configuración (`validate-setup` command)

---

## 🎯 Prioridades Inmediatas (Q1 2025)

### Prioridad y Complejidad — Resumen Ejecutivo

**Top tasks (Alta prioridad / Alta complejidad)**

1. Tests para módulos críticos: `kolla_ansible/ansible.py`, `kolla_ansible/cli/commands.py`, `kolla_ansible/utils.py` — **Complejidad: Alta**
2. Migración a Ansible 2.19+ (`requirements-core.yml`) — **Complejidad: Alta**
3. Refactorizar CLI (`SetupWizard.take_action()` y patrón Command/Handler) — **Complejidad: Alta**
4. Resolver regla `no-changed-when` y casos de idempotencia (ansible-lint) — **Complejidad: Alta**
5. Implementar paralelización inteligente del deployment — **Complejidad: Alta**
6. Integración completa con HashiCorp Vault (Secrets Management) — **Complejidad: Alta**
7. Añadir type hints completos en módulos core — **Complejidad: Alta**
8. Enforcement de coverage en CI (`--cov-fail-under`, reportes de cobertura) — **Complejidad: Alta**
9. Soporte para updates parciales / Rolling updates sin downtime — **Complejidad: Alta**
10. Documentación de Arquitectura y API interna (`doc/source/architecture/`) — **Complejidad: Media**

**Organización:** Dentro de cada sección las tareas están ordenadas por complejidad (Alta → Media → Baja).

### Prioridad consolidada (Vista plana)

A. **Alta prioridad / Alta complejidad**
- [ ] Tests críticos: `kolla_ansible/ansible.py`, `kolla_ansible/cli/commands.py`, `kolla_ansible/utils.py`
- [ ] Migración a Ansible 2.19+ (`requirements-core.yml`)
- [ ] Refactorizar CLI (SetupWizard → Collector/Validator/Writer)
- [ ] Resolver `no-changed-when` (idempotencia) y casos críticos de ansible-lint
- [ ] Implementar paralelización inteligente del deployment
- [ ] Integración completa con HashiCorp Vault (Secrets Management)
- [ ] Soporte para updates parciales / Rolling updates sin downtime
- [ ] Enforcement de coverage en CI y reportes de cobertura

B. **Alta prioridad / Media complejidad**
- [ ] Añadir type hints completos en módulos core (empezar por `ansible.py`)
- [ ] Corregir `unnamed-task` y convertir tareas repetitivas en handlers (`no-handler`)
- [ ] Actualizar collections (`community.docker` 5.x) y dependencias críticas
- [ ] Actualizar `cryptography`, `hvac` y resolver CVEs

C. **Media prioridad / Alta complejidad**
- [ ] Integración con Grafana y alertas inteligentes
- [ ] Observability: Logging JSON + Loki, Correlation IDs para tracing
- [ ] Actualizar a OpenStack 2025.1 (plan de compatibilidad y testing)

D. **Media / Baja prioridad**
- [x] Añadir pre-commit hook `pyupgrade` | **Complejidad: Baja**
- [x] Añadir pre-commit hook `isort` | **Complejidad: Baja**
- [ ] Añadir pre-commit hook `mypy` (pendiente configurar `setup.cfg`/`tox.ini`) | **Complejidad: Media**
- [x] Añadir pre-commit hook `check-yaml` | **Complejidad: Baja**
- [x] Crear `tests/conftest.py` y fixtures compartidos para tests | **Complejidad: Baja**
- [x] Documentar `defaults/main.yml` para roles prioritarios | **Complejidad: Media**
- [x] Crear `meta/argument_specs.yml` para roles prioritarios (nova, neutron, keystone, common) | **Complejidad: Media**
- [x] Crear `doc/source/architecture/` y guías para desarrolladores | **Complejidad: Media**

**Nota:** Esta lista es una vista plana para planificación; los items permanecen en sus secciones originales y se irán marcando conforme avance el trabajo.

### 1. Calidad de Código [ALTA PRIORIDAD]

#### 1.1 Ansible Lint Cleanup

**Impacto**: Alto | **Complejidad**: Media

- [ ] **Resolver warnings críticos de ansible-lint** (28 reglas deshabilitadas) | **Complejidad: Media**
  - [ ] `unnamed-task`: Añadir nombres descriptivos a todas las tasks | **Complejidad: Media**
  - [ ] `no-changed-when`: Implementar indicadores de cambio en commands | **Complejidad: Alta**
  - [ ] `no-handler`: Convertir tasks repetitivas en handlers | **Complejidad: Media**
  - [ ] `risky-file-permissions`: Especificar permisos explícitos | **Complejidad: Baja**
  - [ ] `command-instead-of-module`: Usar módulos nativos donde sea posible | **Complejidad: Media**

**Archivos afectados**: `.ansible-lint`, `ansible/roles/*/tasks/*.yml`

#### 1.2 Python Code Modernization

**Impacto**: Alto | **Complejidad**: Media

- [ ] **Añadir type hints completos** | **Complejidad: Alta**

  - [ ] `kolla_ansible/ansible.py` | **Complejidad: Alta**
  - [ ] `kolla_ansible/utils.py` | **Complejidad: Media**
  - [ ] `kolla_ansible/cmd/*.py` | **Complejidad: Alta**
  - [ ] `tools/*.py` | **Complejidad: Media**

- [ ] **Refactorizar CLI commands** | **Complejidad: Alta**

  - [ ] Separar lógica de negocio de comandos CLI | **Complejidad: Alta**
  - [ ] Implementar pattern Command/Handler | **Complejidad: Media**
  - [ ] Mejorar manejo de errores y logging | **Complejidad: Media**
  - [ ] Refactorizar `SetupWizard.take_action()` (~80 líneas) en clases separadas: | **Complejidad: Alta**
    - [ ] `SetupCollector` - Recolección de datos | **Complejidad: Media**
    - [ ] `SetupValidator` - Validación de configuración | **Complejidad: Alta**
    - [ ] `SetupWriter` - Escritura de archivos | **Complejidad: Media**
  - [ ] Mover imports dentro de métodos al inicio de archivos | **Complejidad: Baja**
  - [ ] Centralizar lectura de YAML en `utils.py` (código duplicado en 4+ archivos) | **Complejidad: Media**

- [ ] **Modernización de Patrones Python** | **Complejidad: Media**
  - [ ] Migrar `os.path.join()` a `pathlib.Path` en todos los módulos | **Complejidad: Media**
  - [ ] Reemplazar string formatting `%` por f-strings | **Complejidad: Baja**
  - [ ] Usar `TypedDict` para contextos de filtros Jinja2 | **Complejidad: Media**
  - [ ] Reemplazar `try/except Exception` genéricos por excepciones específicas | **Complejidad: Media**

- [ ] **Mejorar test coverage** | **Complejidad: Alta**
  - [ ] Configurar pytest-cov | **Complejidad: Baja**
  - [ ] Objetivo: >80% coverage en módulos core | **Complejidad: Alta**
  - [ ] Añadir integration tests | **Complejidad: Alta**

- [ ] **Tests Críticos Faltantes** (módulos sin cobertura) | **Complejidad: Alta**
  - [ ] `kolla_ansible/ansible.py` - Core de ejecución de playbooks | **Complejidad: Alta**
  - [ ] `kolla_ansible/utils.py` - Utilidades fundamentales | **Complejidad: Media**
  - [ ] `kolla_ansible/cli/commands.py` - Todos los comandos CLI | **Complejidad: Alta**
  - [ ] `kolla_ansible/cmd/genpwd.py` - Generación de passwords (crítico seguridad) | **Complejidad: Media**
  - [ ] `kolla_ansible/hashi_vault.py` - Integración con Vault | **Complejidad: Media**
  - [ ] Crear `conftest.py` con fixtures compartidos | **Complejidad: Baja**
  - [ ] Añadir tests parametrizados con `@pytest.mark.parametrize` | **Complejidad: Baja**

**Archivos afectados**: `kolla_ansible/`, `tests/`

#### 1.3 Configuración de Herramientas de Desarrollo

**Impacto**: Medio | **Complejidad**: Baja

- [ ] **Configurar pytest en setup.cfg** | **Complejidad: Baja**
  - [ ] Añadir sección `[tool:pytest]` con `testpaths`, `addopts` | **Complejidad: Baja**
  - [ ] Configurar `--cov-fail-under=70` para enforcement | **Complejidad: Baja**
  - [ ] Añadir `filterwarnings` para deprecations | **Complejidad: Baja**

- [ ] **Configurar mypy para type checking** | **Complejidad: Media**
  - [ ] Añadir sección `[mypy]` en `setup.cfg` | **Complejidad: Baja**
  - [ ] Crear `[testenv:mypy]` en `tox.ini` | **Complejidad: Baja**
  - [ ] Añadir `types-PyYAML`, `types-requests` como deps | **Complejidad: Baja**

- [ ] **Excepciones Personalizadas** | **Complejidad: Media**
  - [ ] Crear `kolla_ansible/exceptions.py` con: | **Complejidad: Baja**
    - [ ] `VaultAuthenticationError` | **Complejidad: Baja**
    - [ ] `VaultConfigError` | **Complejidad: Baja**
    - [ ] `ConfigurationError` | **Complejidad: Baja**
    - [ ] `PasswordGenerationError` | **Complejidad: Baja**
  - [ ] Reemplazar `sys.exit(1)` por excepciones en `hashi_vault.py` | **Complejidad: Media**
  - [ ] Reemplazar `print()` por logging estructurado | **Complejidad: Baja**

**Archivos afectados**: `setup.cfg`, `tox.ini`, `kolla_ansible/exceptions.py`, `kolla_ansible/hashi_vault.py`

#### 1.4 Dependencies Update

**Impacto**: Medio | **Complejidad**: Alta

- [ ] **Actualizar Ansible Core** | **Complejidad: Alta**

  - [ ] Migrar a Ansible 2.19+ | **Complejidad: Alta**
  - [ ] Resolver incompatibilidades | **Complejidad: Alta**
  - [ ] Actualizar `requirements-core.yml` | **Complejidad: Media**

- [ ] **Actualizar Collections** | **Complejidad: Media**

  - [ ] `community.docker` a versión 5.x | **Complejidad: Media**
  - [ ] `containers.podman` (migración gradual) | **Complejidad: Media**
  - [ ] Verificar compatibilidad | **Complejidad: Media**

- [ ] **Actualizar Python Dependencies** | **Complejidad: Baja**
  - [ ] Añadir upper bounds en `requirements.txt`:
    - [ ] `bcrypt>=3.0.0,<5` | **Complejidad: Baja**
    - [ ] `Jinja2>=3,<4` | **Complejidad: Baja**
    - [ ] `netaddr>=0.7.19,<1.0` | **Complejidad: Baja**
  - [ ] Actualizar `cryptography`, `hvac` | **Complejidad: Media**
  - [ ] Resolver CVEs conocidas | **Complejidad: Media**

**Archivos afectados**: `requirements.txt`, `requirements-core.yml`, `setup.cfg`

### 2. Seguridad [ALTA PRIORIDAD]

#### 2.1 Security Hardening

**Impacto**: Alto | **Complejidad**: Media

- [ ] **Secrets Management** | **Complejidad: Alta**
  - [ ] Integración completa con HashiCorp Vault | **Complejidad: Alta**
  - [ ] Soporte para AWS Secrets Manager | **Complejidad: Alta**
  - [ ] Rotación automática de passwords | **Complejidad: Alta**

- [ ] **Mejorar generación de passwords** | **Complejidad: Media**

  - [ ] Eliminar uso de MD5 (B303 bandit skip) | **Complejidad: Baja**
  - [ ] Implementar SHA256 para hashing | **Complejidad: Media**
  - [ ] Añadir rate limiting | **Complejidad: Media**

- [ ] **Validación de inputs** | **Complejidad: Media**

  - [ ] Validar IPs en CLI | **Complejidad: Baja**
  - [ ] Validar paths de archivos | **Complejidad: Baja**
  - [ ] Sanitizar inputs de usuario | **Complejidad: Media**

**Archivos afectados**: `tools/generate_passwords.py`, `kolla_ansible/cmd/*.py`

#### 2.2 Security Scanning

**Impacto**: Medio | **Complejidad**: Baja

- [ ] **Integrar herramientas de seguridad** | **Complejidad: Baja**
  - [ ] Bandit para análisis Python | **Complejidad: Baja**
  - [ ] Ansible-lint security rules | **Complejidad: Baja**
  - [ ] Container image vulnerability scanning | **Complejidad: Media**
  - [ ] SAST en CI/CD pipeline | **Complejidad: Media**

**Archivos afectados**: `.pre-commit-config.yaml`, `tox.ini`, CI/CD configs

### 3. Performance [MEDIA PRIORIDAD]

#### 3.1 Deployment Optimization

**Impacto**: Alto | **Complejidad**: Alta

- [ ] **Paralelización inteligente** | **Complejidad: Alta**

  - [ ] Revisar `ANSIBLE_SERIAL = 0` | **Complejidad: Media**
  - [ ] Implementar paralelización por grupos | **Complejidad: Alta**
  - [ ] Optimizar orden de ejecución de tasks | **Complejidad: Alta**

- [ ] **Caching de artifacts** | **Complejidad: Alta**
  - [ ] Cache de imágenes de contenedor | **Complejidad: Media**
  - [ ] Re-deployments incrementales | **Complejidad: Alta**
  - [ ] Solo desplegar servicios modificados | **Complejidad: Media**

**Archivos afectados**: `ansible/`, configuraciones de Ansible

#### 3.2 Resource Optimization

**Impacto**: Medio | **Complejidad**: Media

- [ ] **Configuraciones eficientes por defecto** | **Complejidad: Media**
  - [ ] Optimizar CPU/memory limits | **Complejidad: Media**
  - [ ] Profiling automatizado | **Complejidad: Media**
  - [ ] Identificación de bottlenecks | **Complejidad: Media**

**Archivos afectados**: `ansible/group_vars/`, templates de configuración

### 4. Developer Experience [MEDIA PRIORIDAD]

#### 4.1 Developer Tooling

**Impacto**: Medio | **Complejidad**: Baja

- [ ] **Nuevos comandos CLI**
  - [ ] `kolla-ansible dev-setup`: Setup de entorno de desarrollo | **Complejidad: Baja**
  - [ ] `kolla-ansible lint`: Verificación local completa | **Complejidad: Baja**
  - [ ] `kolla-ansible test`: Tests rápidos | **Complejidad: Baja**
  - [ ] `kolla-ansible debug`: Información del sistema | **Complejidad: Baja**
  - [ ] `kolla-ansible health-check`: Validación post-deployment | **Complejidad: Media**
  - [ ] `kolla-ansible logs`: Recolección centralizada de logs | **Complejidad: Media**
  - [ ] `kolla-ansible explain SERVICE`: Documentación inline | **Complejidad: Media**

**Archivos afectados**: `kolla_ansible/cmd/`, `setup.cfg`

#### 4.2 Pre-commit Hooks

**Impacto**: Bajo | **Complejidad**: Baja

- [ ] **Automatizar verificaciones** | **Complejidad: Baja**
  - [ ] Ansible-lint en pre-commit | **Complejidad: Baja**
  - [ ] Bandit security checks | **Complejidad: Baja**
  - [ ] Type checking con mypy | **Complejidad: Media**
  - [ ] Code formatting con black | **Complejidad: Baja**
  - [ ] `pyupgrade` - Modernización automática de sintaxis Python | **Complejidad: Baja**
  - [ ] `isort` - Ordenamiento automático de imports | **Complejidad: Baja**
  - [ ] `check-yaml` - Validación de archivos YAML | **Complejidad: Baja**
  - [ ] `trailing-whitespace` y `end-of-file-fixer` | **Complejidad: Baja**

**Archivos afectados**: `.pre-commit-config.yaml`

---

## 🚀 Mejoras a Medio Plazo (Q2-Q3 2025)

### 5. Observabilidad Avanzada

#### 5.1 Dashboard Unificado

**Impacto**: Alto | **Complejidad**: Alta

- [ ] **Integración con Grafana** | **Complejidad: Alta**
  - [ ] Dashboards pre-configurados para todos los servicios | **Complejidad: Media**
  - [ ] Métricas custom para Kolla-Ansible | **Complejidad: Media**
  - [ ] Alertas inteligentes basadas en patrones | **Complejidad: Alta**

#### 5.2 Logging Mejorado

**Impacto**: Medio | **Complejidad**: Media

- [ ] **Estandarización de logs** | **Complejidad: Media**
  - [ ] Formato JSON en todos los contenedores | **Complejidad: Media**
  - [ ] Correlation IDs para tracing cross-service | **Complejidad: Media**
  - [ ] Integración con Loki | **Complejidad: Media**

#### 5.3 Métricas de Deployment

**Impacto**: Medio | **Complejidad**: Media

- [ ] **Instrumentación de comandos**
  - [ ] Time tracking por fase
  - [ ] Resource utilization durante deployments
  - [ ] Error rate y failure pattern analysis

### 6. Compatibilidad y Actualizaciones

#### 6.1 OpenStack Updates

**Impacto**: Alto | **Complejidad**: Alta

- [ ] **Actualizar a OpenStack 2025.1** | **Complejidad: Alta**
  - [ ] Verificar compatibilidad | **Complejidad: Alta**
  - [ ] Actualizar configuraciones | **Complejidad: Alta**
  - [ ] Testing exhaustivo | **Complejidad: Alta**

#### 6.2 Nuevos Servicios

**Impacto**: Medio | **Complejidad**: Alta

- [ ] **Soporte para servicios emergentes** | **Complejidad: Alta**
  - [ ] Ironic (bare metal) | **Complejidad: Alta**
  - [ ] Cyborg (accelerators) | **Complejidad: Alta**
  - [ ] Mejoras en Nova, Neutron, Cinder | **Complejidad: Alta**

### 7. Documentación de Roles Ansible

#### 7.1 Estandarización de defaults/main.yml

**Impacto**: Medio | **Complejidad**: Media

- [ ] **Documentar variables en defaults/main.yml** | **Complejidad: Media**
  - [ ] Añadir comentarios descriptivos a cada variable | **Complejidad: Media**
  - [ ] Especificar tipo de dato (integer, string, boolean, list) | **Complejidad: Baja**
  - [ ] Indicar valores por defecto y rangos válidos | **Complejidad: Baja**
  - [ ] Ejemplo de formato estándar:
    ```yaml
    # Port for Nova API service
    # Type: integer
    # Default: 8774
    nova_api_port: 8774
    ```

- [ ] **Crear meta/argument_specs.yml** (Ansible 2.11+) | **Complejidad: Media**
  - [ ] Validación automática de variables de rol | **Complejidad: Media**
  - [ ] Documentación generada automáticamente | **Complejidad: Media**
  - [ ] Priorizar roles: `nova`, `neutron`, `keystone`, `common` | **Complejidad: Media**

**Archivos afectados**: `ansible/roles/*/defaults/main.yml`, `ansible/roles/*/meta/`

### 8. Usabilidad y Simplificación

#### 8.1 Configuración Simplificada

**Impacto**: Alto | **Complejidad**: Media

- [ ] **Valores por defecto inteligentes** | **Complejidad: Media**
  - [ ] Reducir variables requeridas | **Complejidad: Media**
  - [ ] Auto-detección de configuración | **Complejidad: Alta**
  - [ ] Templates por tipo de deployment | **Complejidad: Media**

#### 7.2 Deployment Incremental

**Impacto**: Alto | **Complejidad**: Alta

- [ ] **Soporte para updates parciales** | **Complejidad: Alta**
  - [ ] Deployment de servicios individuales | **Complejidad: Media**
  - [ ] Rolling updates sin downtime | **Complejidad: Alta**
  - [ ] Rollback automatizado | **Complejidad: Alta**

### 8. Certificados y Compliance

#### 8.1 Gestión de Certificados

**Impacto**: Medio | **Complejidad**: Media

- [ ] **Mejoras en cert management** | **Complejidad: Media**
  - [ ] Integración con cert-manager | **Complejidad: Media**
  - [ ] Renovación automática sin downtime | **Complejidad: Alta**
  - [ ] Certificados custom por servicio | **Complejidad: Media**

#### 8.2 Compliance

**Impacto**: Medio | **Complejidad**: Alta

- [ ] **Hardening y compliance** | **Complejidad: Alta**
  - [ ] Implementar CIS benchmarks | **Complejidad: Alta**
  - [ ] FIPS 140-2 compliance | **Complejidad: Alta**
  - [ ] Configuraciones de seguridad estrictas por defecto | **Complejidad: Media**

---

## 📊 Mejoras a Largo Plazo (Q4 2025+)

### 9. Multi-Cloud y Escalabilidad

- [ ] **Multi-cloud readiness** | **Complejidad: Alta**

  - [ ] Deployment en múltiples clouds | **Complejidad: Alta**
  - [ ] Cloud-init integration | **Complejidad: Alta**
  - [ ] Networking híbrido con VPN | **Complejidad: Alta**

- [ ] **Auto-scaling** | **Complejidad: Alta**
  - [ ] Auto-scaling básico en servicios stateless | **Complejidad: Alta**
  - [ ] Resource optimization automática | **Complejidad: Alta**

### 10. CI/CD y Testing

- [ ] **Mejorar pipeline CI/CD** | **Complejidad: Media**

  - [ ] Expandir matrix de testing (más distros) | **Complejidad: Media**
  - [ ] Integration tests automatizados
  - [ ] Nightly builds con regression reports

- [ ] **Dependabot**
  - [ ] Actualizaciones automáticas de dependencias
  - [ ] Security vulnerability alerts

### 11. Documentación Interactiva

- [ ] **Tutoriales ejecutables** | **Complejidad: Media**
  - [ ] Ejemplos interactivos | **Complejidad: Media**
  - [ ] AI-assisted diagnostics | **Complejidad: Alta**
  - [ ] Traducción a múltiples idiomas | **Complejidad: Media**

### 12. Documentación de Arquitectura

- [ ] **Crear sección doc/source/architecture/** | **Complejidad: Media**
  - [ ] `overview.rst` - Visión general del sistema | **Complejidad: Baja**
  - [ ] `components.rst` - Descripción de componentes principales | **Complejidad: Media**
  - [ ] `data-flow.rst` - Flujo de datos en deployments | **Complejidad: Media**
  - [ ] Diagrama de dependencias entre roles | **Complejidad: Media**

- [ ] **Documentar API interna de Python** | **Complejidad: Media**
  - [ ] `doc/source/api/filters.rst` - Filtros Jinja2 custom | **Complejidad: Media**
  - [ ] `doc/source/api/cli.rst` - Comandos CLI y opciones | **Complejidad: Media**
  - [ ] `doc/source/api/modules.rst` - Módulos Ansible custom | **Complejidad: Media**

- [ ] **Guías para desarrolladores** | **Complejidad: Media**
  - [ ] `doc/source/developer/testing.rst` - Cómo escribir y ejecutar tests | **Complejidad: Media**
  - [ ] `doc/source/developer/debugging.rst` - Técnicas de debugging | **Complejidad: Media**
  - [ ] `doc/source/developer/releasing.rst` - Proceso de release | **Complejidad: Media**

- [ ] **Documentar API interna de Python**
  - [ ] `doc/source/api/filters.rst` - Filtros Jinja2 custom
  - [ ] `doc/source/api/cli.rst` - Comandos CLI y opciones
  - [ ] `doc/source/api/modules.rst` - Módulos Ansible custom

- [ ] **Guías para desarrolladores**
  - [ ] `doc/source/developer/testing.rst` - Cómo escribir y ejecutar tests
  - [ ] `doc/source/developer/debugging.rst` - Técnicas de debugging
  - [ ] `doc/source/developer/releasing.rst` - Proceso de release

---

## 🔍 Análisis de Gaps Técnicos Identificados

### Problemas Críticos del Código Base

1. **Ansible Lint Issues**: 28 reglas deshabilitadas en `.ansible-lint`

   - `unnamed-task`: FIXME(mgoddard) - Falta naming en muchas tasks
   - `no-changed-when`: TODO(mnasiadka) - Commands sin indicadores de cambio
   - `no-handler`: Tasks que deberían ser handlers
   - `risky-file-permissions`: Permisos no especificados explícitamente
   - `command-instead-of-module`: Uso de command en lugar de módulos nativos

2. **Python Code Quality**:

   - Falta type hints en módulos críticos (`ansible.py`, `utils.py`, `cmd/*.py`)
   - Test coverage limitado (solo stestr básico, no coverage reports)
   - CLI commands muy monolíticos (SetupWizard, ValidateSetup podrían refactorizarse)

3. **Dependencies Outdated**:

   - Ansible-core limitado a <2.19 (versión actual 2.18)
   - Collections con versiones muy restrictivas (`community.docker <5`)
   - Requirements.txt sin upper bounds en `cryptography`, `hvac`

4. **Performance Bottlenecks**:

   - `ANSIBLE_SERIAL = 0` (serial execution por defecto)
   - No hay caching de artifacts en deployments
   - Tasks repetitivas sin optimización

5. **Security Gaps**:

   - Bandit skip para MD5 hash (B303) - debería usar SHA256
   - Password generation sin rate limiting
   - Falta validación robusta de inputs en CLI (IPs, paths)

6. **Documentation Gaps**:
   - Muchos TODO/FIXME sin resolver en código
   - Falta documentación inline en código Python
   - README.rst genérico, falta getting started específico

7. **Arquitectura de Código**:
   - Clases CLI monolíticas (`SetupWizard`, `ValidateSetup` con métodos de ~80 líneas)
   - Código duplicado para lectura YAML en 4+ archivos
   - Uso de `sys.exit()` y `print()` en lugar de excepciones/logging
   - Falta `conftest.py` para fixtures compartidos en tests

8. **Roles Ansible**:
   - Variables en `defaults/main.yml` sin documentación de tipo/descripción
   - Falta `meta/argument_specs.yml` para validación automática
   - Inconsistencia en estructura de comentarios entre roles

---

## 🎯 Métricas de Éxito

| Métrica                 | Objetivo           | Estado Actual  |
| ----------------------- | ------------------ | -------------- |
| Deployment Success Rate | >95%               | ~85%           |
| Time to Deploy          | <30 min            | ~45 min        |
| Security Score (CIS)    | Level 1            | Parcial        |
| Documentation Coverage  | 90%                | ~70%           |
| Test Coverage           | >80%               | ~35%           |
| Ansible Lint Issues     | 0 críticos         | 28 reglas skip |
| Performance Overhead    | <50% vs bare metal | ~60%           |
| Developer Setup Time    | <5 min             | ~15 min        |
| Funciones con Type Hints| 100%               | ~20%           |
| Módulos con Docstrings  | 100%               | ~40%           |
| Excepciones Custom      | 5+                 | 1              |
| Roles con argument_specs| 100%               | 0%             |

---

## 📋 Plan de Implementación por Quarters

### Q1 2025: Foundation & Code Quality

**Objetivo**: Establecer baseline de calidad de código

- **Semanas 1-2**: Actualización de dependencias (Ansible 2.19+, Python deps)
- **Semanas 3-4**: Fix ansible-lint warnings críticos (unnamed-task, no-changed-when)
- **Semanas 5-6**: Type hints básicos y mejoras en configuración inicial
- **Semanas 7-8**: Security hardening y security scanning setup
- **Semanas 9-12**: Test coverage improvement y CI/CD optimization

**Recursos**: 2 developers full-time + 1 DevOps part-time

### Q2 2025: Developer Experience & Observability

**Objetivo**: Transformar la experiencia de desarrollo

- **Mes 1**: Developer tooling (dev-setup, lint, debug commands)
- **Mes 2**: Dashboard unificado y métricas custom
- **Mes 3**: Logging mejorado y health checks automatizados

**Recursos**: 2 developers + 1 UX/DX engineer + 1 DevOps

### Q3 2025: Performance & Reliability

**Objetivo**: Optimización para producción

- **Mes 1**: Optimizaciones de deployment (parallelization, caching)
- **Mes 2**: Multi-cloud support básico y resource optimization
- **Mes 3**: Chaos engineering básico y disaster recovery automation

**Recursos**: 3 developers + 1 SRE + 1 performance engineer

### Q4 2025: Advanced Features & Integration

**Objetivo**: Feature parity con competidores

- **Mes 1**: Nuevos servicios OpenStack (Ironic, Cyborg)
- **Mes 2**: Cloud native evolution (K8s experimental)
- **Mes 3**: AI-assisted troubleshooting y community expansion

**Recursos**: 3 developers + 1 cloud architect + community managers

---

## 📚 Referencias y Documentación

### Documentos Relacionados

- **Kolla-Control TODO**: `kolla-control/TODO.md` - Tareas del portal web
- **Ansible Lint Progress**: `ANSIBLE-LINT-PROGRESS.md` - Progreso de limpieza de lint
- **Documentation Index**: `DOCUMENTATION_INDEX.md` - Índice de toda la documentación
- **Architecture Summary**: `RESUMEN_ARQUITECTURA.md` - Resumen de arquitectura

### Archivos Clave para Modificar

- **Ansible Lint**: `.ansible-lint`, `.ansible-lint-test`
- **Python Config**: `setup.cfg`, `setup.py`, `tox.ini`
- **Dependencies**: `requirements.txt`, `requirements-core.yml`, `requirements.yml`
- **Pre-commit**: `.pre-commit-config.yaml`
- **Tests**: `tests/`, `.stestr.conf`

### Comandos Útiles

```bash
# Lint
tox -e ansible-lint
tox -e pep8

# Tests
tox -e py311

# Setup wizard
kolla-ansible setup-wizard

# Validate setup
kolla-ansible validate-setup
```

---

**Última actualización**: 9 Ene 2026  
**Próxima revisión**: Q1 2026 (Marzo 2026)

> **Nota**: Este TODO se enfoca en mejoras alcanzables con el equipo actual, priorizando impacto vs complejidad. Revisar trimestralmente basado en feedback de usuarios y evolución de OpenStack.
