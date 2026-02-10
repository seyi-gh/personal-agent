import json
from source.Deco import Deco

@Deco.InternalError()
def json_load(path: str):
  return json.load(open(path))

@Deco.InternalError()
def json_dump(obj, path: str):
  return json.dump(obj, open(path, 'w'), indent=2)

@Deco.InternalError()
def open_read(path: str):
  return open(path, 'r').read()