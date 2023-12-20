import json
import os
from typing import Any, Dict, Optional


class StaticStrings:
  def __init__(self, json_file_path: Optional[str] = None) -> None:
      self._values: Dict[str, str] = {}
      if json_file_path and os.path.isfile(json_file_path):
          self.load_json(json_file_path)

  def __getattr__(self, key: str) -> str:
      if key in self._values:
          return self._values[key]
      else:
          raise AttributeError(f"{self.__class__.__name__} has no attribute '{key}'")

  def __setattr__(self, key: str, value: Any) -> None:
      if key in ('_values',):
          object.__setattr__(self, key, value)
      else:
          self._values[key] = str(value)

  def load_json(self, file_path: str) -> None:
      with open(file_path, "r") as file:
          data = json.load(file)
          if not isinstance(data, dict):
              raise ValueError("JSON file must contain a dictionary.")
          for key, value in data.items():
              if not isinstance(key, str) or not isinstance(value, str):
                  raise ValueError("JSON file must contain a dict with string keys and values.")
              self.set(key, value)

  def set(self, key: str, value: str) -> None:
      self._values[key] = str(value)
