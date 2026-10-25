#!/bin/sh
set -eu

DATA_DIR=/app_configs/obsidian_bridge/tunnel
BINARY="$DATA_DIR/bin/tunnel-client"
KEY="$DATA_DIR/api-key"
OPTIONS=/data/options.json

if [ ! -f "$BINARY" ]; then
  echo "ERROR: A locally provisioned tunnel-client is required at $BINARY" >&2
  exit 1
fi
if [ ! -f "$KEY" ]; then
  echo "ERROR: Tunnel credential file is missing at $KEY" >&2
  exit 1
fi
if [ ! -f "$OPTIONS" ]; then
  echo "ERROR: Missing Supervisor options.json" >&2
  exit 1
fi

TUNNEL_ID="$(sed -n 's/^[[:space:]]*"tunnel_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$OPTIONS")"
SERVER_URL="$(sed -n 's/^[[:space:]]*"mcp_server_url"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$OPTIONS")"
if [ -z "$TUNNEL_ID" ] || [ -z "$SERVER_URL" ]; then
  echo "ERROR: Set tunnel_id and mcp_server_url in the add-on configuration" >&2
  exit 1
fi
if [ ! -x "$BINARY" ]; then
  echo "ERROR: tunnel-client must be executable" >&2
  exit 1
fi

mkdir -p "$DATA_DIR/run"
exec "$BINARY" run \
  --control-plane.tunnel-id "$TUNNEL_ID" \
  --control-plane.api-key "file:$KEY" \
  --mcp.server-url "channel=main,url=$SERVER_URL" \
  --health.listen-addr "127.0.0.1:0" \
  --health.url-file "$DATA_DIR/run/health.url"
