FROM alpine:3.22
ARG BUILD_VERSION=0.1.0
LABEL io.hass.version="${BUILD_VERSION}" io.hass.type="app" io.hass.arch="amd64"
COPY run.sh /run.sh
RUN chmod 755 /run.sh
CMD ["/run.sh"]
