FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-dev python3-venv \
    build-essential pkg-config \
    libpq-dev libldap2-dev libsasl2-dev \
    libssl-dev libffi-dev \
    libxml2-dev libxslt1-dev \
    libjpeg-dev zlib1g-dev libfreetype6-dev \
    liblcms2-dev libwebp-dev libopenjp2-7-dev \
    libharfbuzz-dev libfribidi-dev \
    libmagic1 ca-certificates curl \
    postgresql-client npm fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv

COPY requirements.txt /tmp/odoo-requirements.txt

RUN pip install --no-cache-dir -r /tmp/odoo-requirements.txt

RUN npm install -g rtlcss \
    && npm cache clean --force

RUN useradd --create-home --uid 1001 --user-group odoo \
    && mkdir -p /opt/odoo/odoo-server /var/lib/odoo \
    && chown -R odoo:odoo /var/lib/odoo

USER odoo
WORKDIR /opt/odoo/odoo-server

EXPOSE 8069
ENTRYPOINT ["/opt/venv/bin/python", "/opt/odoo/odoo-server/odoo-bin"]
