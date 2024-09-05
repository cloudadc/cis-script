#!/bin/bash

FILES=("hygon-cis-197.20.30.204.yaml" "hygon-cis-197.20.30.205.yaml")
BACKUP_DIR="backup"
OLD_IMAGE="artifactory.dev.com:31345/net-docker-ver-local/bigip-ctlr/k8s-bigip-ctlr:2.16.1"
NEW_IMAGE="artifactory.dev.com:31345/net-docker-ver-local/bigip-ctlr/k8s-bigip-ctlr:2.17.1"

NEW_ARGS='            "--disable-teems=true",
            "--periodic-sync-interval=300",
            "--namespace-label=cis.f5.com/zone=zone-1",'

if [ ! -d "$BACKUP_DIR" ]; then
  mkdir -p "$BACKUP_DIR"
fi

backup_file() {
  local FILE="$1"
  
  if [ -f "$FILE" ]; then
    BACKUP_FILE="${BACKUP_DIR}/$(basename ${FILE})_$(date +%Y%m%d%H%M%S).bak"
    cp "$FILE" "$BACKUP_FILE"
    echo "Backup of $FILE completed: $BACKUP_FILE"
  else
    echo "Error: $FILE does not exist."
  fi
}

upgrade_image() {
  local FILE="$1"

  if [ -f "$FILE" ]; then
    sed -i '' "s|image: \"$OLD_IMAGE\"|image: \"$NEW_IMAGE\"|g" "$FILE"
    echo "Replaced image in $FILE to $NEW_IMAGE"
  else
    echo "Error: $FILE does not exist."
  fi
}

upgrade_livenessProbe() {
  local FILE="$1"

  if [ -f "$FILE" ]; then
    echo "Upgraded livenessProbe in $FILE"
  else
    echo "Error: $FILE does not exist."
  fi
}

upgrade_arguments() {
  local FILE="$1"
  temp_file="temp_args.txt"

  if [ -f "$FILE" ]; then
    sed -i '' '/--namespace=[^,]*/d' "$FILE"
    printf "%s\n" "$NEW_ARGS" > "$temp_file"
    awk -v args_file="$temp_file" '
      /--bigip-partition=/ {
        print;
        system("cat " args_file);
        next
      }
      { print }
    ' "$FILE" > "${FILE}.tmp" && mv "${FILE}.tmp" "$FILE"
    rm "$temp_file"
    sed -i '' 's/\r$//' "$FILE"
    echo "Updated arguments in $FILE"
  else
    echo "Error: $FILE does not exist."
  fi
}

for FILE in "${FILES[@]}"; do
  backup_file "$FILE"
  upgrade_image "$FILE" 
  upgrade_livenessProbe "$FILE"
  upgrade_arguments "$FILE"
done

