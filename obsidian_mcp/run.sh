#!/bin/sh
set -eu
ROOT=/app_configs/obsidian_bridge
if [ ! -d "$ROOT/vault" ] || [ ! -d "$ROOT/mcp-trash" ]; then
  echo "ERROR: Persistent Obsidian vault and trash directories were not found in $ROOT" >&2
  exit 1
fi
ln -s "$ROOT/vault" /vault
ln -s "$ROOT/mcp-trash" /trash
exec python /app/server.py
