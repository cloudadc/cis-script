import os
import re
import argparse
import shutil
from datetime import datetime

parser = argparse.ArgumentParser(description='cis 2.17.1 upgrade tools')
parser.add_argument('--files', type=str, help='cis deployments need to update')
parser.add_argument('--image', type=str, help='new cis image')
parser.add_argument('--interval', type=str, help='cis sync interval')
parser.add_argument('--label', type=str, help='cis watch namespace label')
parser.add_argument('--cm', action='store_true', default=False, help='add label to configmap')
cli = parser.parse_args()

FILES = "cis-192.168.30.204.yaml,cis-192.168.30.205.yaml"
NEW_IMAGE = "artifactory.dev.com:31345/net-docker-ver-local/bigip-ctlr/k8s-bigip-ctlr:2.17.1"
SYNC_INTERVAL="30"
NAMESPACE_LABEL="cis.f5.com/zone=zone-1"

if cli.files:
    FILES = cli.files

if cli.image:
    NEW_IMAGE = cli.image

if cli.interval:
    SYNC_INTERVAL = cli.interval

if cli.label:
    NAMESPACE_LABEL = cli.label

file_array = FILES.split(",")

update_backup_directory   = "backup"
new_args_disable_teems    = '''            "--disable-teems=true",'''
new_args_sync_interval    = '''            "--periodic-sync-interval=REPLACEMENT",'''
new_args_namespace_label  = '''            "--namespace-label=REPLACEMENT",'''
new_args_sync_interval    = new_args_sync_interval.replace("REPLACEMENT", SYNC_INTERVAL)
new_args_namespace_label  = new_args_namespace_label.replace("REPLACEMENT", NAMESPACE_LABEL) 
new_label_line            = '''    isTenantNameServiceNamespace: "true"'''

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
    if os.path.isfile(file):
        if not os.path.exists(update_backup_directory):
            os.makedirs(update_backup_directory)
        backup_file_name = os.path.join(update_backup_directory, f"{os.path.basename(file)}_{datetime.now().strftime('%Y%m%d%H%M%S')}.bak")
        shutil.copy2(file, backup_file_name)
        print(f"Backup of {file} completed: {backup_file_name}")
    else:
        print(f"Error: {file} does not exist.")

def extract_image_from_yaml(file):
    if os.path.isfile(file):
        with open(file, 'r') as f:
            content = f.read()

        # Regular expression to match the 'image' field within the 'containers' section
        image_pattern = re.compile(r'image:\s*"([^"]+)"')
        image_match = image_pattern.findall(content)

        if image_match:
            return image_match[0]
        else:
            return None
    else:
        return None


def upgrade_image(file):
    old_cis_image = extract_image_from_yaml(file)
    if os.path.isfile(file):
        with open(file, 'r') as f:
            content = f.read()
        content = content.replace(f'image: "{old_cis_image}"', f'image: "{NEW_IMAGE}"')
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

def extract_args_section(file):
    if os.path.isfile(file):
        with open(file, 'r') as f:
            content = f.read()

        args_pattern = re.compile(r'args:\s*\[(.*?)\]', re.DOTALL)
        args_match = args_pattern.search(content)

        if args_match:
            args_section = args_match.group(1)
            return args_section
        else:
            print("No args section found in the file.")
            return None
    else:
        print(f"File {file} does not exist.")
        return None

def upgrade_arguments(file):
    args = extract_args_section(file)
    if os.path.isfile(file):
        with open(file, 'r') as f:
            lines = f.readlines()

        with open(file, 'w') as f:
            for line in lines:
                if '--namespace=' in line:
                    continue
                f.write(line)
 
                if '--bigip-partition=' in line:
                    if "--disable-teems" not in args:
                        f.write(new_args_disable_teems + '\n')
                    if "--periodic-sync-interval" not in args:
                        f.write(new_args_sync_interval + '\n')
                    if "--namespace-label" not in args:
                        f.write(new_args_namespace_label + '\n')

        print(f"Updated arguments in {file}")
    else:
        print(f"Error: {file} does not exist.")

def upgrade_configmap(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    modified_lines = []
    label_inserted = False

    for line in lines:
        modified_lines.append(line)
        if 'as3: "true"' in line and not label_inserted:
            modified_lines.append(new_label_line + '\n')
            label_inserted = True

    with open(file_path, 'w') as file:
        file.writelines(modified_lines)

    print(f"Add {new_label_line} to {file_path}")


if cli.cm:
    for file in file_array:
        upgrade_configmap(file)
else:
    for file in file_array:
        backup_file(file)
        upgrade_image(file)
        upgrade_liveness_probe(file)
        upgrade_arguments(file)
