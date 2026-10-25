FROM ghcr.io/vrtmrz/livesync-cli:latest
ARG BUILD_VERSION=0.1.0
LABEL io.hass.version="${BUILD_VERSION}" io.hass.type="app" io.hass.arch="amd64"
USER root
COPY run.sh /run.sh
RUN chmod 755 /run.sh
ENTRYPOINT ["/bin/sh", "/run.sh"]
