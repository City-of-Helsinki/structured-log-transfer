from django.conf import settings
from django_extensions.management.jobs import QuarterHourlyJob

from log_transfer.tasks import send_audit_log_to_elastic_search


class Job(QuarterHourlyJob):
    help = "Send AuditLogEntry to centralized log center every 15 minutes"

    def execute(self):
        if settings.ENABLE_SEND_AUDIT_LOG:
            print("Running send audit log to elastic.")
            send_audit_log_to_elastic_search()
            print("Send audit log to elastic done.")
        else:
            print("NOT running send audit log to elastic, ENABLE_SEND_AUDIT_LOG is set to " + str(settings.ENABLE_SEND_AUDIT_LOG) +  " .")
            