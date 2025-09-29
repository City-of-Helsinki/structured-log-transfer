import datetime
import json

import pytest
from log_transfer.utils import changes_as_json_str


def test_changes_as_json_str():
    as_dict = {"value": "hello"}
    as_str = json.dumps(as_dict)
    invalid = datetime.datetime(2025, 10, 10)

    assert changes_as_json_str(as_str) == as_str
    assert changes_as_json_str(as_dict) == as_str

    with pytest.raises(TypeError) as ex:
        changes_as_json_str(invalid)

    assert ex.match("Expected 'str | dict', got 'datetime'")