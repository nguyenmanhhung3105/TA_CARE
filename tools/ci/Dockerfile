ARG PLAYWRIGHT_IMAGE=mcr.microsoft.com/playwright:v1.58.2-noble@sha256:6446946a1d9fd62d9ae501312a2d76a43ee688542b21622056a372959b65d63d
FROM ${PLAYWRIGHT_IMAGE}
ENV DEBIAN_FRONTEND=noninteractive LANG=C.UTF-8 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" NODE_PATH=/opt/ci-tools/node_modules TACARE_ENVIRONMENT=local
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-dev python3-venv build-essential pkg-config \
    libpq-dev libldap2-dev libsasl2-dev libssl-dev libffi-dev libxml2-dev libxslt1-dev \
    libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev libopenjp2-7-dev \
    libharfbuzz-dev libfribidi-dev libmagic1 postgresql-client fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m venv /opt/venv && pip install --no-cache-dir -r /tmp/requirements.txt
COPY package.json package-lock.json /opt/ci-tools/
RUN npm ci --ignore-scripts --prefix /opt/ci-tools && npm install -g rtlcss@4.3.0
USER pwuser
WORKDIR /tmp
