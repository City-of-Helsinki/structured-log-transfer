from datetime import datetime, timedelta
from unittest import mock

import pytest
from django.contrib.auth.models import AnonymousUser
from django.test import override_settings
from django.utils import timezone

from log_transfer.tests import audit_logging
from log_transfer.enums import Operation, Status
from log_transfer.models import AuditLogEntry
from log_transfer.tasks import (
    clear_audit_log_entries,
    send_audit_log_to_elastic_search,
    get_entries_from_elastic_search,
    search_entries_from_elastic_search,
    delete_elastic_index
)


_common_fields = {
    "audit_event": {
        "origin": "TEST_SERVICE",
        "status": "SUCCESS",
        "date_time_epoch": 1590969600000,
        "date_time": "2020-06-01T00:00:00.000Z",
        "actor": {
            "role": "OWNER",
            "user_id": "",
            "ip_address": "192.168.1.1",
            "provider": "",
        },
        "operation": "READ",
        "target": {
            "id": "",
            "type": "User",
        },
        "additional_information": "",
    }
}

@pytest.mark.django_db
@override_settings(
    AUDIT_LOG_ORIGIN="TEST_SERVICE",
)
@pytest.mark.parametrize("operation", list(Operation))
def test_log_system_operation(fixed_datetime, user, operation):
    audit_logging.log(
        None,
        "",
        operation,
        user,
        get_time=fixed_datetime,
        ip_address="192.168.1.1",
    )

    audit_log_changes = AuditLogEntry.objects.first().message
    assert audit_log_changes == {
        **_common_fields,
        "audit_event": {
            **_common_fields["audit_event"],
            "operation": operation.value,
            "actor": {
                "role": "SYSTEM",
                "user_id": "",
                "ip_address": "192.168.1.1",
                "provider": "",
            },
            "target": {
                "id": str(user.pk),
                "type": "User",
            },
        },
    }



@pytest.mark.django_db
@override_settings(
    AUDIT_LOG_ORIGIN="TEST_SERVICE",
)
def test_log_origin(fixed_datetime, user):
    audit_logging.log(
        user,
        "",
        Operation.READ,
        user,
        get_time=fixed_datetime,
        ip_address="192.168.1.1",
    )

    audit_log_changes = AuditLogEntry.objects.first().message
    assert audit_log_changes["audit_event"]["origin"] == "TEST_SERVICE"


@pytest.mark.django_db
@override_settings(
    AUDIT_LOG_ORIGIN="TEST_SERVICE",
)
def test_log_current_timestamp(user):
    tolerance = timedelta(seconds=1)
    date_before_logging = datetime.now(tz=timezone.utc) - tolerance
    audit_logging.log(
        user,
        "",
        Operation.READ,
        user,
        ip_address="192.168.1.1",
    )

    date_after_logging = datetime.now(tz=timezone.utc) + tolerance
    audit_log_changes = AuditLogEntry.objects.first().message
    logged_date_from_date_time_epoch = datetime.fromtimestamp(
        int(audit_log_changes["audit_event"]["date_time_epoch"]) / 1000, tz=timezone.utc
    )
    assert date_before_logging <= logged_date_from_date_time_epoch <= date_after_logging
    logged_date_from_date_time = datetime.strptime(
        audit_log_changes["audit_event"]["date_time"], "%Y-%m-%dT%H:%M:%S.%f%z"
    )
    assert date_before_logging <= logged_date_from_date_time <= date_after_logging


@pytest.mark.django_db
@override_settings(
    AUDIT_LOG_ORIGIN="TEST_SERVICE",
)
def test_log_additional_information(user):
    audit_logging.log(
        user,
        "",
        Operation.UPDATE,
        user,
        additional_information="test",
    )

    audit_log_changes = AuditLogEntry.objects.first().message
    assert audit_log_changes["audit_event"]["additional_information"] == "test"



@pytest.mark.django_db
@override_settings(CLEAR_AUDIT_LOG_ENTRIES=True)
def test_send_audit_log(user, fixed_datetime):

    # database is cleared between tests, so it attempts to send to elastic using old id numbers
    # solution: delete the index and start over for each test
    delete_elastic_index()

    addresses = ["192.168.1.1", "192.168.1.2", "192.168.1.3"]
    for addr in addresses:
        audit_logging.log(
          user,
          "shared.oidc.auth.HelsinkiOIDCAuthenticationBackend",
          Operation.READ,
          user,
          get_time=fixed_datetime,
          ip_address=addr,
        )
    assert AuditLogEntry.objects.count() == 3

    ids = send_audit_log_to_elastic_search()
    assert len(ids) == 3

    result = get_entries_from_elastic_search(ids)

    assert len(result.get("docs")) == 3

    # Test search

    result = search_entries_from_elastic_search()
    hits = result["hits"]
    total = hits["total"]
    value = total["value"]
    assert value == 3


@pytest.mark.django_db
@override_settings(DATE_TIME_PARENT_FIELD="different_audit_event", DATE_TIME_FIELD="different_date_time")
def test_send_different_audit_log(user, fixed_datetime):

    # database is cleared between tests, so it attempts to send to elastic using old id numbers
    # solution: delete the index and start over for each test
    delete_elastic_index()

    # Create another kind of log, this is in the same test to prevent
    # conflicting ids in database to be sent to elastic

    somedata = ["a", "b", "c"]
    for data in somedata:
        audit_logging.differentKindOfLog(
          somefield=data,
          anotherfield="another "+data,
        )

    assert AuditLogEntry.objects.count() == 3 # 3 instances in db as db was cleaned up

    ids = send_audit_log_to_elastic_search()
    assert len(ids) == 3

    result = get_entries_from_elastic_search(ids)

    assert len(result.get("docs")) == 3 # Only 3 ids were created

    # Test search

    result = search_entries_from_elastic_search()
    hits = result["hits"]
    total = hits["total"]
    value = total["value"]
    assert value == 3 # Search will find only the ones from this test, as index was deleted


@pytest.mark.django_db
@override_settings(DATE_TIME_PARENT_FIELD=None, DATE_TIME_FIELD="date_time")
def test_send_timestamp_in_root(user, fixed_datetime):

    # database is cleared between tests, so it attempts to send to elastic using old id numbers
    # solution: delete the index and start over for each test
    delete_elastic_index()

    # Create another kind of log, this is in the same test to prevent
    # conflicting ids in database to be sent to elastic

    somedata = ["a", "b", "c"]
    for data in somedata:
        audit_logging.dateTimeInRootLog(
          somefield=data,
          anotherfield="another "+data,
        )

    assert AuditLogEntry.objects.count() == 3 # 3 instances in db as db was cleaned up

    ids = send_audit_log_to_elastic_search()
    assert len(ids) == 3

    result = get_entries_from_elastic_search(ids)

    assert len(result.get("docs")) == 3 # Only 3 ids were created

    # Test search

    result = search_entries_from_elastic_search()
    hits = result["hits"]
    total = hits["total"]
    value = total["value"]
    assert value == 3 # Search will find only the ones from this test, as index was deleted


@pytest.mark.django_db
@override_settings(CLEAR_AUDIT_LOG_ENTRIES=True)
def test_clear_audit_log(user, fixed_datetime):
    addresses = ["192.168.1.1", "192.168.1.2", "192.168.1.3"]
    for addr in addresses:
        audit_logging.log(
          user,
          "shared.oidc.auth.HelsinkiOIDCAuthenticationBackend",
          Operation.READ,
          user,
          get_time=fixed_datetime,
          ip_address=addr
        )

    assert AuditLogEntry.objects.count() == 3

    new_sent_log = AuditLogEntry.objects.all()[0]
    expired_unsent_log = AuditLogEntry.objects.all()[1]
    expired_sent_log = AuditLogEntry.objects.all()[2]

    new_sent_log.markAsSent()

    expired_unsent_log.created_at = timezone.now() - timedelta(days=35)
    expired_unsent_log.save()

    expired_sent_log.created_at = timezone.now() - timedelta(days=35)
    expired_sent_log.markAsSent()

    clear_audit_log_entries()
    assert AuditLogEntry.objects.count() == 2
    assert AuditLogEntry.objects.filter(id=new_sent_log.id).exists()
    assert AuditLogEntry.objects.filter(id=expired_unsent_log.id).exists()
