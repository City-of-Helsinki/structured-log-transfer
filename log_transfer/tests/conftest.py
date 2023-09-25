from datetime import datetime, timezone
from typing import Callable

import pytest

from django.utils import timezone

from log_transfer.tests.audit_logging import delete_elastic_index

#from shared.common.tests.conftest import *  # noqa

from log_transfer.tests.factories import (
    UserFactory,
)

@pytest.fixture
def fixed_datetime() -> Callable[[], datetime]:
    return lambda: datetime(2020, 6, 1, tzinfo=timezone.utc)

@pytest.fixture()
def user():
    return UserFactory()

@pytest.fixture(scope='session')
@pytest.mark.PARALLEL_DJANGO_AUDITLOG
@pytest.mark.PARALLEL_SINGLE_COLUMN_JSON
def django_db_modify_db_settings():
    pass

@pytest.fixture(scope="session")
@pytest.mark.PARALLEL_DJANGO_AUDITLOG
@pytest.mark.PARALLEL_SINGLE_COLUMN_JSON
def parallel_session_setup():
    delete_elastic_index()
    yield
