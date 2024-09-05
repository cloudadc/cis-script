import os
import re
import shutil
from datetime import datetime

FILES = ["hygon-cis-197.20.30.204.yaml", "hygon-cis-197.20.30.205.yaml"]
OLD_IMAGE = "artifactory.dev.com:31345/net-docker-ver-local/bigip-ctlr/k8s-bigip-ctlr:2.16.1"
NEW_IMAGE = "artifactory.dev.com:31345/net-docker-ver-local/bigip-ctlr/k8s-bigip-ctlr:2.17.1"
SYNC_INTERVAL="30"
NAMESPACE_LABEL="cis.f5.com/zone=zone-1"

update_backup_directory   = "backup"
new_args_disable_teems    = '''            "--disable-teems=true",'''
new_args_sync_interval    = '''            "--periodic-sync-interval=REPLACEMENT",'''
new_args_namespace_label  = '''            "--namespace-label=REPLACEMENT",'''
new_args_sync_interval    = new_args_sync_interval.replace("REPLACEMENT", SYNC_INTERVAL)
new_args_namespace_label  = new_args_namespace_label.replace("REPLACEMENT", NAMESPACE_LABEL) 

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

def upgrade_image(file):
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

for file in FILES:
    backup_file(file)
    upgrade_image(file)
    upgrade_liveness_probe(file)
    upgrade_arguments(file)
