import sys
import traceback
from source.Colors import Colors as c

class Deco:
  @staticmethod
  def InternalError(
    print_: bool=True,
    exit: bool=True,
    ret_value=None
  ):
    def decorator(func):
      def wrapper(*args, **kwargs):
        try:
          return func(*args, **kwargs)
        except Exception as e:
          tb = traceback.format_exc()
          c.format(
            f'Error: {func}\n{tb}',
            c.error,
            print_
          )
          if exit: sys.exit(1)
          return ret_value
      return wrapper
    return decorator