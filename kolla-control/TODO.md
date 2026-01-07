# TODO - Kolla-Control Web Portal

> **Portal web moderno para gestión de Kolla-Ansible con integración de Foreman**

**Ubicación**: `kolla-control/` - Subproyecto dentro del repositorio principal  
**Status**: ✅ Estructura inicial creada (31 Oct 2025)

---

## ✅ Características Implementadas

### Backend (FastAPI)

- [x] **Arquitectura completa**
  - [x] Modelos de base de datos (SQLAlchemy)
  - [x] API REST endpoints (deployments, operations, inventory)
  - [x] Wrapper de Kolla-Ansible CLI con streaming
  - [x] WebSocket support para logs en tiempo real
  - [x] Docker Compose para desarrollo
  - [x] Documentación (README + QUICKSTART)

### Frontend (React + TypeScript)

- [x] **Fase 1: Infraestructura Core** ✅

  - [x] React 19 + TypeScript 5.7 + Vite 6
  - [x] Dashboard con métricas y gráficos (Recharts)
  - [x] Contexts (Theme, Auth, WebSocket)
  - [x] Layout principal con navegación
  - [x] Real-time WebSocket (Socket.IO)

- [x] **Fase 2: Interactive Features** ✅ (Completado 1 Nov 2025, Commit 40d7a4523)
  - [x] Deployment Wizard (4-step form with validation)
  - [x] Inventory Manager (Full CRUD hosts management)
  - [x] Operations Panel (7 operations with real-time status)
  - [x] Form validation (React Hook Form + Zod)
  - [x] TanStack Query integration
  - [x] Dev server verification & git push

---

## 🎯 Prioridades Inmediatas

### Fase 3: Advanced Features [EN PROGRESO]

**Impacto**: Alto | **Complejidad**: Media

- [ ] **Real-time Logs Viewer**

  - [ ] Componente de logs con filtrado
  - [ ] Búsqueda en tiempo real
  - [ ] Exportación de logs
  - [ ] Auto-scroll y pause functionality
  - [ ] Color coding por nivel de log

- [ ] **Monaco Editor para YAML**
  - [ ] Integración de Monaco Editor
  - [ ] Syntax highlighting para YAML
  - [ ] Validación de sintaxis
  - [ ] Auto-completion para variables Kolla
  - [ ] Diff viewer para comparar configuraciones

**Archivos afectados**: `frontend/src/pages/`, `frontend/src/components/`

### Fase 4: Backend Async Tasks [ALTA PRIORIDAD]

**Impacto**: Alto | **Complejidad**: Alta

- [ ] **Celery Integration**

  - [ ] Setup de Celery con Redis
  - [ ] Task queue para operaciones largas
  - [ ] Progress tracking
  - [ ] Task cancellation
  - [ ] Retry logic con exponential backoff

- [ ] **Background Jobs**
  - [ ] Deployment tasks asíncronos
  - [ ] Health checks periódicos
  - [ ] Log rotation y cleanup
  - [ ] Backup automático de configuraciones

**Archivos afectados**: `backend/app/core/celery.py`, `backend/requirements.txt`

### Fase 5: Foreman Integration [ALTA PRIORIDAD]

**Impacto**: Alto | **Complejidad**: Alta

- [ ] **Foreman API Client**

  - [ ] Cliente Python para Foreman API
  - [ ] Autenticación y autorización
  - [ ] CRUD operations para hosts
  - [ ] Provisioning de bare metal
  - [ ] Sincronización de inventario

- [ ] **UI para Foreman**
  - [ ] Página de gestión de hosts Foreman
  - [ ] Wizard de provisioning
  - [ ] Monitoreo de estado de provisioning
  - [ ] Integración con Inventory Manager

**Archivos afectados**: `backend/app/services/foreman.py`, `frontend/src/pages/ForemanManager.tsx`

---

## 🚀 Mejoras a Medio Plazo

### 6. Autenticación y Autorización [MEDIA PRIORIDAD]

**Impacto**: Alto | **Complejidad**: Media

- [ ] **JWT Authentication**

  - [ ] Login/Logout endpoints
  - [ ] Token refresh mechanism
  - [ ] Password reset flow
  - [ ] Session management

- [ ] **RBAC (Role-Based Access Control)**
  - [ ] Definición de roles (Admin, Operator, Viewer)
  - [ ] Permisos por recurso
  - [ ] Middleware de autorización
  - [ ] UI para gestión de usuarios y roles

**Archivos afectados**: `backend/app/core/auth.py`, `backend/app/models/user.py`

### 7. Monitoring y Observabilidad [MEDIA PRIORIDAD]

**Impacto**: Medio | **Complejidad**: Media

- [ ] **Prometheus Integration**

  - [ ] Métricas de aplicación
  - [ ] Métricas de Kolla-Ansible
  - [ ] Exporters custom

- [ ] **Grafana Dashboards**
  - [ ] Dashboard de deployment metrics
  - [ ] Dashboard de health checks
  - [ ] Dashboard de resource utilization

**Archivos afectados**: `backend/app/core/metrics.py`, `docker-compose.yml`

### 8. Testing [MEDIA PRIORIDAD]

**Impacto**: Alto | **Complejidad**: Media

- [ ] **Backend Tests**

  - [ ] Unit tests con pytest
  - [ ] Integration tests para API
  - [ ] Test coverage >80%
  - [ ] Mocking de Kolla-Ansible CLI

- [ ] **Frontend Tests**
  - [ ] Unit tests con Vitest
  - [ ] Component tests con React Testing Library
  - [ ] E2E tests con Playwright
  - [ ] Test coverage >70%

**Archivos afectados**: `backend/tests/`, `frontend/src/**/*.test.tsx`

---

## 📊 Mejoras a Largo Plazo

### 9. CI/CD Pipeline

**Impacto**: Medio | **Complejidad**: Media

- [ ] **GitHub Actions**

  - [ ] Lint y tests automáticos
  - [ ] Build de imágenes Docker
  - [ ] Deployment automático a staging
  - [ ] Security scanning

- [ ] **Docker Production Images**
  - [ ] Multi-stage builds optimizados
  - [ ] Image scanning con Trivy
  - [ ] Registry privado
  - [ ] Versionado semántico

### 10. Advanced Features

**Impacto**: Medio | **Complejidad**: Alta

- [ ] **Configuration Management**

  - [ ] Versionado de configuraciones
  - [ ] Diff viewer entre versiones
  - [ ] Rollback de configuraciones
  - [ ] Templates de configuración

- [ ] **Audit Logging**

  - [ ] Log de todas las operaciones
  - [ ] Búsqueda y filtrado de audit logs
  - [ ] Exportación de audit logs
  - [ ] Compliance reports

- [ ] **Notifications**
  - [ ] Email notifications
  - [ ] Slack integration
  - [ ] Webhook support
  - [ ] In-app notifications

### 11. Performance Optimization

**Impacto**: Medio | **Complejidad**: Media

- [ ] **Frontend Optimization**

  - [ ] Code splitting
  - [ ] Lazy loading de componentes
  - [ ] Service Worker para caching
  - [ ] Bundle size optimization

- [ ] **Backend Optimization**
  - [ ] Database query optimization
  - [ ] Caching con Redis
  - [ ] Connection pooling
  - [ ] API response compression

---

## 🎯 Métricas de Éxito

| Métrica                  | Objetivo     | Estado Actual |
| ------------------------ | ------------ | ------------- |
| API Response Time        | <200ms (p95) | ~150ms        |
| Frontend Load Time       | <2s          | ~1.5s         |
| Test Coverage (Backend)  | >80%         | 0%            |
| Test Coverage (Frontend) | >70%         | 0%            |
| Deployment Success Rate  | >95%         | N/A           |
| User Satisfaction        | >4.5/5       | N/A           |

---

## 📋 Plan de Implementación

### Sprint 1 (2 semanas): Fase 3 - Advanced Features

**Objetivo**: Completar logs viewer y Monaco editor

- **Semana 1**: Real-time logs viewer con filtrado
- **Semana 2**: Monaco editor para YAML con validación

**Recursos**: 1 frontend developer

### Sprint 2 (3 semanas): Fase 4 - Backend Async

**Objetivo**: Implementar Celery y background jobs

- **Semana 1**: Setup de Celery con Redis
- **Semana 2**: Migrar operaciones a tasks asíncronos
- **Semana 3**: Progress tracking y retry logic

**Recursos**: 1 backend developer

### Sprint 3 (4 semanas): Fase 5 - Foreman Integration

**Objetivo**: Integración completa con Foreman

- **Semana 1-2**: Foreman API client
- **Semana 3**: UI para gestión de hosts
- **Semana 4**: Wizard de provisioning

**Recursos**: 1 full-stack developer

### Sprint 4 (3 semanas): Auth & RBAC

**Objetivo**: Sistema de autenticación completo

- **Semana 1**: JWT authentication
- **Semana 2**: RBAC implementation
- **Semana 3**: UI para gestión de usuarios

**Recursos**: 1 backend + 1 frontend developer

### Sprint 5 (2 semanas): Testing

**Objetivo**: Alcanzar coverage targets

- **Semana 1**: Backend tests (>80% coverage)
- **Semana 2**: Frontend tests (>70% coverage)

**Recursos**: 1 QA engineer + 1 developer

---

## 📚 Referencias

### Documentación

- **README**: `kolla-control/README.md` - Descripción general del proyecto
- **Quick Start**: `kolla-control/QUICKSTART.md` - Guía de inicio rápido
- **API Docs**: `http://localhost:8000/docs` - Swagger UI (cuando el backend está corriendo)

### Estructura del Proyecto

```
kolla-control/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── core/     # Core functionality (config, celery, etc.)
│   │   ├── models/   # SQLAlchemy models
│   │   └── services/ # Business logic
│   └── requirements.txt
├── frontend/         # React frontend
│   ├── src/
│   │   ├── components/  # Reusable components
│   │   ├── contexts/    # React contexts
│   │   ├── pages/       # Page components
│   │   └── services/    # API clients
│   └── package.json
└── docker-compose.yml
```

### Comandos Útiles

```bash
# Backend
cd kolla-control/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd kolla-control/frontend
npm install
npm run dev

# Docker Compose
cd kolla-control
docker-compose up -d
```

### Stack Tecnológico

- **Backend**: FastAPI, SQLAlchemy, Pydantic, WebSockets
- **Frontend**: React 19, TypeScript 5.7, Vite 6, TailwindCSS
- **Database**: PostgreSQL (producción), SQLite (desarrollo)
- **Task Queue**: Celery + Redis (pendiente)
- **Monitoring**: Prometheus + Grafana (pendiente)

---

**Última actualización**: 23 Nov 2025  
**Próxima revisión**: Sprint 1 completion (Diciembre 2025)

> **Nota**: Este TODO se enfoca en el desarrollo del portal web Kolla-Control. Para tareas relacionadas con el core de Kolla-Ansible, ver `../TODO.md`
