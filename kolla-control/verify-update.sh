#!/bin/bash

# Kolla-Control Update Verification Script
# Verifica que todas las actualizaciones se aplicaron correctamente

set -e

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  🔍 Kolla-Control - Verificación de Actualización        ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SUCCESS=0
FAILURES=0

check() {
    local name=$1
    local command=$2
    local expected=$3
    
    echo -n "Verificando $name... "
    
    result=$(eval "$command" 2>/dev/null || echo "ERROR")
    
    if [[ "$result" == *"$expected"* ]]; then
        echo -e "${GREEN}✅ OK${NC}"
        ((SUCCESS++))
    else
        echo -e "${RED}❌ FALLO${NC}"
        echo "   Esperado: $expected"
        echo "   Obtenido: $result"
        ((FAILURES++))
    fi
}

echo "📦 Backend (Python)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check "FastAPI 0.115.5" "grep 'fastapi==' backend/requirements.txt" "fastapi==0.115.5"
check "Pydantic 2.10.0" "grep 'pydantic==' backend/requirements.txt" "pydantic==2.10.0"
check "SQLAlchemy 2.0.36" "grep 'sqlalchemy==' backend/requirements.txt" "sqlalchemy==2.0.36"
check "aiomysql driver" "grep 'aiomysql' backend/requirements.txt" "aiomysql==0.2.0"
check "Redis 5.2.0" "grep 'redis==' backend/requirements.txt" "redis==5.2.0"
check "Alembic 1.14.0" "grep 'alembic==' backend/requirements.txt" "alembic==1.14.0"

echo ""
check "No asyncpg" "grep -c 'asyncpg' backend/requirements.txt" "0"
check "No psycopg2" "grep -c 'psycopg2' backend/requirements.txt" "0"

echo ""
echo "🎨 Frontend (React)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check "React 19.0.0" "grep '\"react\":' frontend/package.json" "19.0.0"
check "React DOM 19.0.0" "grep '\"react-dom\":' frontend/package.json" "19.0.0"
check "React Router 7.0.0" "grep '\"react-router-dom\":' frontend/package.json" "7.0.0"
check "TypeScript 5.7.2" "grep '\"typescript\":' frontend/package.json" "5.7.2"
check "Vite 6.0.1" "grep '\"vite\":' frontend/package.json" "6.0.1"
check "React Query 5.59" "grep '\"@tanstack/react-query\":' frontend/package.json" "5.59"

echo ""
check "Node >= 24" "grep '\"node\":' frontend/package.json" "24.0.0"

echo ""
echo "🗄️  Base de Datos (MariaDB)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check "MariaDB imagen" "grep 'image: mariadb' docker-compose.yml" "mariadb:11.6"
check "MariaDB port 3306" "grep '3306:3306' docker-compose.yml" "3306:3306"
check "MySQL variables" "grep 'MYSQL_DATABASE' docker-compose.yml" "MYSQL_DATABASE"
check "UTF8mb4 charset" "grep 'utf8mb4' docker-compose.yml" "utf8mb4"
check "MariaDB volume" "grep 'mariadb_data' docker-compose.yml" "mariadb_data"

echo ""
check "No PostgreSQL" "grep -c 'postgres:' docker-compose.yml" "0"
check "No postgres_data" "grep -c 'postgres_data:' docker-compose.yml" "0"

echo ""
echo "🐳 Docker Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check "Backend Python 3.13" "grep 'FROM python' docker/backend.Dockerfile" "python:3.13-slim"
check "Frontend Node 24" "grep 'FROM node' docker/frontend.Dockerfile" "node:24-alpine"
check "MySQL lib (backend)" "grep 'libmysqlclient' docker/backend.Dockerfile" "libmysqlclient"

echo ""
echo "🔧 Configuración"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check "DATABASE_URL MariaDB" "grep 'DATABASE_URL=' backend/.env.example" "mysql+aiomysql"
check "DB Port 3306" "grep 'DATABASE_URL=' backend/.env.example" "3306"
check "aiomysql driver" "grep 'DATABASE_URL=' docker-compose.yml" "mysql+aiomysql"

echo ""
echo "📚 Documentación"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check "README.md actualizado" "grep 'MariaDB 11.6' README.md" "MariaDB 11.6"
check "README.md React 19" "grep 'React 19' README.md" "React 19"
check "README.md Python 3.13" "grep 'Python 3.13' README.md" "Python 3.13"
check "CHANGELOG.md existe" "test -f CHANGELOG.md && echo 'exists'" "exists"
check "UPGRADE_GUIDE.md existe" "test -f UPGRADE_GUIDE.md && echo 'exists'" "exists"
check "UPDATE_SUMMARY.md existe" "test -f UPDATE_SUMMARY.md && echo 'exists'" "exists"

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                    RESUMEN FINAL                          ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

TOTAL=$((SUCCESS + FAILURES))
PERCENTAGE=$((SUCCESS * 100 / TOTAL))

echo "Total de verificaciones: $TOTAL"
echo -e "✅ Exitosas: ${GREEN}$SUCCESS${NC}"
echo -e "❌ Fallidas:  ${RED}$FAILURES${NC}"
echo ""
echo "Porcentaje de éxito: $PERCENTAGE%"
echo ""

if [ $FAILURES -eq 0 ]; then
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  🎉 ¡ACTUALIZACIÓN VERIFICADA EXITOSAMENTE!              ║${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}║  ✅ Python 3.13                                          ║${NC}"
    echo -e "${GREEN}║  ✅ React 19                                             ║${NC}"
    echo -e "${GREEN}║  ✅ Node.js 24                                           ║${NC}"
    echo -e "${GREEN}║  ✅ MariaDB 11.6                                         ║${NC}"
    echo -e "${GREEN}║                                                           ║${NC}"
    echo -e "${GREEN}║  Todas las verificaciones pasaron correctamente.         ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Próximos pasos:"
    echo "  1. Probar el stack: docker-compose up -d --build"
    echo "  2. Verificar logs: docker-compose logs -f"
    echo "  3. Ejecutar migraciones: docker-compose exec backend alembic upgrade head"
    echo "  4. Acceder a la API: http://localhost:8000/docs"
    exit 0
else
    echo -e "${RED}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ⚠️  ALGUNAS VERIFICACIONES FALLARON                     ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Por favor revisa los errores arriba y ejecuta el script de nuevo."
    exit 1
fi
