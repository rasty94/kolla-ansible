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

### 1. Calidad de Código [ALTA PRIORIDAD]

#### 1.1 Ansible Lint Cleanup

**Impacto**: Alto | **Complejidad**: Media

- [ ] **Resolver warnings críticos de ansible-lint** (28 reglas deshabilitadas)
  - [ ] `unnamed-task`: Añadir nombres descriptivos a todas las tasks
  - [ ] `no-changed-when`: Implementar indicadores de cambio en commands
  - [ ] `no-handler`: Convertir tasks repetitivas en handlers
  - [ ] `risky-file-permissions`: Especificar permisos explícitos
  - [ ] `command-instead-of-module`: Usar módulos nativos donde sea posible

**Archivos afectados**: `.ansible-lint`, `ansible/roles/*/tasks/*.yml`

#### 1.2 Python Code Modernization

**Impacto**: Alto | **Complejidad**: Media

- [ ] **Añadir type hints completos**

  - [ ] `kolla_ansible/ansible.py`
  - [ ] `kolla_ansible/utils.py`
  - [ ] `kolla_ansible/cmd/*.py`
  - [ ] `tools/*.py`

- [ ] **Refactorizar CLI commands**

  - [ ] Separar lógica de negocio de comandos CLI
  - [ ] Implementar pattern Command/Handler
  - [ ] Mejorar manejo de errores y logging

- [ ] **Mejorar test coverage**
  - [ ] Configurar pytest-cov
  - [ ] Objetivo: >80% coverage en módulos core
  - [ ] Añadir integration tests

**Archivos afectados**: `kolla_ansible/`, `tests/`

#### 1.3 Dependencies Update

**Impacto**: Medio | **Complejidad**: Alta

- [ ] **Actualizar Ansible Core**

  - [ ] Migrar a Ansible 2.19+
  - [ ] Resolver incompatibilidades
  - [ ] Actualizar `requirements-core.yml`

- [ ] **Actualizar Collections**

  - [ ] `community.docker` a versión 5.x
  - [ ] `containers.podman` (migración gradual)
  - [ ] Verificar compatibilidad

- [ ] **Actualizar Python Dependencies**
  - [ ] Añadir upper bounds en `requirements.txt`
  - [ ] Actualizar `cryptography`, `hvac`
  - [ ] Resolver CVEs conocidas

**Archivos afectados**: `requirements.txt`, `requirements-core.yml`, `setup.cfg`

### 2. Seguridad [ALTA PRIORIDAD]

#### 2.1 Security Hardening

**Impacto**: Alto | **Complejidad**: Media

- [ ] **Mejorar generación de passwords**

  - [ ] Eliminar uso de MD5 (B303 bandit skip)
  - [ ] Implementar SHA256 para hashing
  - [ ] Añadir rate limiting

- [ ] **Validación de inputs**

  - [ ] Validar IPs en CLI
  - [ ] Validar paths de archivos
  - [ ] Sanitizar inputs de usuario

- [ ] **Secrets Management**
  - [ ] Integración completa con HashiCorp Vault
  - [ ] Soporte para AWS Secrets Manager
  - [ ] Rotación automática de passwords

**Archivos afectados**: `tools/generate_passwords.py`, `kolla_ansible/cmd/*.py`

#### 2.2 Security Scanning

**Impacto**: Medio | **Complejidad**: Baja

- [ ] **Integrar herramientas de seguridad**
  - [ ] Bandit para análisis Python
  - [ ] Ansible-lint security rules
  - [ ] Container image vulnerability scanning
  - [ ] SAST en CI/CD pipeline

**Archivos afectados**: `.pre-commit-config.yaml`, `tox.ini`, CI/CD configs

### 3. Performance [MEDIA PRIORIDAD]

#### 3.1 Deployment Optimization

**Impacto**: Alto | **Complejidad**: Alta

- [ ] **Paralelización inteligente**

  - [ ] Revisar `ANSIBLE_SERIAL = 0`
  - [ ] Implementar paralelización por grupos
  - [ ] Optimizar orden de ejecución de tasks

- [ ] **Caching de artifacts**
  - [ ] Cache de imágenes de contenedor
  - [ ] Re-deployments incrementales
  - [ ] Solo desplegar servicios modificados

**Archivos afectados**: `ansible/`, configuraciones de Ansible

#### 3.2 Resource Optimization

**Impacto**: Medio | **Complejidad**: Media

- [ ] **Configuraciones eficientes por defecto**
  - [ ] Optimizar CPU/memory limits
  - [ ] Profiling automatizado
  - [ ] Identificación de bottlenecks

**Archivos afectados**: `ansible/group_vars/`, templates de configuración

### 4. Developer Experience [MEDIA PRIORIDAD]

#### 4.1 Developer Tooling

**Impacto**: Medio | **Complejidad**: Baja

- [ ] **Nuevos comandos CLI**
  - [ ] `kolla-ansible dev-setup`: Setup de entorno de desarrollo
  - [ ] `kolla-ansible lint`: Verificación local completa
  - [ ] `kolla-ansible test`: Tests rápidos
  - [ ] `kolla-ansible debug`: Información del sistema
  - [ ] `kolla-ansible health-check`: Validación post-deployment
  - [ ] `kolla-ansible logs`: Recolección centralizada de logs
  - [ ] `kolla-ansible explain SERVICE`: Documentación inline

**Archivos afectados**: `kolla_ansible/cmd/`, `setup.cfg`

#### 4.2 Pre-commit Hooks

**Impacto**: Bajo | **Complejidad**: Baja

- [ ] **Automatizar verificaciones**
  - [ ] Ansible-lint en pre-commit
  - [ ] Bandit security checks
  - [ ] Type checking con mypy
  - [ ] Code formatting con black

**Archivos afectados**: `.pre-commit-config.yaml`

---

## 🚀 Mejoras a Medio Plazo (Q2-Q3 2025)

### 5. Observabilidad Avanzada

#### 5.1 Dashboard Unificado

**Impacto**: Alto | **Complejidad**: Alta

- [ ] **Integración con Grafana**
  - [ ] Dashboards pre-configurados para todos los servicios
  - [ ] Métricas custom para Kolla-Ansible
  - [ ] Alertas inteligentes basadas en patrones

#### 5.2 Logging Mejorado

**Impacto**: Medio | **Complejidad**: Media

- [ ] **Estandarización de logs**
  - [ ] Formato JSON en todos los contenedores
  - [ ] Correlation IDs para tracing cross-service
  - [ ] Integración con Loki

#### 5.3 Métricas de Deployment

**Impacto**: Medio | **Complejidad**: Media

- [ ] **Instrumentación de comandos**
  - [ ] Time tracking por fase
  - [ ] Resource utilization durante deployments
  - [ ] Error rate y failure pattern analysis

### 6. Compatibilidad y Actualizaciones

#### 6.1 OpenStack Updates

**Impacto**: Alto | **Complejidad**: Alta

- [ ] **Actualizar a OpenStack 2025.1**
  - [ ] Verificar compatibilidad
  - [ ] Actualizar configuraciones
  - [ ] Testing exhaustivo

#### 6.2 Nuevos Servicios

**Impacto**: Medio | **Complejidad**: Alta

- [ ] **Soporte para servicios emergentes**
  - [ ] Ironic (bare metal)
  - [ ] Cyborg (accelerators)
  - [ ] Mejoras en Nova, Neutron, Cinder

### 7. Usabilidad y Simplificación

#### 7.1 Configuración Simplificada

**Impacto**: Alto | **Complejidad**: Media

- [ ] **Valores por defecto inteligentes**
  - [ ] Reducir variables requeridas
  - [ ] Auto-detección de configuración
  - [ ] Templates por tipo de deployment

#### 7.2 Deployment Incremental

**Impacto**: Alto | **Complejidad**: Alta

- [ ] **Soporte para updates parciales**
  - [ ] Deployment de servicios individuales
  - [ ] Rolling updates sin downtime
  - [ ] Rollback automatizado

### 8. Certificados y Compliance

#### 8.1 Gestión de Certificados

**Impacto**: Medio | **Complejidad**: Media

- [ ] **Mejoras en cert management**
  - [ ] Integración con cert-manager
  - [ ] Renovación automática sin downtime
  - [ ] Certificados custom por servicio

#### 8.2 Compliance

**Impacto**: Medio | **Complejidad**: Alta

- [ ] **Hardening y compliance**
  - [ ] Implementar CIS benchmarks
  - [ ] FIPS 140-2 compliance
  - [ ] Configuraciones de seguridad estrictas por defecto

---

## 📊 Mejoras a Largo Plazo (Q4 2025+)

### 9. Multi-Cloud y Escalabilidad

- [ ] **Multi-cloud readiness**

  - [ ] Deployment en múltiples clouds
  - [ ] Cloud-init integration
  - [ ] Networking híbrido con VPN

- [ ] **Auto-scaling**
  - [ ] Auto-scaling básico en servicios stateless
  - [ ] Resource optimization automática

### 10. CI/CD y Testing

- [ ] **Mejorar pipeline CI/CD**

  - [ ] Expandir matrix de testing (más distros)
  - [ ] Integration tests automatizados
  - [ ] Nightly builds con regression reports

- [ ] **Dependabot**
  - [ ] Actualizaciones automáticas de dependencias
  - [ ] Security vulnerability alerts

### 11. Documentación Interactiva

- [ ] **Tutoriales ejecutables**
  - [ ] Ejemplos interactivos
  - [ ] AI-assisted diagnostics
  - [ ] Traducción a múltiples idiomas

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

---

## 🎯 Métricas de Éxito

| Métrica                 | Objetivo           | Estado Actual  |
| ----------------------- | ------------------ | -------------- |
| Deployment Success Rate | >95%               | ~85%           |
| Time to Deploy          | <30 min            | ~45 min        |
| Security Score (CIS)    | Level 1            | Parcial        |
| Documentation Coverage  | 90%                | ~70%           |
| Test Coverage           | >80%               | ~40%           |
| Ansible Lint Issues     | 0 críticos         | 28 reglas skip |
| Performance Overhead    | <50% vs bare metal | ~60%           |
| Developer Setup Time    | <5 min             | ~15 min        |

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

**Última actualización**: 23 Nov 2025  
**Próxima revisión**: Q1 2025 (Marzo 2025)

> **Nota**: Este TODO se enfoca en mejoras alcanzables con el equipo actual, priorizando impacto vs complejidad. Revisar trimestralmente basado en feedback de usuarios y evolución de OpenStack.
