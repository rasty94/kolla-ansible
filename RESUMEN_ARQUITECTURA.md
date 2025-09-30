# Kolla Ansible - Resumen de Arquitectura y Funcionamiento

## Descripción General

**Kolla Ansible** es un proyecto de OpenStack que permite desplegar servicios de OpenStack e infraestructura en contenedores Docker/Podman utilizando Ansible como motor de automatización. El proyecto está separado del proyecto Kolla principal y se enfoca específicamente en la orquestación del despliegue.

### Misión del Proyecto
> "Proporcionar contenedores listos para producción y herramientas de despliegue para operar nubes OpenStack."

Kolla es altamente especializado por defecto, pero permite personalización completa, permitiendo a operadores con poca experiencia desplegar OpenStack rápidamente.

## Arquitectura del Proyecto

### Estructura de Directorios

```
kolla-ansible/
├── ansible/                    # Playbooks y roles de Ansible
│   ├── *.yml                  # Playbooks principales (site.yml, etc.)
│   ├── roles/                 # Roles de servicios OpenStack
│   ├── group_vars/            # Variables de configuración
│   └── inventory/             # Inventarios de ejemplo
├── kolla_ansible/             # Código Python principal
│   ├── cli/                   # Interfaz de línea de comandos
│   ├── cmd/                   # Comandos ejecutables
│   └── *.py                   # Módulos utilitarios
├── etc/                       # Configuraciones de ejemplo
├── tools/                     # Herramientas auxiliares
├── tests/                     # Tests funcionales
├── doc/                       # Documentación
├── contrib/                   # Contribuciones y demos
└── specs/                     # Especificaciones técnicas
```

### Componentes Principales

#### 1. Interfaz de Línea de Comandos (CLI)
- **Punto de entrada**: `kolla-ansible` comando principal
- **Arquitectura**: Utiliza `cliff` (OpenStack CLI framework)
- **Comandos disponibles** (setup.cfg):
  - `deploy`: Despliega OpenStack
  - `reconfigure`: Reconfigura servicios
  - `upgrade`: Actualiza servicios
  - `destroy`: Elimina el despliegue
  - `bootstrap-servers`: Prepara servidores
  - `prechecks`: Verificaciones pre-despliegue
  - `post-deploy`: Configuración post-despliegue

#### 2. Motor de Ansible
- **Playbook principal**: `ansible/site.yml`
- **Estrategia de ejecución**: Agrupa hosts por configuración y servicios habilitados
- **Roles modulares**: Cada servicio OpenStack tiene su propio rol

#### 3. Gestión de Configuración
- **Archivo principal**: `globals.yml` (`/etc/kolla/globals.yml`)
- **Variables por defecto**: `ansible/group_vars/all.yml`
- **Configuración personalizada**: `node_custom_config` directory
- **Estrategias de configuración**: `COPY_ONCE` o `COPY_ALWAYS`

## Servicios Soportados

### Servicios Core de OpenStack
- **Identity**: Keystone
- **Compute**: Nova, Nova-cell
- **Networking**: Neutron, OVN, Kuryr
- **Storage**: Cinder, Glance, Swift
- **Orchestration**: Heat
- **Dashboard**: Horizon

### Servicios Avanzados
- **Telemetry**: Ceilometer, Aodh, Gnocchi
- **Bare Metal**: Ironic, Bifrost
- **Container**: Zun, Magnum
- **Database**: Trove
- **DNS**: Designate
- **Key Management**: Barbican
- **NFV**: Tacker
- **Orchestration**: Mistral

### Componentes de Infraestructura
- **Load Balancing**: HAProxy, Keepalived
- **Databases**: MariaDB, Redis
- **Message Queue**: RabbitMQ
- **Monitoring**: Prometheus, Grafana, Collectd
- **Logging**: OpenSearch, Fluentd
- **Caching**: Memcached

## Arquitectura de Despliegue

### Tipos de Despliegue

1. **All-in-One (AIO)**
   - Todos los servicios en un solo host
   - Ideal para desarrollo y testing
   - Inventario: `ansible/inventory/all-in-one`

2. **Multi-nodo**
   - Servicios distribuidos en múltiples hosts
   - Separación por roles: control, compute, network, storage
   - Inventario: `ansible/inventory/multinode`

### Flujo de Despliegue

1. **Bootstrap Servers** (`bootstrap-servers`)
   - Instala dependencias del sistema
   - Configura Docker/Podman
   - Prepara el entorno

2. **Prechecks** (`prechecks`)
   - Verifica requisitos del sistema
   - Valida configuración
   - Comprueba conectividad

3. **Deploy** (`deploy`)
   - Despliega contenedores
   - Configura servicios
   - Establece conectividad entre servicios

4. **Post-deploy** (`post-deploy`)
   - Crea recursos iniciales
   - Configura endpoints
   - Genera archivos de credenciales

### Gestión de Contenedores

- **Engine soportados**: Docker, Podman
- **Registro de imágenes**: Configurable (Docker Hub, Quay.io, privado)
- **Distribuciones base**: CentOS Stream, Debian, Rocky, Ubuntu
- **Arquitecturas**: x86_64, aarch64
- **Estrategia de actualización**: Rolling updates

## Configuración y Personalización

### Archivo globals.yml
```yaml
# Configuración básica
kolla_base_distro: "rocky"
kolla_container_engine: "docker"
openstack_release: "master"

# Networking
kolla_internal_vip_address: "10.10.10.254"
network_interface: "eth0"
neutron_external_interface: "eth1"

# Habilitación de servicios
enable_cinder: "yes"
enable_heat: "yes"
enable_horizon: "yes"
```

### Personalización de Configuración
- **Templates Jinja2**: Para generación dinámica de configuración
- **Hooks personalizados**: Pre/post tasks por servicio
- **Override de variables**: Por grupo, por host, por servicio

## Herramientas de Gestión

### Gestión de Contraseñas
- `kolla-genpwd`: Genera contraseñas aleatorias
- `kolla-mergepwd`: Combina archivos de contraseñas
- `kolla-writepwd`: Escribe contraseñas
- `kolla-readpwd`: Lee contraseñas

### Herramientas de Mantenimiento
- `cleanup-containers`: Limpia contenedores
- `cleanup-host`: Limpia configuración del host
- `cleanup-images`: Limpia imágenes no utilizadas
- `prune-images`: Elimina imágenes huérfanas

## Alta Disponibilidad

### Componentes HA
- **HAProxy**: Load balancing para APIs
- **Keepalived**: VIP management
- **Galera**: Cluster de MariaDB
- **RabbitMQ**: Clustering nativo

### Estrategias de Resilencia
- **Health checks**: Verificación continua de servicios
- **Automatic restart**: Reinicio automático de contenedores fallidos
- **Rolling updates**: Actualizaciones sin interrupción
- **Backup/Recovery**: Procedimientos automatizados

## Monitoreo y Logging

### Stack de Monitoreo
- **Prometheus**: Métricas
- **Grafana**: Visualización
- **Collectd/Telegraf**: Recolección de métricas

### Stack de Logging
- **OpenSearch**: Indexación y búsqueda
- **Fluentd**: Agregación de logs
- **OpenSearch Dashboards**: Visualización de logs

## Integración y Extensibilidad

### APIs y Interfaces
- **OpenStack APIs**: Exposición estándar de todas las APIs
- **Ansible API**: Extensión mediante roles personalizados
- **Plugin system**: Filtros y módulos personalizados

### Integración con Ecosystem
- **Kayobe**: Despliegue en bare metal
- **Kolla**: Construcción de imágenes
- **Bifrost**: Provisioning de bare metal
- **Tenks**: Testing de bare metal virtualizado

## Seguridad

### TLS/SSL
- **Certificados automáticos**: Let's Encrypt integration
- **CA personalizada**: Soporte para certificados propios
- **Endpoints seguros**: HTTPS para todas las APIs

### Autenticación y Autorización
- **Keystone**: Identity management
- **RBAC**: Role-based access control
- **External auth**: LDAP, AD integration

## Testing y CI/CD

### Testing Framework
- **Functional tests**: Tests end-to-end
- **Gate jobs**: Zuul CI/CD pipeline
- **ARA**: Ansible Run Analysis
- **Deployment scenarios**: Multiple test environments

### Validación
- **Syntax checking**: YAML y Python linting
- **Configuration validation**: Pre-deployment checks
- **Service verification**: Post-deployment testing

## Consideraciones de Producción

### Requisitos del Sistema
- **OS soportados**: CentOS Stream, Rocky, Ubuntu, Debian
- **Python**: >= 3.10
- **Ansible**: >= 2.17, < 2.19
- **Container engine**: Docker o Podman

### Escalabilidad
- **Horizontal scaling**: Múltiples nodos por servicio
- **Service separation**: Aislamiento por tipo de servicio
- **Resource constraints**: Límites de CPU/memoria por contenedor

### Backup y Disaster Recovery
- **Database backup**: MariaDB automated backups
- **Configuration backup**: Ansible-based configuration snapshots
- **Recovery procedures**: Automated restoration workflows

Este resumen proporciona una visión completa de la arquitectura y funcionamiento de Kolla Ansible, desde sus componentes básicos hasta consideraciones avanzadas de producción.