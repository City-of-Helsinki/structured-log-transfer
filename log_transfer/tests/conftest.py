from datetime import datetime, timezone
from typing import Callable

from pytest import fixture

from log_transfer.tests.audit_logging import delete_elastic_index
from log_transfer.tests.factories import UserFactory


@fixture
def fixed_datetime() -> Callable[[], datetime]:
    return lambda: datetime(2020, 6, 1, tzinfo=timezone.utc)


@fixture
def user():
    return UserFactory()


@fixture(autouse=True)
def clear_elastic_search_index():
    # Database is cleared between tests, but elastic search is not,
    # so the app attempts to send to elastic using old id numbers.
    # Solution: delete the index and start over for each test.
    delete_elastic_index()
