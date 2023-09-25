from datetime import datetime, timezone
from typing import Callable, Optional, Union, List

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType
from django.db.models import Model
from django.db import transaction
from django.db.models.base import ModelBase
from elastic_transport import ObjectApiResponse

from log_transfer.enums import Operation, Role, Status
from log_transfer.models import AuditLogEntry
from log_transfer.tasks import LOGGER, init
from structuredlogtransfer.settings import AuditLoggerType

# In this module for testing purposes only.

User = get_user_model()


def _now() -> datetime:
    """Returns the current time in UTC timezone."""
    return datetime.now(tz=timezone.utc)


def _iso8601_date(time: datetime) -> str:
    """Formats the timestamp in ISO-8601 format, e.g. '2020-06-01T00:00:00.000Z'."""
    return f"{time.replace(tzinfo=None).isoformat(timespec='milliseconds')}Z"

@transaction.atomic
def log(
    actor: Optional[Union[User, AnonymousUser]],
    actor_backend: str,
    operation: Operation,
    target: Union[Model, ModelBase],
    status: Status = Status.SUCCESS,
    get_time: Callable[[], datetime] = _now,
    ip_address: str = "",
    additional_information: str = "",
    audit_logger_type: AuditLoggerType = AuditLoggerType.SINGLE_COLUMN_JSON,
):
    current_time = get_time()

    if audit_logger_type == AuditLoggerType.SINGLE_COLUMN_JSON:
        user_id = str(actor.pk) if getattr(actor, "pk", None) else ""
        message = {
            "audit_event": { # See env variable DATE_TIME_PARENT_FIELD if changing this
                "origin": settings.AUDIT_LOG_ORIGIN,
                "status": str(status.value),
                "date_time_epoch": int(current_time.timestamp() * 1000),
                "date_time": _iso8601_date(current_time), # See env variable DATE_TIME_FIELD if changing this
                "actor": {
                    "role": str(Role.SYSTEM.value),
                    "user_id": user_id,
                    "provider": actor_backend
                    if actor_backend
                    else "",
                    "ip_address": ip_address,
                },
                "operation": str(operation.value),
                "additional_information": additional_information,
                "target": {
                    "id": _get_target_id(target),
                    "type": _get_target_type(target),
                },
            },
        }

        AuditLogEntry.objects.create(
            message=message,
        )

    elif audit_logger_type == AuditLoggerType.DJANGO_AUDITLOG:
        from auditlog.models import LogEntry

        LogEntry.objects.create(
            content_type=ContentType.objects.get_for_model(actor),
            object_pk=str(actor.pk),
            object_id=actor.id,
            serialized_data=None,
            actor=actor,
            additional_data={"is_sent": False, "ip_address": ip_address},
            action=LogEntry.Action.CREATE,
            timestamp=current_time,
            changes={"username": [None, actor.username]},
        )

    # Should never happen, but just in case
    else:
        raise RuntimeError("Unknown audit logger type set.")


def differentKindOfLog(
    somefield: str,
    status: Status = Status.SUCCESS,
    get_time: Callable[[], datetime] = _now,
    anotherfield: str = "",
):
    current_time = get_time()

    message = {
        "different_audit_event": { # See env variable DATE_TIME_PARENT_FIELD in tests
            "origin": settings.AUDIT_LOG_ORIGIN,
            "status": str(status.value),
            "epoch_differentkind": int(current_time.timestamp() * 1000),
            "different_date_time": _iso8601_date(current_time), # See env variable DATE_TIME_FIELD in tests
            "somefield": somefield,
            "anotherfield": anotherfield,
        },
    }

    AuditLogEntry.objects.create(
        message=message,
    )

def dateTimeInRootLog(
    somefield: str,
    status: Status = Status.SUCCESS,
    get_time: Callable[[], datetime] = _now,
    anotherfield: str = "",
):
    current_time = get_time()

    message = {
        "different_audit_event": {
            "origin": settings.AUDIT_LOG_ORIGIN,
            "status": str(status.value),
            "epoch_differentkind": int(current_time.timestamp() * 1000),
            "somefield": somefield,
            "anotherfield": anotherfield,
        },
        "date_time": _iso8601_date(current_time), # See env variable DATE_TIME_FIELD in tests
    }

    AuditLogEntry.objects.create(
        message=message,
    )


def _get_target_id(target: Union[Model, ModelBase]) -> Optional[str]:
    if isinstance(target, ModelBase):
        return ""
    field_name = getattr(target, "audit_log_id_field", "pk")
    audit_log_id = getattr(target, field_name, None)
    return str(audit_log_id)


def _get_target_type(target: Union[Model, ModelBase]) -> Optional[str]:
    return (
        str(target.__class__.__name__)
        if isinstance(target, Model)
        else str(target.__name__)
    )


def search_entries_from_elastic_search() -> Optional[ObjectApiResponse]:
    es = init()
    if es is None:
        return

    LOGGER.info(f"Search: {settings.ELASTICSEARCH_APP_AUDIT_LOG_INDEX}")

    # Index needs a refresh for the search to work this quickly
    es.indices.refresh(index=settings.ELASTICSEARCH_APP_AUDIT_LOG_INDEX)

    response = es.search(index=settings.ELASTICSEARCH_APP_AUDIT_LOG_INDEX, query={"match_all": {}})
    LOGGER.info(f"Search result: {response}")
    return response


def get_entries_from_elastic_search(id_list: List[str]) -> Optional[ObjectApiResponse]:
    client = init()
    if client is None:
        return

    LOGGER.info(f"Getting from: {settings.ELASTICSEARCH_APP_AUDIT_LOG_INDEX}")
    response = client.mget(index=settings.ELASTICSEARCH_APP_AUDIT_LOG_INDEX, ids=id_list)
    print(f"Result: {response}")
    return response


def delete_elastic_index() -> None:
    client = init()
    if client is None:
        return
    client.options(ignore_status=[404]).indices.delete(index=settings.ELASTICSEARCH_APP_AUDIT_LOG_INDEX)
