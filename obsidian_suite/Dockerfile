FROM ghcr.io/vrtmrz/livesync-cli:1.0.39-cli
ARG BUILD_VERSION=0.1.0
LABEL io.hass.version="${BUILD_VERSION}" io.hass.type="app" io.hass.arch="amd64"
USER root
RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-venv ca-certificates \
  && rm -rf /var/lib/apt/lists/*
RUN python3 -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir "mcp==1.30.0" "uvicorn==0.54.0"
COPY server.py /opt/obsidian/server.py
COPY supervisor.py /opt/obsidian/supervisor.py
COPY preflight.py /opt/obsidian/preflight.py
ENTRYPOINT ["/opt/venv/bin/python", "/opt/obsidian/supervisor.py"]
