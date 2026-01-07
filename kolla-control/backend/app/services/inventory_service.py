"""
Inventory Service
Handles parsing and generation of Ansible inventory files
"""
import configparser
from typing import List, Dict, Any
import logging
from pathlib import Path

from app.models import Host
from app.core.config import settings

logger = logging.getLogger(__name__)

class InventoryService:
    def __init__(self, inventory_path: str = None):
        self.inventory_path = inventory_path or settings.ANSIBLE_INVENTORY_PATH

    def generate_inventory_file(self, hosts: List[Host]) -> str:
        """
        Generate Ansible inventory file content from list of hosts
        """
        config = configparser.ConfigParser(allow_no_value=True)
        
        # Group hosts by their roles/groups
        groups: Dict[str, List[Host]] = {}
        
        # Initialize default groups
        default_groups = ['control', 'network', 'compute', 'storage', 'monitoring']
        for group in default_groups:
            groups[group] = []
            
        for host in hosts:
            if not host.is_active:
                continue
                
            # Add to specific groups
            for role in host.groups:
                if role not in groups:
                    groups[role] = []
                groups[role].append(host)
        
        # Create sections
        for group_name, group_hosts in groups.items():
            config.add_section(group_name)
            for host in group_hosts:
                # Format: hostname ansible_host=ip ansible_user=user ...
                line = f"{host.hostname} ansible_host={host.ip_address} ansible_user={host.ansible_user}"
                if host.ansible_port != 22:
                    line += f" ansible_port={host.ansible_port}"
                if host.ansible_ssh_private_key_file:
                    line += f" ansible_ssh_private_key_file={host.ansible_ssh_private_key_file}"
                
                config.set(group_name, line)
                
        # Write to string
        import io
        output = io.StringIO()
        config.write(output)
        return output.getvalue()

    def save_inventory(self, hosts: List[Host]) -> None:
        """
        Save hosts to inventory file
        """
        content = self.generate_inventory_file(hosts)
        
        # Ensure directory exists
        Path(self.inventory_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.inventory_path, 'w') as f:
            f.write(content)
            
    def parse_inventory_file(self) -> List[Dict[str, Any]]:
        """
        Parse existing inventory file
        """
        if not Path(self.inventory_path).exists():
            return []
            
        config = configparser.ConfigParser(allow_no_value=True)
        config.read(self.inventory_path)
        
        parsed_hosts = {}
        
        for section in config.sections():
            for key in config[section]:
                # Parse line: hostname var1=val1 var2=val2
                parts = key.split()
                hostname = parts[0]
                
                if hostname not in parsed_hosts:
                    parsed_hosts[hostname] = {
                        "hostname": hostname,
                        "groups": set(),
                        "ip_address": "",
                        "ansible_user": "root",
                        "ansible_port": 22,
                        "ansible_ssh_private_key_file": None
                    }
                
                parsed_hosts[hostname]["groups"].add(section)
                
                # Parse vars
                for part in parts[1:]:
                    if "=" in part:
                        k, v = part.split("=", 1)
                        if k == "ansible_host":
                            parsed_hosts[hostname]["ip_address"] = v
                        elif k == "ansible_user":
                            parsed_hosts[hostname]["ansible_user"] = v
                        elif k == "ansible_port":
                            parsed_hosts[hostname]["ansible_port"] = int(v)
                        elif k == "ansible_ssh_private_key_file":
                            parsed_hosts[hostname]["ansible_ssh_private_key_file"] = v
                            
        # Convert sets to lists
        result = []
        for host in parsed_hosts.values():
            host["groups"] = list(host["groups"])
            result.append(host)
            
        return result

inventory_service = InventoryService()
