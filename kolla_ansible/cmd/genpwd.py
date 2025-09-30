#!/usr/bin/env python

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import hmac
import os
import random
import secrets
import stat
import string
import sys

from ansible.utils.encrypt import random_salt
from cryptography import fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from hashlib import md5
from oslo_utils import uuidutils
import yaml

# NOTE(SamYaple): Update the search path to prefer PROJECT_ROOT as the source
#                 of packages to import if we are using local tools instead of
#                 pip installed kolla tools
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), '../..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def generate_RSA(bits=4096):
    new_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=bits,
        backend=default_backend()
    )
    private_key = new_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode()
    public_key = new_key.public_key().public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH
    ).decode()
    return private_key, public_key


def generate_password(length=40, include_symbols=True, require_uppercase=True,
                      require_lowercase=True, require_digits=True):
    """Generate a secure password with configurable complexity."""
    # Define character sets
    lower_chars = string.ascii_lowercase
    upper_chars = string.ascii_uppercase
    digit_chars = string.digits
    symbol_chars = '+-.*'  # Only these special characters

    # Ensure at least one of each required type
    password = []
    if require_lowercase:
        password.append(secrets.choice(lower_chars))
    if require_uppercase:
        password.append(secrets.choice(upper_chars))
    if require_digits:
        password.append(secrets.choice(digit_chars))
    if include_symbols:
        password.append(secrets.choice(symbol_chars))

    # Fill the rest of the password
    all_chars = ''
    if require_lowercase:
        all_chars += lower_chars
    if require_uppercase:
        all_chars += upper_chars
    if require_digits:
        all_chars += digit_chars
    if include_symbols:
        all_chars += symbol_chars

    if not all_chars:
        all_chars = string.ascii_letters + string.digits  # fallback

    # Fill remaining length
    remaining_length = length - len(password)
    if remaining_length > 0:
        password.extend(secrets.choice(all_chars) for _ in range(remaining_length))

    # Shuffle to avoid predictable patterns
    secrets.SystemRandom().shuffle(password)

    return ''.join(password)


def genpwd(passwords_file, length, uuid_keys, ssh_keys, blank_keys,
           fernet_keys, hmac_md5_keys, bcrypt_keys,
           include_symbols, require_uppercase, require_lowercase, require_digits):
    try:
        with open(passwords_file, 'r') as f:
            passwords = yaml.safe_load(f.read())
    except FileNotFoundError:
        print(f"ERROR: Passwords file \"{passwords_file}\" is missing")
        sys.exit(1)

    if os.stat(passwords_file).st_mode & stat.S_IROTH:
        print(f"WARNING: Passwords file \"{passwords_file}\" is"
              " world-readable. The permissions will be changed.")

    if os.stat(passwords_file).st_mode & stat.S_IWOTH:
        print(f"WARNING: Passwords file \"{passwords_file}\" is"
              " world-writeable. The permissions will be changed.")

    if not isinstance(passwords, dict):
        print("ERROR: Passwords file not in expected key/value format")
        sys.exit(1)

    for k, v in passwords.items():
        if (k in ssh_keys and
                (v is None or
                 v.get('public_key') is None and
                 v.get('private_key') is None)):
            private_key, public_key = generate_RSA()
            passwords[k] = {
                'private_key': private_key,
                'public_key': public_key
            }
            continue
        if v is None:
            if k in blank_keys and v is None:
                continue
            if k in uuid_keys:
                passwords[k] = uuidutils.generate_uuid()
            elif k in hmac_md5_keys:
                passwords[k] = (hmac.new(
                    uuidutils.generate_uuid().encode(), ''.encode(), md5)
                    .hexdigest())
            elif k in fernet_keys:
                passwords[k] = fernet.Fernet.generate_key().decode()
            elif k in bcrypt_keys:
                # NOTE(wszusmki) To be compatible with the ansible
                # password_hash filter, we use the utility function from the
                # ansible library.
                passwords[k] = random_salt(22)
            else:
                passwords[k] = generate_password(
                    length=length,
                    include_symbols=include_symbols,
                    require_uppercase=require_uppercase,
                    require_lowercase=require_lowercase,
                    require_digits=require_digits
                )

    try:
        os.remove(passwords_file)
    except OSError:
        pass

    flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
    mode = 0o640

    with os.fdopen(os.open(passwords_file, flags, mode=mode), 'w') as f:
        f.write(yaml.safe_dump(passwords, default_flow_style=False))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p', '--passwords', type=str,
        default=os.path.abspath('/etc/kolla/passwords.yml'),
        help=('Path to the passwords.yml file'))
    parser.add_argument(
        '--password-length', type=int, default=40,
        help='Length of generated passwords')
    parser.add_argument(
        '--include-symbols', action='store_true', default=True,
        help='Include symbols in passwords')
    parser.add_argument(
        '--require-uppercase', action='store_true', default=True,
        help='Require uppercase letters in passwords')
    parser.add_argument(
        '--require-lowercase', action='store_true', default=True,
        help='Require lowercase letters in passwords')
    parser.add_argument(
        '--require-digits', action='store_true', default=True,
        help='Require digits in passwords')

    args = parser.parse_args()
    passwords_file = os.path.expanduser(args.passwords)

    # These keys should be random uuids
    uuid_keys = ['rbd_secret_uuid',
                 'cinder_rbd_secret_uuid',
                 'gnocchi_project_id',
                 'gnocchi_resource_id',
                 'gnocchi_user_id',
                 'designate_pool_id']

    # SSH key pair
    ssh_keys = ['kolla_ssh_key', 'nova_ssh_key',
                'keystone_ssh_key', 'bifrost_ssh_key',
                'octavia_amp_ssh_key', 'neutron_ssh_key',
                'haproxy_ssh_key']

    # If these keys are None, leave them as None
    blank_keys = ['docker_registry_password']

    # HMAC-MD5 keys
    hmac_md5_keys = ['designate_rndc_key',
                     'osprofiler_secret']

    # Fernet keys
    fernet_keys = ['barbican_crypto_key']

    # bcrypt salts
    bcrypt_keys = ['prometheus_bcrypt_salt']

    genpwd(passwords_file, args.password_length, uuid_keys, ssh_keys, blank_keys,
           fernet_keys, hmac_md5_keys, bcrypt_keys,
           args.include_symbols, args.require_uppercase, args.require_lowercase, args.require_digits)


if __name__ == '__main__':
    main()
