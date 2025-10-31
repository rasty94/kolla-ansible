# Kolla-Control - Quick Start Guide

## 🚀 Getting Started

This guide will help you get Kolla-Control up and running in development mode.

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL 15+ (or use Docker Compose)
- Redis 7+ (or use Docker Compose)
- Docker & Docker Compose (recommended)

---

## Option 1: Docker Compose (Recommended)

### 1. Clone and Setup

```bash
cd kolla-ansible/kolla-control
cp backend/.env.example backend/.env
```

### 2. Edit Configuration

Edit `backend/.env` and set your SECRET_KEY:

```bash
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
sed -i "s/your-secret-key-change-this-in-production/$SECRET_KEY/" backend/.env
```

### 3. Start Services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Backend API (port 8000)
- Celery Worker
- Flower (Celery UI - port 5555)
- Frontend (port 5173)

### 4. Initialize Database

```bash
docker-compose exec backend alembic upgrade head
```

### 5. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API Docs**: http://localhost:8000/docs
- **Flower (Celery)**: http://localhost:5555

---

## Option 2: Manual Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env and configure your settings

# Start PostgreSQL and Redis (manual or Docker)
docker run -d --name postgres -p 5432:5432 \
  -e POSTGRES_USER=kolla_control \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=kolla_control \
  postgres:15-alpine

docker run -d --name redis -p 6379:6379 redis:7-alpine

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload

# In another terminal, start Celery worker
celery -A app.tasks.celery_app worker --loglevel=info
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

---

## 📝 Configuration

### Backend Environment Variables

Key variables in `.env`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://kolla_control:password@localhost:5432/kolla_control

# Redis
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/1

# Security
SECRET_KEY=your-secret-key-here

# Kolla-Ansible Paths
KOLLA_ANSIBLE_PATH=/usr/local/share/kolla-ansible
KOLLA_CONFIG_PATH=/etc/kolla
ANSIBLE_INVENTORY_PATH=/etc/kolla/inventory

# Foreman (optional)
FOREMAN_ENABLED=false
FOREMAN_URL=https://foreman.example.com
```

---

## 🔧 Development Workflow

### Database Migrations

```bash
# Create a new migration
cd backend
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1
```

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm run test
```

### Code Quality

```bash
# Backend
cd backend
black app/
ruff check app/
mypy app/

# Frontend
cd frontend
npm run lint
npm run format
```

---

## 🎯 First Steps

### 1. Create a Deployment

```bash
curl -X POST http://localhost:8000/api/v1/deployments/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "production",
    "description": "Production OpenStack deployment",
    "globals_config": {
      "kolla_base_distro": "ubuntu",
      "openstack_release": "2025.1"
    },
    "inventory_config": {
      "control": ["controller1.example.com"],
      "compute": ["compute1.example.com"]
    }
  }'
```

### 2. Add Hosts to Inventory

```bash
curl -X POST http://localhost:8000/api/v1/inventory/hosts \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "controller1.example.com",
    "ip_address": "192.168.1.10",
    "groups": ["control", "network", "monitoring"]
  }'
```

### 3. Run Prechecks

```bash
curl -X POST http://localhost:8000/api/v1/operations/prechecks \
  -H "Content-Type: application/json" \
  -d '{"inventory_path": "/etc/kolla/inventory/multinode"}'
```

---

## 📚 API Documentation

Once the backend is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Test connection
psql postgresql://kolla_control:password@localhost:5432/kolla_control -c "SELECT 1"
```

### Redis Connection Issues

```bash
# Check Redis is running
docker ps | grep redis

# Test connection
redis-cli ping
```

### Backend Startup Issues

```bash
# Check logs
docker-compose logs -f backend

# Or manually
tail -f /var/log/kolla-control/app.log
```

### Frontend Build Issues

```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

## 🔐 Security Notes

**⚠️ IMPORTANT FOR PRODUCTION:**

1. Change `SECRET_KEY` to a strong random value
2. Use strong database passwords
3. Enable HTTPS/TLS
4. Configure firewall rules
5. Use environment-specific `.env` files
6. Never commit `.env` files to git

---

## 📞 Getting Help

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/rasty94/kolla-ansible/issues)
- **API Reference**: http://localhost:8000/docs

---

## 🎉 Next Steps

- [ ] Configure Foreman integration
- [ ] Set up Prometheus/Grafana
- [ ] Configure authentication (Keystone/LDAP)
- [ ] Create deployment templates
- [ ] Set up scheduled backups
- [ ] Configure monitoring alerts

Enjoy using Kolla-Control! 🚀
