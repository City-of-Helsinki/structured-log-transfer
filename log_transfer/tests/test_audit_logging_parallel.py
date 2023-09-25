import pytest
import time

from django.test import override_settings

from auditlog.models import LogEntry

from log_transfer.models import AuditLogEntry
from log_transfer.tests.audit_logging import search_entries_from_elastic_search, get_entries_from_elastic_search, delete_elastic_index
from log_transfer.tasks import send_audit_log_to_elastic_search
from log_transfer.enums import Operation
from log_transfer.tests import audit_logging
from log_transfer.tests.factories import UserFactory
from log_transfer.tests.utils.generators import generate_random_ip

from structuredlogtransfer.settings import AuditLoggerType

# 1 run for each worker
runs = [i for i in range(0, 2)]

AUDIT_LOG_COUNT=20

@pytest.mark.parametrize("run_count", runs)
@pytest.mark.PARALLEL_SINGLE_COLUMN_JSON
@pytest.mark.django_db(transaction=True, serialized_rollback=True)
@override_settings(
    AUDIT_LOGGER_TYPE=AuditLoggerType.SINGLE_COLUMN_JSON,
    CLEAR_AUDIT_LOG_ENTRIES=True,
)
def test_send_overlapping_audit_log(run_count, user, fixed_datetime, parallel_session_setup):  
    addresses = []
    for _ in range(AUDIT_LOG_COUNT):
        addresses.append(generate_random_ip())

    user = UserFactory()
    
    for addr in addresses:
        audit_logging.log(
            user,
            "shared.oidc.auth.HelsinkiOIDCAuthenticationBackend",
            Operation.READ,
            user,
            get_time=fixed_datetime,
            ip_address=addr,
        )

    number_of_audit_log_entries = AuditLogEntry.objects.count()
    
    # Each worker has some log entries to send
    assert number_of_audit_log_entries != 0
        
    send_audit_log_to_elastic_search()
    
    # Wait some time so all workers finished sending audit logs
    time.sleep(15)
    
    # Test search
    result = search_entries_from_elastic_search()
    hits = result["hits"]
    total = hits["total"]
    value = total["value"]
    assert value == AUDIT_LOG_COUNT*len(runs)


@pytest.mark.parametrize("run_count", runs)
@pytest.mark.PARALLEL_DJANGO_AUDITLOG
@pytest.mark.django_db(transaction=True, serialized_rollback=True)
@override_settings(
    AUDIT_LOGGER_TYPE=AuditLoggerType.DJANGO_AUDITLOG,
    CLEAR_AUDIT_LOG_ENTRIES=True,
)
def test_send_overlapping_audit_log__use_django_auditlog(run_count, user, fixed_datetime, parallel_session_setup):
    addresses = []
    for _ in range(AUDIT_LOG_COUNT):
        addresses.append(generate_random_ip())

    user = UserFactory()
    
    for addr in addresses:
        audit_logging.log(
            user,
            "shared.oidc.auth.HelsinkiOIDCAuthenticationBackend",
            Operation.READ,
            user,
            get_time=lambda: fixed_datetime,
            ip_address=addr,
            audit_logger_type=AuditLoggerType.DJANGO_AUDITLOG,
        )

    number_of_audit_log_entries = LogEntry.objects.count()
    
    # Each worker has some log entries to send
    assert number_of_audit_log_entries != 0
        
    send_audit_log_to_elastic_search()
    
    # Wait some time so all workers finished sending audit logs
    time.sleep(5)
    
    # Test search
    result = search_entries_from_elastic_search()
    hits = result["hits"]
    total = hits["total"]
    value = total["value"]
    assert value == AUDIT_LOG_COUNT*len(runs)