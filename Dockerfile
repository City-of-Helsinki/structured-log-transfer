# ==============================
FROM helsinkitest/python:3.8-slim as appbase
# ==============================
RUN mkdir /entrypoint

COPY requirements.in .

RUN apt-install.sh \
        git \
        # netcat \
        libpq-dev \
        build-essential \
        gettext \
        libmariadb-dev \
        pkg-config \
        postgresql-client \
    && pip install -U pip \
    && pip install pip-tools \
    && pip install mysqlclient \
    && pip-compile requirements.in \
    && pip uninstall -y pip-tools \
    && pip install -r /app/requirements.txt \
    && pip cache purge \
    && pip uninstall -y pip \
    && apt-cleanup.sh build-essential

COPY . .

RUN SECRET_KEY="only-used-for-collectstatic" python manage.py collectstatic

# Uncomment this, if utility gets translated messages
#RUN ./manage.py compilemessages

ADD --chown=appuser:appuser --chmod 440 https://cacerts.digicert.com/DigiCertGlobalRootCA.crt.pem certs/

#CMD ["echo", "Only run from cronjobs"]
ENTRYPOINT ["./manage.py"]
