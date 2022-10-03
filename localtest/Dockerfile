FROM localhost/structured-log-transfer
COPY --chown=appuser:appuser --chmod=700 entrypoint_test.sh entrypoint_test.sh
COPY --chown=appuser:appuser --chmod=700 . .

ENV DJANGO_SETTINGS_MODULE structuredlogtransfer.settings

entrypoint ["./entrypoint_test.sh"]
