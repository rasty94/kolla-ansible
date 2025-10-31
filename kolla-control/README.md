# Kolla-Control

**Modern Web UI for Kolla-Ansible Deployment Management**

Kolla-Control is a comprehensive web-based management portal for OpenStack deployments using Kolla-Ansible. It provides an intuitive interface for managing infrastructure, deployments, and operations with integrated Foreman support for bare metal provisioning.

## ✨ Features

### 🎯 Core Functionality
- **Interactive Dashboard**: Real-time cluster status, metrics, and alerts
- **Deployment Wizard**: Step-by-step guided OpenStack deployment
- **Inventory Management**: Visual host and group management with validation
- **Operations Center**: One-click operations (deploy, upgrade, backup, destroy)
- **Live Logs**: WebSocket streaming of Ansible playbook output
- **Configuration Editor**: Visual editor for globals.yml with validation

### 🔌 Integrations
- **Foreman Integration**: Automated bare metal provisioning
- **Prometheus/Grafana**: Built-in monitoring and alerting
- **Keystone Auth**: Optional OpenStack authentication
- **OpenSearch**: Centralized logging integration

### 🛡️ Enterprise Features
- **Role-Based Access Control**: Granular permissions
- **Audit Logging**: Complete operation history
- **Scheduled Operations**: Automated backups and maintenance
- **Rollback Support**: Automatic recovery on failures
- **Multi-Environment**: Manage dev, staging, and production

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    KOLLA-CONTROL WEB UI                      │
│         (React 18 + TypeScript + Tailwind CSS)               │
└────────────────┬────────────────────────────────────────────┘
                 │ REST API / WebSocket
┌────────────────▼────────────────────────────────────────────┐
│              KOLLA-CONTROL API BACKEND                       │
│         (FastAPI + Celery + Redis + PostgreSQL)              │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   Deployment │  │   Inventory  │  │   Monitoring │       │
│  │    Engine    │  │   Manager    │  │    Engine    │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
└─────────┼──────────────────┼──────────────────┼───────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌──────────────────┐ ┌──────────────┐ ┌────────────────┐
│ Kolla-Ansible    │ │   Foreman    │ │  Prometheus/   │
│  CLI Wrapper     │ │   REST API   │ │   Grafana      │
└──────────────────┘ └──────────────┘ └────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (for development)

### Development Setup

```bash
# Clone and navigate to the project
cd kolla-ansible/kolla-control

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head

# Start backend services
docker-compose up -d postgres redis
uvicorn app.main:app --reload

# Frontend setup (in another terminal)
cd ../frontend
npm install
npm run dev
```

Visit http://localhost:5173 for the UI and http://localhost:8000/docs for API documentation.

### Production Deployment

```bash
# Build and deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Or deploy to Kubernetes
kubectl apply -f kubernetes/
```

---

## 📚 Documentation

- [Installation Guide](docs/installation.md)
- [API Documentation](docs/api.md) - Also available at `/docs` endpoint
- [Foreman Integration](docs/foreman-integration.md)
- [Configuration Guide](docs/configuration.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Contributing](docs/contributing.md)

---

## Tech Stack

### Backend
- **FastAPI 0.115**: Modern Python async web framework
- **SQLAlchemy 2.0**: Async ORM with aiomysql
- **MariaDB 11.6**: Primary database
- **Redis 7**: Cache and Celery broker
- **Celery 5.4**: Distributed task queue
- **Pydantic 2.10**: Data validation
- **Alembic**: Database migrations
- **Python 3.13**: Latest Python version

### Frontend
- **React 19**: UI library (latest)
- **TypeScript 5.7**: Type safety
- **Vite 6.0**: Build tool
- **Tailwind CSS**: Styling
- **React Query**: Data fetching
- **Zustand**: State management
- **Socket.IO**: WebSocket client
- **Monaco Editor**: Code editor
- **Node.js 24**: Latest LTS

---

## 📖 API Overview

### Deployments
```bash
POST   /api/v1/deployments/            # Create deployment
GET    /api/v1/deployments/            # List deployments
POST   /api/v1/deployments/{id}/deploy    # Execute deploy
GET    /api/v1/deployments/{id}/logs      # Stream logs (WebSocket)
```

### Inventory
```bash
GET    /api/v1/inventory/              # Get inventory
POST   /api/v1/inventory/hosts/        # Add host
POST   /api/v1/inventory/sync-foreman  # Sync from Foreman
```

### Operations
```bash
POST   /api/v1/operations/prechecks    # Run prechecks
POST   /api/v1/operations/upgrade      # Upgrade OpenStack
POST   /api/v1/operations/backup       # MariaDB backup
```

See full API documentation at `/docs` when running the backend.

---

## 🔐 Security

- JWT-based authentication
- Role-based access control (RBAC)
- API rate limiting
- HTTPS/TLS support
- Secure credential storage
- Audit logging

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm run test
npm run test:coverage
```

---

## 📊 Project Status

**Current Phase**: Initial Development (v0.1.0-alpha)

### Roadmap

- [x] Project architecture and structure
- [ ] Backend API core endpoints
- [ ] Frontend basic UI components
- [ ] Kolla-Ansible CLI wrapper
- [ ] WebSocket log streaming
- [ ] Foreman integration
- [ ] Authentication & RBAC
- [ ] Testing suite
- [ ] Documentation
- [ ] Production Docker images
- [ ] CI/CD pipeline

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](docs/contributing.md).

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](../LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Kolla-Ansible](https://github.com/openstack/kolla-ansible) - The foundation
- [OpenStack](https://www.openstack.org/) - The platform
- [Foreman](https://theforeman.org/) - Provisioning integration

---

## 📞 Support

- GitHub Issues: [Report bugs or request features](https://github.com/rasty94/kolla-ansible/issues)
- Documentation: [Read the docs](docs/)
- Community: Join our discussions

---

**Made with ❤️ for the OpenStack community**
