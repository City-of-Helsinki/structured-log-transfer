# ==============================
FROM registry.access.redhat.com/ubi9/python-312 AS appbase
# ==============================
WORKDIR /app
COPY requirements.in .

USER root
RUN dnf install -y dnf-plugins-core \
    && dnf install -y \
        git \
        libpq-devel \
        pkg-config \
        postgresql \
        mysql \
    && pip install -U pip \
    && pip install pip-tools \
    && pip install mysqlclient \
    && pip-compile requirements.in \
    && pip uninstall -y pip-tools \
    && pip install -r /app/requirements.txt \
    && pip uninstall -y pip

# Django is configured to use /srv/static as STATIC_ROOT
# so make sure it exists and user has permissions to it.
RUN mkdir /srv/static && chown 1001:0 /srv/static

# Switch back to default non-root user.
USER 1001

COPY . .

RUN SECRET_KEY="only-used-for-collectstatic" python manage.py collectstatic

# Uncomment this, if utility gets translated messages
#RUN ./manage.py compilemessages

ADD --chown=appuser:appuser https://www.digicert.com/CACerts/BaltimoreCyberTrustRoot.crt.pem certs/

#CMD ["echo", "Only run from cronjobs"]
ENTRYPOINT ["./manage.py"]
