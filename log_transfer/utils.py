import json
from typing import Union


def changes_as_json_str(changes: Union[str, dict]) -> str:
  if isinstance(changes, str):
    return changes
  
  if isinstance(changes, dict):
    return json.dumps(changes)
  
  value_type = type(changes).__name__

  raise TypeError(
      f"Invalid changes_as_json_str input. Expected 'str | dict', got '{value_type}'"
  )