"""
Kolla-Ansible CLI wrapper service

This module provides a Python interface to execute Kolla-Ansible commands
and capture their output in real-time.
"""
import asyncio
import logging
from pathlib import Path
from typing import AsyncIterator, Dict, List, Optional, Callable
import subprocess

from app.core.config import settings
from app.models.models import OperationType

logger = logging.getLogger(__name__)


class KollaAnsibleError(Exception):
    """Exception raised when Kolla-Ansible command fails"""
    pass


class KollaAnsibleService:
    """Service to interact with Kolla-Ansible CLI"""
    
    def __init__(
        self,
        kolla_ansible_path: Optional[str] = None,
        config_path: Optional[str] = None,
        inventory_path: Optional[str] = None,
    ):
        self.kolla_ansible_path = kolla_ansible_path or settings.KOLLA_ANSIBLE_PATH
        self.config_path = config_path or settings.KOLLA_CONFIG_PATH
        self.inventory_path = inventory_path or settings.ANSIBLE_INVENTORY_PATH
        
        # Ensure paths exist
        Path(self.config_path).mkdir(parents=True, exist_ok=True)
    
    def _build_command(
        self,
        operation: OperationType,
        inventory: Optional[str] = None,
        extra_vars: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
        skip_tags: Optional[List[str]] = None,
        limit: Optional[str] = None,
        verbose: int = 0,
    ) -> List[str]:
        """
        Build kolla-ansible command
        
        Args:
            operation: Type of operation to perform
            inventory: Path to inventory file
            extra_vars: Extra variables to pass to Ansible
            tags: Ansible tags to run
            skip_tags: Ansible tags to skip
            limit: Limit execution to specific hosts
            verbose: Verbosity level (0-3)
        
        Returns:
            Command as list of strings
        """
        cmd = ["kolla-ansible", operation.value]
        
        # Add inventory
        if inventory:
            cmd.extend(["-i", inventory])
        elif self.inventory_path:
            cmd.extend(["-i", self.inventory_path])
        
        # Add extra vars
        if extra_vars:
            for key, value in extra_vars.items():
                cmd.extend(["-e", f"{key}={value}"])
        
        # Add tags
        if tags:
            cmd.extend(["--tags", ",".join(tags)])
        
        # Add skip tags
        if skip_tags:
            cmd.extend(["--skip-tags", ",".join(skip_tags)])
        
        # Add limit
        if limit:
            cmd.extend(["--limit", limit])
        
        # Add verbosity
        if verbose > 0:
            cmd.append("-" + "v" * min(verbose, 3))
        
        return cmd
    
    async def execute(
        self,
        operation: OperationType,
        inventory: Optional[str] = None,
        extra_vars: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
        skip_tags: Optional[List[str]] = None,
        limit: Optional[str] = None,
        verbose: int = 0,
        on_output: Optional[Callable[[str], None]] = None,
        environment_id: Optional[int] = None,
    ) -> Dict[str, any]:
        """
        Execute kolla-ansible command asynchronously
        
        Args:
            operation: Type of operation to perform
            inventory: Path to inventory file
            extra_vars: Extra variables to pass to Ansible
            tags: Ansible tags to run
            skip_tags: Ansible tags to skip
            limit: Limit execution to specific hosts
            verbose: Verbosity level (0-3)
            on_output: Callback function called for each output line
            environment_id: ID of the environment context
        
        Returns:
            Dictionary with return_code, stdout, stderr
        
        Raises:
            KollaAnsibleError: If command execution fails
        """
        # Determine paths based on environment
        config_path = self.config_path
        inventory_path = inventory or self.inventory_path
        
        if environment_id:
            # TODO: Fetch environment paths from DB or cache
            # For now, assuming a convention based on ID
            # In a real implementation, this service should have access to the DB or receive the paths directly
            pass

        cmd = self._build_command(
            operation=operation,
            inventory=inventory_path,
            extra_vars=extra_vars,
            tags=tags,
            skip_tags=skip_tags,
            limit=limit,
            verbose=verbose,
        )
        
        logger.info(f"Executing command: {' '.join(cmd)}")
        
        # Execute command
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self.kolla_ansible_path,
            env={
                **subprocess.os.environ,
                "KOLLA_CONFIG_PATH": config_path,
            },
        )
        
        stdout_lines = []
        stderr_lines = []
        
        async def read_stream(stream, is_stderr=False):
            """Read stream line by line"""
            while True:
                line = await stream.readline()
                if not line:
                    break
                
                line_str = line.decode('utf-8').rstrip()
                
                if is_stderr:
                    stderr_lines.append(line_str)
                else:
                    stdout_lines.append(line_str)
                
                # Call callback if provided
                if on_output:
                    await asyncio.to_thread(on_output, line_str)
                
                logger.debug(f"{'STDERR' if is_stderr else 'STDOUT'}: {line_str}")
        
        # Read stdout and stderr concurrently
        await asyncio.gather(
            read_stream(process.stdout, is_stderr=False),
            read_stream(process.stderr, is_stderr=True),
        )
        
        # Wait for process to complete
        return_code = await process.wait()
        
        result = {
            "return_code": return_code,
            "stdout": "\n".join(stdout_lines),
            "stderr": "\n".join(stderr_lines),
            "success": return_code == 0,
        }
        
        if return_code != 0:
            logger.error(
                f"Command failed with return code {return_code}: {result['stderr']}"
            )
        
        return result
    
    async def stream_output(
        self,
        operation: OperationType,
        inventory: Optional[str] = None,
        extra_vars: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
        skip_tags: Optional[List[str]] = None,
        limit: Optional[str] = None,
        verbose: int = 0,
    ) -> AsyncIterator[str]:
        """
        Execute command and stream output line by line (for WebSocket)
        
        Args:
            operation: Type of operation to perform
            inventory: Path to inventory file
            extra_vars: Extra variables
            tags: Ansible tags to run
            skip_tags: Ansible tags to skip
            limit: Limit execution to specific hosts
            verbose: Verbosity level
        
        Yields:
            Lines of output from the command
        """
        cmd = self._build_command(
            operation=operation,
            inventory=inventory,
            extra_vars=extra_vars,
            tags=tags,
            skip_tags=skip_tags,
            limit=limit,
            verbose=verbose,
        )
        
        logger.info(f"Streaming command: {' '.join(cmd)}")
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,  # Merge stderr into stdout
            cwd=self.kolla_ansible_path,
            env={
                **subprocess.os.environ,
                "KOLLA_CONFIG_PATH": self.config_path,
            },
        )
        
        # Stream output line by line
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            
            line_str = line.decode('utf-8').rstrip()
            yield line_str
        
        # Wait for process to complete
        return_code = await process.wait()
        
        # Yield final status
        yield f"\n--- Command completed with return code {return_code} ---"
        
        if return_code != 0:
            raise KollaAnsibleError(
                f"Command failed with return code {return_code}"
            )
    
    async def prechecks(
        self,
        inventory: Optional[str] = None,
        limit: Optional[str] = None,
    ) -> Dict[str, any]:
        """Run prechecks"""
        return await self.execute(
            operation=OperationType.PRECHECKS,
            inventory=inventory,
            limit=limit,
        )
    
    async def deploy(
        self,
        inventory: Optional[str] = None,
        limit: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, any]:
        """Deploy OpenStack"""
        return await self.execute(
            operation=OperationType.DEPLOY,
            inventory=inventory,
            limit=limit,
            tags=tags,
        )
    
    async def upgrade(
        self,
        inventory: Optional[str] = None,
        limit: Optional[str] = None,
    ) -> Dict[str, any]:
        """Upgrade OpenStack"""
        return await self.execute(
            operation=OperationType.UPGRADE,
            inventory=inventory,
            limit=limit,
        )
    
    async def reconfigure(
        self,
        inventory: Optional[str] = None,
        limit: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, any]:
        """Reconfigure OpenStack services"""
        return await self.execute(
            operation=OperationType.RECONFIGURE,
            inventory=inventory,
            limit=limit,
            tags=tags,
        )
    
    async def pull_images(
        self,
        inventory: Optional[str] = None,
        limit: Optional[str] = None,
    ) -> Dict[str, any]:
        """Pull container images"""
        return await self.execute(
            operation=OperationType.PULL,
            inventory=inventory,
            limit=limit,
        )
    
    async def backup(
        self,
        inventory: Optional[str] = None,
    ) -> Dict[str, any]:
        """Backup MariaDB"""
        return await self.execute(
            operation=OperationType.BACKUP,
            inventory=inventory,
        )


# Create singleton instance
kolla_ansible_service = KollaAnsibleService()
