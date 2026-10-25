FROM python:3.14-slim
ARG BUILD_VERSION=1.0.0
LABEL io.hass.version="${BUILD_VERSION}" io.hass.type="app" io.hass.arch="amd64"
WORKDIR /app
RUN pip install --no-cache-dir 'mcp==1.30.0' 'uvicorn==0.54.0'
COPY server.py /app/server.py
COPY run.sh /run.sh
RUN chmod +x /run.sh
CMD ["/run.sh"]
