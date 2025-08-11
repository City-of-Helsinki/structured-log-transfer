# ==============================
FROM helsinki.azurecr.io/ubi9/python-39-gdal AS appbase
# ==============================
WORKDIR /app
RUN mkdir /entrypoint
COPY requirements.in .

RUN dnf install -y dnf-plugins-core \
    && dnf install -y \
        git \
        libpq-devel \
        # build-essential equivalent packages
        make \
        automake \
        gcc \
        gcc-c++ \
        gettext \
        #libmariadb-devel \
        pkg-config \
        postgresql \
    && pip install -U pip \
    && pip install pip-tools \
    && pip install mysqlclient \
    && pip-compile requirements.in \
    && pip uninstall -y pip-tools \
    && pip install -r /app/requirements.txt \
    && pip uninstall -y pip \
    && dnf remove -y \
        # build-essential equivalent packages
        make \
        automake \
        gcc \
        gcc-c++ \
        gettext

COPY . .

RUN SECRET_KEY="only-used-for-collectstatic" python manage.py collectstatic

# Uncomment this, if utility gets translated messages
#RUN ./manage.py compilemessages

ADD --chown=appuser:appuser https://www.digicert.com/CACerts/BaltimoreCyberTrustRoot.crt.pem certs/

#CMD ["echo", "Only run from cronjobs"]
ENTRYPOINT ["./manage.py"]
