"""
Configuration file management endpoints
"""
import os
from pathlib import Path
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.schemas import Message
import yaml
import json

router = APIRouter()


@router.get("/config/{config_type}")
async def get_config_file(config_type: str) -> Dict[str, Any]:
    """
    Get configuration file content

    Args:
        config_type: Type of config file (globals, passwords, inventory, multinode)
    """
    config_paths = {
        "globals": f"{settings.KOLLA_CONFIG_PATH}/globals.yml",
        "passwords": f"{settings.KOLLA_CONFIG_PATH}/passwords.yml",
        "inventory": f"{settings.ANSIBLE_INVENTORY_PATH}/inventory.ini",
        "multinode": f"{settings.KOLLA_CONFIG_PATH}/config/multinode",
    }

    if config_type not in config_paths:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported config type: {config_type}",
        )

    config_path = config_paths[config_type]

    if not os.path.exists(config_path):
        # Return default content for demo purposes
        if config_type == "globals":
            return {
                "id": "globals",
                "name": "globals.yml",
                "path": config_path,
                "content": """# Kolla Ansible globals.yml
global:
  kolla_base_distro: "ubuntu"
  kolla_install_type: "source"
  openstack_release: "2025.1"
  kolla_internal_vip_address: "10.0.0.10"
  kolla_external_vip_address: "192.168.1.10"
  network_interface: "eth0"
  neutron_external_interface: "eth1"

keystone:
  admin_password: "CHANGEME"

nova:
  libvirt_type: "kvm"

neutron:
  plugin: "ml2"
  type_drivers: "flat,vlan,vxlan"
  mechanism_drivers: "openvswitch,l2population"

cinder:
  volume_driver: "cinder.volume.drivers.lvm.LVMVolumeDriver"
  volume_group: "cinder-volumes"

glance:
  default_store: "file"

horizon:
  listen_port: "80"
""",
                "lastModified": "2025-01-01T00:00:00Z",
                "size": 1024
            }
        elif config_type == "passwords":
            return {
                "id": "passwords",
                "name": "passwords.yml",
                "path": config_path,
                "content": """# Kolla Ansible passwords.yml
# This file contains auto-generated passwords for OpenStack services
# DO NOT MODIFY MANUALLY - Use kolla-ansible passwords command instead

keystone_admin_password: "CHANGEME"
database_password: "CHANGEME"
rabbitmq_password: "CHANGEME"
""",
                "lastModified": "2025-01-01T00:00:00Z",
                "size": 512
            }
        elif config_type == "inventory":
            return {
                "id": "inventory",
                "name": "inventory.ini",
                "path": config_path,
                "content": """# Kolla Ansible inventory.ini
[control]
localhost ansible_connection=local

[network]
localhost ansible_connection=local

[compute]
# Add compute nodes here

[monitoring]
localhost ansible_connection=local

[storage]
localhost ansible_connection=local
""",
                "lastModified": "2025-01-01T00:00:00Z",
                "size": 256
            }
        else:
            return {
                "id": "multinode",
                "name": "multinode",
                "path": config_path,
                "content": "# Multinode configuration\n# Add your multinode settings here\n",
                "lastModified": "2025-01-01T00:00:00Z",
                "size": 128
            }

    try:
        # Read actual file
        with open(config_path, 'r') as f:
            content = f.read()

        stat = os.stat(config_path)

        return {
            "id": config_type,
            "name": os.path.basename(config_path),
            "path": config_path,
            "content": content,
            "lastModified": stat.st_mtime.isoformat(),
            "size": stat.st_size
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading config file: {str(e)}",
        )


@router.put("/config/{config_type}", response_model=Message)
async def update_config_file(
    config_type: str,
    data: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
):
    """
    Update configuration file content

    Args:
        config_type: Type of config file
        data: Configuration data with 'content' field
    """
    config_paths = {
        "globals": f"{settings.KOLLA_CONFIG_PATH}/globals.yml",
        "passwords": f"{settings.KOLLA_CONFIG_PATH}/passwords.yml",
        "inventory": f"{settings.ANSIBLE_INVENTORY_PATH}/inventory.ini",
        "multinode": f"{settings.KOLLA_CONFIG_PATH}/config/multinode",
    }

    if config_type not in config_paths:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported config type: {config_type}",
        )

    config_path = config_paths[config_type]
    content = data.get("content", "")

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content is required",
        )

    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        # Write file
        with open(config_path, 'w') as f:
            f.write(content)

        return Message(message=f"Configuration file {config_type} updated successfully")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error writing config file: {str(e)}",
        )


@router.get("/config/{config_type}/download")
async def download_config_file(config_type: str):
    """
    Download configuration file

    Args:
        config_type: Type of config file
    """
    config_paths = {
        "globals": f"{settings.KOLLA_CONFIG_PATH}/globals.yml",
        "passwords": f"{settings.KOLLA_CONFIG_PATH}/passwords.yml",
        "inventory": f"{settings.ANSIBLE_INVENTORY_PATH}/inventory.ini",
        "multinode": f"{settings.KOLLA_CONFIG_PATH}/config/multinode",
    }

    if config_type not in config_paths:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported config type: {config_type}",
        )

    config_path = config_paths[config_type]

    if not os.path.exists(config_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Configuration file {config_type} not found",
        )

    return FileResponse(
        path=config_path,
        filename=os.path.basename(config_path),
        media_type='application/octet-stream'
    )


@router.post("/config/validate/{config_type}", response_model=Message)
async def validate_config_file(config_type: str, data: Dict[str, Any]):
    """
    Validate configuration file content

    Args:
        config_type: Type of config file
        data: Configuration data with 'content' field
    """
    content = data.get("content", "")

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content is required for validation",
        )

    try:
        if config_type in ["globals", "passwords", "multinode"]:
            # Validate YAML
            yaml.safe_load(content)
            return Message(message="YAML syntax is valid")
        elif config_type == "inventory":
            # Basic INI validation - could be enhanced
            if "[" in content and "]" in content:
                return Message(message="INI syntax appears valid")
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid INI file format",
                )
        else:
            return Message(message="Config type not supported for validation")

    except yaml.YAMLError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid YAML syntax: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation error: {str(e)}",
        )