import colorama as co

reset_color = co.Style.RESET_ALL

class Colors:
  color = co.Fore
  error = color.RED

  @staticmethod
  def format(message: str, color: str, print_: bool=False):
    ret_message = color + message + reset_color
    if print_: print(ret_message)
    return ret_message