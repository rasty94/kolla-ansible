# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import sys

from cliff.command import Command

from kolla_ansible import ansible
from kolla_ansible import utils

# Serial is not recommended and disabled by default.
# Users can enable it by configuring the variable.
ANSIBLE_SERIAL = 0


def _get_playbook_path(playbook):
    """Return the absolute path of Kolla Ansible playbook"""
    return utils.get_data_files_path("ansible", "%s.yml" % playbook)


def _choose_playbooks(parsed_args, kolla_playbook="site"):
    """Return user defined playbook if set, otherwise return Kolla playbook"""
    if parsed_args.playbook:
        playbooks = parsed_args.playbook
    else:
        playbooks = [_get_playbook_path(kolla_playbook)]
    return playbooks


class KollaAnsibleMixin:
    """Mixin class for commands running Kolla Ansible."""

    def get_parser(self, prog_name):
        parser = super(KollaAnsibleMixin, self).get_parser(prog_name)
        ansible_group = parser.add_argument_group("Ansible arguments")
        ka_group = parser.add_argument_group("Kolla Ansible arguments")
        self.add_ansible_args(ansible_group)
        self.add_kolla_ansible_args(ka_group)
        return parser

    def add_kolla_ansible_args(self, group):
        ansible.add_kolla_ansible_args(group)

    def add_ansible_args(self, group):
        ansible.add_ansible_args(group)

    def _get_verbosity_args(self):
        """Add quietness and verbosity level arguments."""
        # Cliff's default verbosity level is 1, 0 means quiet.
        verbosity_args = {}
        if self.app.options.verbose_level:
            ansible_verbose_level = self.app.options.verbose_level - 1
            verbosity_args["verbose_level"] = ansible_verbose_level
        else:
            verbosity_args["quiet"] = True
        return verbosity_args

    def run_playbooks(self, parsed_args, *args, **kwargs):
        # If the user knows what they're doing and explicitly sets
        # ansible_python_interpreter, respect their choice and avoid
        # overriding it by kolla-ansible.
        extra = kwargs.get("extra_vars", {})
        for var in getattr(parsed_args, "extra_vars", []) or []:
            if var.startswith("ansible_python_interpreter="):
                extra.pop("ansible_python_interpreter", None)
                break
        kwargs.update(self._get_verbosity_args())
        return ansible.run_playbooks(parsed_args, *args, **kwargs)


class GatherFacts(KollaAnsibleMixin, Command):
    """Gather Ansible facts on hosts"""

    def take_action(self, parsed_args):
        self.app.LOG.info("Gathering Ansible facts")

        playbooks = _choose_playbooks(parsed_args, "gather-facts")

        self.run_playbooks(parsed_args, playbooks)


class InstallDeps(KollaAnsibleMixin, Command):
    """Install Ansible Galaxy dependencies"""

    def take_action(self, parsed_args):
        self.app.LOG.info("Installing Ansible Galaxy dependencies")
        ansible.install_galaxy_collections()


class Prechecks(KollaAnsibleMixin, Command):
    """Do pre-deployment checks for hosts"""

    def take_action(self, parsed_args):
        self.app.LOG.info("Pre-deployment checking")

        extra_vars = {}
        extra_vars["kolla_action"] = "precheck"

        playbooks = _choose_playbooks(parsed_args,)

        self.run_playbooks(parsed_args, playbooks, extra_vars=extra_vars)


class GenConfig(KollaAnsibleMixin, Command):
    """Generate configuration files for services. No container changes!"""

    def take_action(self, parsed_args):
        self.app.LOG.info(
            "Generate configuration files for enabled OpenStack services")

        extra_vars = {}
        extra_vars["kolla_action"] = "config"

        playbooks = _choose_playbooks(parsed_args)

        self.run_playbooks(parsed_args, playbooks, extra_vars=extra_vars)


class Reconfigure(KollaAnsibleMixin, Command):
    """Reconfigure enabled OpenStack service"""

    def take_action(self, parsed_args):
        self.app.LOG.info("Reconfigure OpenStack service")

        extra_vars = {}
        extra_vars["kolla_action"] = "reconfigure"
        extra_vars["kolla_serial"] = ANSIBLE_SERIAL

        playbooks = _choose_playbooks(parsed_args)

        self.run_playbooks(parsed_args, playbooks, extra_vars=extra_vars)


class ValidateConfig(KollaAnsibleMixin, Command):
    """Validate configuration files for enabled OpenStack services"""

    def take_action(self, parsed_args):
        self.app.LOG.info("Validate configuration files for enabled "
                          "OpenStack services")

        extra_vars = {}
        extra_vars["kolla_action"] = "config_validate"

        playbooks = _choose_playbooks(parsed_args)

        self.run_playbooks(parsed_args, playbooks, extra_vars=extra_vars)


class BootstrapServers(KollaAnsibleMixin, Command):
    """Bootstrap servers with Kolla Ansible deploy dependencies"""

    def take_action(self, parsed_args):
        self.app.LOG.info("Bootstrapping servers")

        extra_vars = {}
        extra_vars["kolla_action"] = "bootstrap-servers"
        extra_vars["ansible_python_interpreter"] = "auto_silent"

        playbooks = _choose_playbooks(parsed_args, "kolla-host")

        self.run_playbooks(parsed_args, playbooks, extra_vars=extra_vars)


class Pull(KollaAnsibleMixin, Command):
    """Pull all images for containers. Only pulls, no container changes."""

    def take_action(self, parsed_args):
        self.app.LOG.info("Pulling Docker images")

        extra_vars = {}
        extra_vars["kolla_action"] = "pull"

        playbooks = _choose_playbooks(parsed_args)

        self.run_playbooks(parsed_args, playbooks, extra_vars=extra_vars)


class Certificates(KollaAnsibleMixin, Command):
    """Generate self-signed certificate for TLS *For Development Only*"""

    def take_action(self, parsed_args):
        self.app.LOG.info("Generate TLS Certificates")

        playbooks = _choose_playbooks(parsed_args, "certificates")

        self.run_playbooks(parsed_args, playbooks)


class OctaviaCertificates(KollaAnsibleMixin, Command):
    """Generate certificates for octavia deployment"""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        group = parser.add_argument_group("Octavia certificates action")
        group.add_argument(
            "--check-expiry",
            type=int,
            help="Check if the certificates will expire "
                 "within given number of days",
        )
        return parser

    def take_action(self, parsed_args):
        extra_vars = {
            "ansible_python_interpreter": sys.executable
        }

        if hasattr(parsed_args, "check_expiry") \
                and parsed_args.check_expiry is not None:
            self.app.LOG.info("Checking if certificates expire "
                              "within given number of days.")
            extra_vars["octavia_certs_check_expiry"] = "yes"
            extra_vars["octavia_certs_expiry_limit"] = parsed_args.check_expiry
        else:
            self.app.LOG.info("Generate octavia Certificates")

        playbooks = _choose_playbooks(parsed_args, "octavia-certificates")

        self.run_playbooks(parsed_args, playbooks, extra_vars=extra_vars)


class Deploy(KollaAnsibleMixin, Command):
    """Generate config, bootstrap and start all Kolla Ansible containers"""

    def take_action(self, parsed_args):
        self.app.LOG.info("Deploying Playbooks")

        extra_vars = {}
        extra_vars["kolla_action"] = "deploy"

        playbooks = _choose_playbooks(parsed_args)

        self.run_playbooks(parsed_args, playbooks, extra_vars=extra_vars)


class DeployContainers(KollaAnsibleMixin, Command):
    """Only deploy and start containers (no config updates or bootstrapping)"""

    def take_action(self, parsed_args):
        self.app.LOG.info("Deploying Containers")

        extra_vars = {}
        extra_vars["kolla_action"] = "deploy-containers"

        playbooks = _choose_playbooks(parsed_args)

        self.run_playbooks(parsed_args, playbooks, extra_vars=extra_vars)


class Postdeploy(KollaAnsibleMixin, Command):
    """Do post deploy on deploy node"""

    def take_action(self, parsed_args):
        self.app.LOG.info("Post-Deploying Playbooks")

        playbooks = _choose_playbooks(parsed_args, "post-deploy")

        self.run_playbooks(parsed_args, playbooks)


class Upgrade(KollaAnsibleMixin, Command):
    """Upgrades existing OpenStack Environment"""

    def take_action(self, parsed_args):
        self.app.LOG.info("Upgrading OpenStack Environment")

        extra_vars = {}
        extra_vars["kolla_action"] = "upgrade"
        extra_vars["kolla_serial"] = ANSIBLE_SERIAL

        playbooks = _choose_playbooks(parsed_args)

        self.run_playbooks(parsed_args, playbooks, extra_vars=extra_vars)


class Stop(KollaAnsibleMixin, Command):
    """Stop Kolla Ansible containers"""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        group = parser.add_argument_group("Stop action")
        group.add_argument(
            "--yes-i-really-really-mean-it",
            action="store_true",
            required=True,
            help="WARNING! This action will remove the Openstack deployment!",
        )
        group.add_argument(
            "--ignore-missing",
            action="store_true",
            help="Don't fail if there are missing containers"
        )
        return parser

    def take_action(self, parsed_args):
        self.app.LOG.info("Stop Kolla containers")

        extra_vars = {}
        extra_vars["kolla_action"] = "stop"
        extra_vars["kolla_action_stop_ignore_missing"] = (
            "yes" if parsed_args.ignore_missing else "no"
        )

        playbooks = _choose_playbooks(parsed_args)

        self.run_playbooks(parsed_args, playbooks, extra_vars=extra_vars)


class Destroy(KollaAnsibleMixin, Command):
    """Destroy Kolla Ansible containers, volumes and host configuration!"""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        group = parser.add_argument_group("Destroy action")
        group.add_argument(
            "--yes-i-really-really-mean-it",
            action="store_true",
            required=True,
            help="WARNING! This action will remove the Openstack deployment!",
        )
        group.add_argument(
            "--include-dev",
            action="store_true",
            help="Remove devevelopment environment",
        )
        group.add_argument(
            "--include-images",
            action="store_true",
            help="Remove leftover container images",
        )
        return parser

    def take_action(self, parsed_args):
        self.app.LOG.warning("WARNING: This will PERMANENTLY DESTROY "
                             "all deployed kolla containers, volumes "
                             "and host configuration. There is no way "
                             "to recover from this action!")

        extra_vars = {}
        extra_vars["kolla_action"] = "destroy"
        extra_vars["destroy_include_dev"] = (
            "yes" if parsed_args.include_dev else "no"
        )
        extra_vars["destroy_include_images"] = (
            "yes" if parsed_args.include_images else "no"
        )

        playbooks = _choose_playbooks(parsed_args, "destroy")

        self.run_playbooks(parsed_args, playbooks, extra_vars=extra_vars)


class PruneImages(KollaAnsibleMixin, Command):
    """Prune orphaned Kolla Ansible docker images"""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        group = parser.add_argument_group("Prune images action")
        group.add_argument(
            "--yes-i-really-really-mean-it",
            action="store_true",
            required=True,
            help="WARNING! This action will remove all orphaned images!",
        )
        return parser

    def take_action(self, parsed_args):
        self.app.LOG.info("Prune orphaned Kolla images")

        playbooks = _choose_playbooks(parsed_args, "prune-images")

        self.run_playbooks(parsed_args, playbooks)


class BifrostDeploy(KollaAnsibleMixin, Command):
    """Deploy and start bifrost container"""

    def take_action(self, parsed_args):
        self.app.LOG.info("Deploying Bifrost")

        extra_vars = {}
        extra_vars["kolla_action"] = "deploy"

        playbooks = _choose_playbooks(parsed_args, "bifrost")

        self.run_playbooks(parsed_args, playbooks, extra_vars=extra_vars)


class BifrostDeployServers(KollaAnsibleMixin, Command):
    """Enroll and deploy servers with bifrost"""

    def take_action(self, parsed_args):
        self.app.LOG.info("Deploying servers with bifrost")

        extra_vars = {}
        extra_vars["kolla_action"] = "deploy-servers"

        playbooks = _choose_playbooks(parsed_args, "bifrost")

        self.run_playbooks(parsed_args, playbooks, extra_vars=extra_vars)


class BifrostUpgrade(KollaAnsibleMixin, Command):
    """Upgrades an existing bifrost container"""

    def take_action(self, parsed_args):
        self.app.LOG.info("Upgrading Bifrost")

        extra_vars = {}
        extra_vars["kolla_action"] = "upgrade"

        playbooks = _choose_playbooks(parsed_args, "bifrost")

        self.run_playbooks(parsed_args, playbooks, extra_vars=extra_vars)


class RabbitMQResetState(KollaAnsibleMixin, Command):
    """Force reset the state of RabbitMQ"""

    def take_action(self, parsed_args):
        self.app.LOG.info("Force reset the state of RabbitMQ")

        playbooks = _choose_playbooks(parsed_args, "rabbitmq-reset-state")

        self.run_playbooks(parsed_args, playbooks)


class MariaDBBackup(KollaAnsibleMixin, Command):
    """Take a backup of MariaDB databases. See help for options."""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        group = parser.add_argument_group("MariaDB backup type")
        group.add_argument(
            "--full",
            action="store_const",
            const="full",
            dest="mariadb_backup_type",
            default="full"
        )
        group.add_argument(
            "--incremental",
            action="store_const",
            const="incremental",
            dest="mariadb_backup_type"
        )
        return parser

    def take_action(self, parsed_args):
        self.app.LOG.info("Backup MariaDB databases")

        extra_vars = {}
        extra_vars["kolla_action"] = "backup"
        extra_vars["mariadb_backup_type"] = parsed_args.mariadb_backup_type

        playbooks = _choose_playbooks(parsed_args, "mariadb_backup")

        self.run_playbooks(parsed_args, playbooks, extra_vars=extra_vars)


class MariaDBRecovery(KollaAnsibleMixin, Command):
    """Recover a completely stopped MariaDB cluster"""

    def take_action(self, parsed_args):
        self.app.LOG.info("Attempting to restart MariaDB cluster")

        extra_vars = {}
        extra_vars["kolla_action"] = "deploy"

        playbooks = _choose_playbooks(parsed_args, "mariadb_recovery")

        self.run_playbooks(parsed_args, playbooks, extra_vars=extra_vars)


class NovaLibvirtCleanup(KollaAnsibleMixin, Command):
    """Clean up disabled nova_libvirt containers"""

    def take_action(self, parsed_args):
        self.app.LOG.info("Cleanup disabled nova_libvirt containers")

        playbooks = _choose_playbooks(parsed_args, "nova-libvirt-cleanup")

        self.run_playbooks(parsed_args, playbooks)


class Check(KollaAnsibleMixin, Command):
    """Check container status"""

    def take_action(self, parsed_args):
        self.app.LOG.info("Checking container status")

        extra_vars = {}
        extra_vars["kolla_action"] = "check"

        playbooks = _choose_playbooks(parsed_args)

        self.run_playbooks(parsed_args, playbooks, extra_vars=extra_vars)


class MigrateContainerEngine(KollaAnsibleMixin, Command):
    """Migrate the container engine of the deployed OpenStack"""

    def take_action(self, parsed_args):
        self.app.LOG.info(
            "Migrate the container engine of the deployed Openstack"
        )

        playbooks = _choose_playbooks(parsed_args, "migrate-container-engine")

        self.run_playbooks(parsed_args, playbooks)


class SetupWizard(Command):
    """Interactive wizard for initial Kolla Ansible setup"""

    def take_action(self, parsed_args):
        import os
        import yaml

        print("=== Kolla Ansible Setup Wizard ===")
        print("This wizard will help you configure basic settings for Kolla Ansible.")
        print()

        # Check if globals.yml exists
        globals_path = "/etc/kolla/globals.yml"
        if os.path.exists(globals_path):
            print(f"Found existing globals.yml at {globals_path}")
            overwrite = input("Do you want to overwrite it? (y/N): ").lower().strip()
            if overwrite != 'y':
                print("Setup cancelled.")
                return

        # Collect basic configuration
        config = {}

        print("\n1. Network Configuration:")
        config['kolla_internal_vip_address'] = input("Internal VIP address (e.g., 192.168.1.100): ").strip()
        config['kolla_external_vip_address'] = input("External VIP address (leave empty if same as internal): ").strip() or config['kolla_internal_vip_address']
        config['network_interface'] = input("Network interface for external network (e.g., eth0): ").strip()

        print("\n2. Container Engine:")
        engine = input("Container engine (docker/podman) [docker]: ").strip().lower()
        config['kolla_base_distro'] = engine if engine in ['docker', 'podman'] else 'docker'

        print("\n3. OpenStack Services:")
        services = input("Enable all-in-one deployment? (y/N): ").lower().strip()
        if services == 'y':
            config['enable_haproxy'] = 'yes'
            config['enable_mariadb'] = 'yes'
            config['enable_rabbitmq'] = 'yes'
            config['enable_keystone'] = 'yes'
            config['enable_glance'] = 'yes'
            config['enable_nova'] = 'yes'
            config['enable_neutron'] = 'yes'
            config['enable_cinder'] = 'yes'
        else:
            print("For advanced configuration, edit /etc/kolla/globals.yml manually.")

        print("\n4. Storage:")
        storage = input("Storage backend (lvm/ceph/none) [none]: ").strip().lower()
        if storage == 'lvm':
            config['enable_cinder_backend_lvm'] = 'yes'
        elif storage == 'ceph':
            config['enable_cinder_backend_rbd'] = 'yes'

        # Write configuration
        os.makedirs("/etc/kolla", exist_ok=True)
        with open(globals_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)

        print(f"\nConfiguration saved to {globals_path}")
        print("Next steps:")
        print("1. Edit /etc/kolla/globals.yml for advanced settings")
        print("2. Generate passwords: kolla-genpwd")
        print("3. Run bootstrap: kolla-ansible bootstrap-servers")
        print("4. Deploy: kolla-ansible deploy")


class ValidateSetup(KollaAnsibleMixin, Command):
    """Validate Kolla Ansible configuration before deployment"""

    def take_action(self, parsed_args):
        import os
        import yaml

        print("=== Kolla Ansible Configuration Validation ===")

        errors = []
        warnings = []

        # Check globals.yml
        globals_path = "/etc/kolla/globals.yml"
        if not os.path.exists(globals_path):
            errors.append(f"globals.yml not found at {globals_path}")
        else:
            try:
                with open(globals_path, 'r') as f:
                    config = yaml.safe_load(f)

                # Validate required fields
                required_fields = ['kolla_internal_vip_address', 'network_interface']
                for field in required_fields:
                    if field not in config or not config[field]:
                        errors.append(f"Missing required field: {field}")

                # Validate IP addresses
                import ipaddress
                for field in ['kolla_internal_vip_address', 'kolla_external_vip_address']:
                    if field in config and config[field]:
                        try:
                            ipaddress.ip_address(config[field])
                        except ValueError:
                            errors.append(f"Invalid IP address for {field}: {config[field]}")

                # Check network interface
                if 'network_interface' in config and config['network_interface']:
                    # Basic check - could be enhanced with actual interface validation
                    pass

            except yaml.YAMLError as e:
                errors.append(f"Invalid YAML in globals.yml: {e}")

        # Check passwords.yml
        passwords_path = "/etc/kolla/passwords.yml"
        if not os.path.exists(passwords_path):
            warnings.append(f"passwords.yml not found at {passwords_path}. Run kolla-genpwd to generate.")
        else:
            try:
                with open(passwords_path, 'r') as f:
                    passwords = yaml.safe_load(f)
                if not passwords:
                    warnings.append("passwords.yml appears to be empty")
            except yaml.YAMLError as e:
                errors.append(f"Invalid YAML in passwords.yml: {e}")

        # Check inventory
        inventory_path = "/etc/kolla/inventory"
        if not os.path.exists(inventory_path):
            warnings.append(f"Inventory not found at {inventory_path}")

        # Report results
        if errors:
            print("❌ ERRORS:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("✅ No critical errors found")

        if warnings:
            print("\n⚠️  WARNINGS:")
            for warning in warnings:
                print(f"  - {warning}")

        if not errors:
            print("\n🎉 Configuration validation passed!")
        else:
            print("\n❌ Please fix the errors before deploying.")
