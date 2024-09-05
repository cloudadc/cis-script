#!/bin/bash

# Path to your YAML file
input_file="cis1.yaml"
temp_file="temp_args.txt"

new_liveness_probe=$(cat <<EOF
          livenessProbe:
            exec:
              command:
              - curl
              - -k
              - -s
              - -o
              - /dev/null
              - https://REPLACEMENT/mgmt/shared/appsvcs/info
EOF
)

MGMT_IP="192.168.1.10"

updated_liveness_probe=$(echo "$new_liveness_probe" | sed "s/REPLACEMENT/$MGMT_IP/g")

awk -v replacement="$updated_liveness_probe" '
  BEGIN { found = 0 }
  /livenessProbe:/ { found = 1 }
  /env:/ && found { found = 0; print replacement; }
  !found { print }
' "$input_file" > "${input_file}.tmp" && mv "${input_file}.tmp" "$input_file"

#pattern_start='livenessProbe:'
#pattern_end='exec:'

# Replace the livenessProbe section
#sed -e "/$pattern_start/,/$pattern_end/{H; /$pattern_end/ {g; s|$pattern_start.*|$updated_liveness_probe|;}}" "$input_file" > "${input_file}.tmp" && mv "${input_file}.tmp" "$input_file"
#sed -e "/$pattern_start/,/$pattern_end/ {/$pattern_end/!d; r /dev/stdin}" <(echo "$escaped_probe") "$input_file" > "${input_file}.tmp" && mv "${input_file}.tmp" "$input_file"


