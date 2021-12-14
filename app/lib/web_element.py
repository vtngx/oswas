class WebElementObj:
  def __init__(self, type, element):
    self.type = type
    self.element = element

  @staticmethod
  def web_ele_2_input(element):
    return WebElementObj('input', element)

  @staticmethod
  def web_ele_2_select(element):
    return WebElementObj('select', element)

  @staticmethod
  def web_ele_2_textarea(element):
    return WebElementObj('textarea', element)