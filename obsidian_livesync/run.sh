#!/bin/sh
set -eu

BASE="/app_configs/obsidian_bridge"
SETTINGS="$BASE/settings/livesync-operativo.json"
VAULT="$BASE/vault"

if [ ! -s "$SETTINGS" ]; then
  echo "ERROR: LiveSync settings are missing"
  exit 1
fi

if [ ! -d "$VAULT" ]; then
  echo "ERROR: Obsidian vault is missing"
  exit 1
fi

exec livesync-cli \
  --settings "$SETTINGS" \
  --vault "$VAULT" \
  --interval 60 \
  daemon
