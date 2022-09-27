# ==============================
FROM helsinkitest/python:3.8-slim as appbase
# ==============================
RUN mkdir /entrypoint

COPY --chown=appuser:appuser requirements.txt /app/requirements.txt

RUN apt-install.sh \
        git \
        netcat \
        libpq-dev \
        build-essential \
        gettext \
    && pip install -U pip \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && apt-cleanup.sh build-essential

COPY . .

RUN SECRET_KEY="only-used-for-collectstatic" python manage.py collectstatic

# Uncomment this, if utility gets translated messages
#RUN ./manage.py compilemessages

CMD ["echo", "Only run from cronjobs"]
