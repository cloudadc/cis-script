import os
import re
import shutil
from datetime import datetime

# Configuration for files, backup directory, and image replacement
FILES = ["hygon-cis-197.20.30.204.yaml", "hygon-cis-197.20.30.205.yaml"]
BACKUP_DIR = "backup"
OLD_IMAGE = "artifactory.dev.cmbc.cn:31345/net-docker-ver-local/bigip-ctlr/k8s-bigip-ctlr:2.16.1"
NEW_IMAGE = "artifactory.dev.cmbc.cn:31345/net-docker-ver-local/bigip-ctlr/k8s-bigip-ctlr:2.17.1"

NEW_ARGS = '''            "--disable-teems=true",
            "--periodic-sync-interval=300",
            "--namespace-label=cis.f5.com/zone=zone-1",'''

new_liveness_probe = """          livenessProbe:
            exec:
              command:
              - curl
              - -k
              - -s
              - -o
              - /dev/null
              - https://REPLACEMENT/mgmt/shared/appsvcs/info
"""


def backup_file(file):
    """Creates a backup of the specified file."""
    if os.path.isfile(file):
        if not os.path.exists(BACKUP_DIR):
            os.makedirs(BACKUP_DIR)
        backup_file_name = os.path.join(BACKUP_DIR, f"{os.path.basename(file)}_{datetime.now().strftime('%Y%m%d%H%M%S')}.bak")
        shutil.copy2(file, backup_file_name)
        print(f"Backup of {file} completed: {backup_file_name}")
    else:
        print(f"Error: {file} does not exist.")

def upgrade_image(file):
    """Replaces the old image with the new image in the specified file."""
    if os.path.isfile(file):
        with open(file, 'r') as f:
            content = f.read()
        content = content.replace(f'image: "{OLD_IMAGE}"', f'image: "{NEW_IMAGE}"')
        with open(file, 'w') as f:
            f.write(content)
        print(f"Replaced image in {file} to {NEW_IMAGE}")
    else:
        print(f"Error: {file} does not exist.")

def upgrade_liveness_probe(file):
    if os.path.isfile(file):
        mgmt_ip = "127.0.0.1"
        with open(file, 'r') as f:
            content = f.read()
        pattern = re.compile(r"--bigip-url=([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)")
        match = pattern.search(content)
        if match:
            mgmt_ip = match.group(1)
        updated_liveness_probe = new_liveness_probe.replace("REPLACEMENT", mgmt_ip)

        in_liveness_block = False
        updated_content = []

        with open(file, 'r') as f:
            content = f.readlines()

        for line in content:
            if re.match(r'^\s*livenessProbe:', line):
                in_liveness_block = True
                continue
            if re.match(r'^\s*initialDelaySeconds:', line) and in_liveness_block:
                in_liveness_block = False
                updated_content.append(updated_liveness_probe)
            if not in_liveness_block:
                updated_content.append(line)
        
        with open(file, 'w') as f:
            f.writelines(updated_content)

        print(f"Updated livenessProbe section in {file}.")
    else:
        print(f"Error: {file} does not exist.")

def upgrade_arguments(file):
    """Replaces certain arguments in the file and adds new arguments after a specific line."""
    if os.path.isfile(file):
        with open(file, 'r') as f:
            lines = f.readlines()

        with open(file, 'w') as f:
            for line in lines:
                # Remove existing --namespace arguments
                if '--namespace=' in line:
                    continue
                f.write(line)
                # Add new arguments after --bigip-partition line
                if '--bigip-partition=' in line:
                    f.write(NEW_ARGS + '\n')

        print(f"Updated arguments in {file}")
    else:
        print(f"Error: {file} does not exist.")

for file in FILES:
    backup_file(file)
    upgrade_image(file)
    upgrade_liveness_probe(file)
    upgrade_arguments(file)
