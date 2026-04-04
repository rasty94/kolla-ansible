Python Modules Reference
========================

This page lists internal Python modules that provide functionality used by playbooks and CLI.

kolla_ansible.ansible
---------------------

Entrypoints to run playbooks and high-level orchestration logic.

Public functions
~~~~~~~~~~~~~~~~

.. py:function:: add_ansible_args(parser)

   Add arguments required for running Ansible playbooks to a parser.

.. py:function:: add_kolla_ansible_args(parser)

   Add arguments required for running Kolla Ansible to a parser.

.. py:function:: _get_inventory_paths(parsed_args) -> List[str]

   Return path(s) to the Kolla Ansible inventory.

.. py:function:: _validate_args(parsed_args, playbooks: list) -> None

   Validate Kolla Ansible arguments and fail early if configuration is invalid.

.. py:function:: _get_vars_files(config_path: str) -> List[str]

   Return a list of variable files found under `globals.d` in the given config path.

.. py:function:: build_args(parsed_args, playbooks: list, extra_vars: dict = {}, verbose_level: int = None) -> Tuple[str, List[str]]

   Build the command and argument list for invoking `ansible-playbook`.

.. py:function:: run_playbooks(parsed_args, playbooks: list, extra_vars: dict = {}, quiet: bool = False, verbose_level: int = 0) -> None

   Run the composed `ansible-playbook` command (uses `utils.run_command`).

.. py:function:: install_galaxy_collections(force: bool = True) -> None

   Install collections declared in `requirements.yml` and `requirements-core.yml`.

kolla_ansible.utils
-------------------

Utility helpers used across modules (YAML loading, path helpers, command execution).

Public functions
~~~~~~~~~~~~~~~~

.. py:function:: get_data_files_path(*relative_path) -> str

   Return the absolute path for packaged data files (handles editable installs).

.. py:function:: galaxy_collection_install(requirements_file: str, collections_path: str = None, force: bool = False) -> None

   Install Ansible Galaxy collections with retries and logging.

.. py:function:: read_file(path: str, mode: str = "r") -> str | bytes

   Read the content of a file and return it.

.. py:function:: read_yaml_file(path: str)

   Read and decode a YAML file; exits with error on failure.

.. py:function:: is_readable_dir(path: str) -> bool

   Check whether a path references a readable directory and return a dict with result/message.

.. py:function:: is_readable_file(path: str) -> bool

   Check whether a path references a readable file and return a dict with result/message.

.. py:function:: run_command(executable: str, args: list, quiet: bool = False, **kwargs) -> None

   Run an external command, optionally silencing output.

kolla_ansible.hashi_vault
-------------------------

Helpers for HashiCorp Vault integration.

Public functions
~~~~~~~~~~~~~~~~

.. py:function:: hashicorp_vault_client(vault_namespace, vault_addr, vault_role_id, vault_secret_id, vault_token, vault_cacert)

   Create and return an authenticated `hvac.Client` instance. Validates arguments and handles AppRole or token authentication.


Notes
~~~~~
- For each function above, add examples and link to unit tests as they are implemented in `tests/`.
- Consider enabling Sphinx autodoc to extract docstrings automatically in later iterations.
