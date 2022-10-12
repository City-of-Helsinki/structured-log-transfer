from django.conf import settings
from django_extensions.management.jobs import MonthlyJob

from log_transfer.tasks import clear_audit_log_entries


class Job(MonthlyJob):
    help = (
        "Clear AuditLogEntry which is already sent to Elasticsearch,"
        "only clear if settings.CLEAR_AUDIT_LOG_ENTRIES is set to True (default: False)"
    )

    def execute(self):
        if settings.CLEAR_AUDIT_LOG_ENTRIES:
            print("Running clear audit log entries job")
            clear_audit_log_entries()
            print("Running clear audit log entries job done")
        else:
            print("NOT Running clear audit log entries job, CLEAR_AUDIT_LOG_ENTRIES env is set to not run this.")
            
