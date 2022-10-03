from datetime import datetime, timezone
from typing import Callable

from pytest import fixture

#from shared.common.tests.conftest import *  # noqa

from log_transfer.tests.factories import (
    UserFactory,
)


@fixture
def fixed_datetime() -> Callable[[], datetime]:
    return lambda: datetime(2020, 6, 1, tzinfo=timezone.utc)

@fixture()
def user():
    return UserFactory()
    