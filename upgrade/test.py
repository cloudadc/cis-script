import re
import os

# Define the input YAML file
input_file = "cis1.yaml"

pattern = re.compile(r"--bigip-url=([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)")

with open(input_file, 'r') as file:
        content = file.read()

match = pattern.search(content)
if match:
    bigip_url = match.group(1)
    print(f"Extracted IP Address: {bigip_url}")
