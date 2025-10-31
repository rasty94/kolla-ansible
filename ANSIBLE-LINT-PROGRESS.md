# Ansible-Lint Cleanup Progress

## 🎯 Objetivo
Resolver las 28 reglas de ansible-lint actualmente deshabilitadas en Kolla-Ansible

## 📊 Estado Actual (31 Octubre 2025)

### Análisis Completado ✅
- **Total YAML files**: 1,176
- **Files con problemas**: 736 (62.6%)
- **Unnamed tasks**: 997
- **Potential handlers**: 83
- **Commands sin changed_when**: 0 ✅ (ya resuelto!)

### Herramientas Creadas ✅

#### 1. fix_ansible_lint.py
- Auto-fix para unnamed tasks
- Genera nombres descriptivos basados en contexto
- Modo dry-run para testing seguro
- **Status**: ✅ Funcional y testeado

#### 2. identify_handlers.py  
- Identifica 83 tasks que deberían ser handlers
- Genera reportes por rol
- Sugiere conversiones
- **Status**: ✅ Funcional y testeado

#### 3. check_task_names.py
- Pre-commit hook para validar nombres
- Previene commits con unnamed tasks
- **Status**: ✅ Creado

#### 4. pre-commit-lint-check.sh
- Checks personalizados de Kolla-Ansible
- Warnings para potenciales handlers
- **Status**: ✅ Creado

#### 5. .pre-commit-config.yaml
- Configuración completa de pre-commit
- Integra ansible-lint, black, flake8, bandit
- **Status**: ✅ Creado

## 📋 Plan de Ejecución

### ✅ Fase 0: Setup (COMPLETADO)
- [x] Análisis de scope y estadísticas
- [x] Creación de herramientas automatizadas
- [x] Documentación de proceso
- [x] Pre-commit hooks configurados

### 🔄 Fase 1: Fix Unnamed Tasks (Semana 1-2)
**Target**: Eliminar 997 unnamed tasks

**Pasos**:
1. [ ] Ejecutar dry-run completo
   ```bash
   venv/bin/python3 tools/fix_ansible_lint.py --check > dryrun-results.txt
   ```

2. [ ] Aplicar fixes a roles core (test limitado)
   ```bash
   # Backup primero
   git checkout -b fix/ansible-lint-unnamed-tasks
   
   # Fix solo roles críticos primero
   venv/bin/python3 tools/fix_ansible_lint.py --fix
   ```

3. [ ] Verificar que nada se rompe
   ```bash
   ansible-lint ansible/roles/keystone/
   tox -e linters
   kolla-ansible prechecks -i ansible/inventory/all-in-one
   ```

4. [ ] Crear PR para review

5. [ ] Aplicar fixes al resto del proyecto

6. [ ] Remover `unnamed-task` de `.ansible-lint` skip_list

**Estimado**: 5-10 días
**Riesgo**: Bajo (solo añade metadatos, no cambia lógica)

### 🔄 Fase 2: Handler Conversion (Semana 3-4)
**Target**: Convertir 83 tasks a handlers

**Pasos**:
1. [ ] Generar reporte completo
   ```bash
   venv/bin/python3 tools/identify_handlers.py --output handlers-report.txt
   ```

2. [ ] Revisar y priorizar conversiones
   - Top 10 roles con más candidatos
   - Patterns más comunes

3. [ ] Convertir handlers manualmente por rol
   - Crear/actualizar `handlers/main.yml`
   - Reemplazar tasks con `notify:`
   - Testing por rol

4. [ ] Crear PRs por rol

5. [ ] Remover `no-handler` de skip_list (parcial)

**Estimado**: 10-15 días
**Riesgo**: Medio (cambia orden de ejecución)

### 🔄 Fase 3: Code Quality (Semana 5-6)
**Target**: Fix key-order, risky-file-permissions, var-naming

**Pasos**:
1. [ ] Estandarizar orden de keys en tasks
2. [ ] Añadir permisos explícitos a file tasks
3. [ ] Añadir prefijos de rol a variables

**Estimado**: 10-15 días
**Riesgo**: Bajo-Medio

### 🔄 Fase 4: Command Improvements (Semana 7-8)
**Target**: Reemplazar shell commands con módulos nativos

**Pasos**:
1. [ ] Identificar shell commands que pueden usar módulos
2. [ ] Crear script de sugerencias automáticas
3. [ ] Aplicar reemplazos seguros

**Estimado**: 10-15 días
**Riesgo**: Medio

## 📈 Métricas de Progreso

### Before (Baseline)
```
Rules disabled: 28
Unnamed tasks: 997
Potential handlers: 83
Files with issues: 736
Code quality: ~60%
```

### Current (31 Oct 2025)
```
Rules disabled: 28 (no change yet)
Unnamed tasks: 997 (tools ready to fix)
Potential handlers: 83 (identified)
Files with issues: 736
Code quality: ~60%
Tools created: 5 ✅
```

### Target (End of Phase 1)
```
Rules disabled: 27 (-1)
Unnamed tasks: 0 (-997) ✅
Potential handlers: 83
Files with issues: ~600 (-136)
Code quality: ~70% (+10%)
```

### Final Target (End of Phase 4)
```
Rules disabled: 15 (-13)
Unnamed tasks: 0 ✅
Potential handlers: 0 ✅
Files with issues: <200 (-536)
Code quality: >85% (+25%)
```

## 🚀 Siguiente Acción Inmediata

**READY TO START**: Fase 1 - Fix Unnamed Tasks

```bash
# 1. Crear branch
git checkout -b fix/ansible-lint-unnamed-tasks

# 2. Ejecutar dry-run y revisar
venv/bin/python3 tools/fix_ansible_lint.py --check | tee dryrun.log

# 3. Aplicar fixes
venv/bin/python3 tools/fix_ansible_lint.py --fix

# 4. Verificar
ansible-lint ansible/ | tee lint-after.log

# 5. Testing
tox -e linters
kolla-ansible prechecks

# 6. Commit
git add ansible/
git commit -m "Fix unnamed tasks across all ansible roles

- Added descriptive names to 997 unnamed tasks
- Used automated tool: tools/fix_ansible_lint.py
- Names generated based on module context
- No functional changes, only metadata

Related-Bug: #ansible-lint-cleanup
```

## 📝 Notas de Implementación

### Decisiones Técnicas
1. **Automated vs Manual**: Usamos automation para unnamed-task (low risk), manual para handlers (medium risk)
2. **Phased Approach**: Por roles para facilitar review y rollback
3. **Testing Strategy**: Pre-checks + lint + full deploy test

### Lessons Learned (to be filled)
- TBD after Phase 1

### Blockers & Risks
- **Testing Infrastructure**: Necesita entorno de test completo
- **Review Capacity**: 997 changes en un PR puede ser difícil de review
- **Backwards Compatibility**: Asegurar que nada se rompe

## 📚 Referencias

- [Detailed Roadmap](../docs/ansible-lint-fixes.md)
- [Tools README](README-ansible-lint.md)
- [Ansible-Lint Documentation](https://ansible-lint.readthedocs.io/)
- [Kolla-Ansible Contributing](../CONTRIBUTING.rst)

## 👥 Team

- **Owner**: @rasty94
- **Reviewers**: TBD
- **Testing**: TBD

---

**Last Updated**: 31 October 2025, 23:45 UTC
**Status**: 🟢 READY TO START - Phase 1
**Next Checkpoint**: End of Week 1 (Nov 7, 2025)
