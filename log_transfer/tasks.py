import logging
from abc import ABC, abstractmethod
from datetime import timedelta
from functools import cached_property
from typing import Any, Dict, List, TYPE_CHECKING, Optional

from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from elasticsearch import Elasticsearch

from log_transfer.models import AuditLogEntry
from structuredlogtransfer.settings import AuditLoggerType

if TYPE_CHECKING:
    from auditlog.models import LogEntry


ES_STATUS_CREATED = "created"
LOGGER = logging.getLogger(__name__)


def init() -> Optional[Elasticsearch]:
    if not (
        settings.ELASTICSEARCH_HOST
        and settings.ELASTICSEARCH_PORT
        and settings.ELASTICSEARCH_APP_AUDIT_LOG_INDEX
        # and settings.ELASTICSEARCH_USERNAME
        # and settings.ELASTICSEARCH_PASSWORD
    ):
        LOGGER.warning(
            "Trying to use Elasticsearch without proper configuration, process skipped. Host: " +
            str(settings.ELASTICSEARCH_HOST) + ", Port: " +
            str(settings.ELASTICSEARCH_PORT) + ", Index: " +
            str(settings.ELASTICSEARCH_APP_AUDIT_LOG_INDEX)
        )
        return
    return Elasticsearch(
        [
            {
                "host": settings.ELASTICSEARCH_HOST,
                "port": settings.ELASTICSEARCH_PORT,
                "scheme": settings.ELASTICSEARCH_SCHEME
            }
        ],
        basic_auth=(settings.ELASTICSEARCH_USERNAME, settings.ELASTICSEARCH_PASSWORD),
    )


def send_audit_log_to_elastic_search() -> Optional[List[str]]:
    client = init()
    if client is None:
        return

    entries = get_unsent_entries()

    result_ids: List[str] = []

    for entry in entries:
        message_body = entry.message.copy()
        response = client.index(
            index=settings.ELASTICSEARCH_APP_AUDIT_LOG_INDEX,
            id=str(entry.log.id),
            document=message_body,
            op_type="create",
        )
        LOGGER.info(f"Sending status: {response}")

        if response.get("result") == ES_STATUS_CREATED:
            entry.mark_as_sent()
            result_ids.append(response.get("_id"))

    return result_ids


class AuditLogFacade(ABC):

    def __init__(self, log: Any):
        self.log = log

    @property
    @abstractmethod
    def message(self) -> Dict[str, Any]:
        return NotImplemented

    @abstractmethod
    def mark_as_sent(self) -> None:
        return NotImplemented

    def __str__(self) -> str:
        return str(self.log)


class SimpleAuditLogFacade(AuditLogFacade):
    log: AuditLogEntry

    @cached_property
    def message(self) -> Dict[str, Any]:
        message = self.log.message.copy()
        message["@timestamp"] = (
            message[settings.DATE_TIME_PARENT_FIELD][settings.DATE_TIME_FIELD]
            if settings.DATE_TIME_PARENT_FIELD
            else message[settings.DATE_TIME_FIELD]
        )
        return message

    def mark_as_sent(self) -> None:
        self.log.is_sent = True
        self.log.save()


class DjangoAuditLogFacade(AuditLogFacade):
    log: "LogEntry"

    @cached_property
    def message(self) -> Dict[str, Any]:
        return {
            "@timestamp": self.log.timestamp,
            "audit_event": {
                "actor": self.log.actor.get_full_name() or str(self.log.actor.email),
                "date_time": self.log.timestamp,
                "operation": str(self.log.action),
                "origin": settings.AUDIT_LOG_ORIGIN,
                "target": self.log.object_repr,
                "environment": settings.AUDIT_LOG_ENVIRONMENT,
                "message": self.log.changes,
            }
        }

    def mark_as_sent(self) -> None:
        if self.log.additional_data is None:
            self.log.additional_data = {}
        self.log.additional_data["is_sent"] = True
        self.log.save()


def get_unsent_entries() -> List[AuditLogFacade]:

    if settings.AUDIT_LOGGER_TYPE == AuditLoggerType.SINGLE_COLUMN_JSON:
        return [
            SimpleAuditLogFacade(log=log)
            for log in AuditLogEntry.objects.filter(is_sent=False).order_by("created_at")
        ]

    elif settings.AUDIT_LOGGER_TYPE == AuditLoggerType.DJANGO_AUDITLOG:
        from auditlog.models import LogEntry

        return [
            DjangoAuditLogFacade(log=log)
            for log in LogEntry.objects.filter(
                ~Q(additional_data__has_key="is_sent")  # support old entries
                | Q(additional_data__is_sent=False),
            ).order_by("timestamp")
        ]

    # Should never happen, but just in case
    else:
        raise RuntimeError("Unknown audit logger type set.")


def clear_audit_log_entries(days_to_keep: int = 30) -> None:
    # Only remove entries older than `X` days

    if settings.AUDIT_LOGGER_TYPE == AuditLoggerType.SINGLE_COLUMN_JSON:
        AuditLogEntry.objects.filter(
            is_sent=True,
            created_at__lte=(timezone.now() - timedelta(days=days_to_keep)),
        ).delete()

    elif settings.AUDIT_LOGGER_TYPE == AuditLoggerType.DJANGO_AUDITLOG:
        from auditlog.models import LogEntry

        LogEntry.objects.filter(
            ~Q(additional_data__has_key="is_sent")  # support old entries
            | Q(additional_data__is_sent=True),
            timestamp__lte=(timezone.now() - timedelta(days=days_to_keep)),
        ).delete()

    # Should never happen, but just in case
    else:
        raise RuntimeError("Unknown audit logger type set.")
