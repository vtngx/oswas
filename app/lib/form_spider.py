import exrex
import random
import string
from datetime import datetime
from .constants import InputTypes
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class FormSpider:

  def __init__(self, max_tries, max_wait, driver):
    self.max_tries = max_tries
    self.max_wait = max_wait
    self.driver = driver

  def find_elements_select(self):
    n = 1
    while(True):
      try:
        selects = WebDriverWait(self.driver, self.max_wait).until(
          EC.presence_of_all_elements_located((
            By.CSS_SELECTOR,
            'form select'
          )),
        )
        return selects
      except:
        # print(f'finding select {n}')
        if n >= self.max_tries:
          return []
        n += 1
  
  def find_elements_input(self):
    n = 1
    while(True):
      try:
        inputs = WebDriverWait(self.driver, self.max_wait).until(
          EC.presence_of_all_elements_located((
            By.CSS_SELECTOR,
            'form input[type]:not([type=hidden]):not([type=submit]):not([hidden])'
          )),
        )
        return inputs
      except:
        # print(f'finding input {n}')
        if n >= self.max_tries:
          return []
        n += 1

  def find_elements_textarea(self):
    n = 1
    while(True):
      try:
        textareas = WebDriverWait(self.driver, self.max_wait).until(
          EC.presence_of_all_elements_located((
            By.CSS_SELECTOR,
            'form textarea'
          )),
        )
        return textareas
      except:
        # print(f'finding textarea {n}')
        if n >= self.max_tries:
          return []
        n += 1

  def find_elements_submit(self):
    n = 1
    while(True):
      try:
        submits = WebDriverWait(self.driver, self.max_wait).until(
          EC.presence_of_all_elements_located((
            By.CSS_SELECTOR,
            'form button[type="submit"], input[type="submit"]'
          )),
        )
        return submits
      except:
        # print(f'finding submit {n}')
        if n >= self.max_tries:
          return []
        n += 1

  def fill_select(self, select_element):
    try:
      [name, id] = [
        select_element.get_attribute('name'),
        select_element.get_attribute('id')
      ]

      if name:
        selector = (By.NAME, name)
      elif id:
        selector = (By.ID, id)

      if selector:
        select_element = WebDriverWait(self.driver, self.max_wait).until(
          EC.element_to_be_clickable(selector)
        )

      s = Select(select_element)
      s.select_by_index(1)
    except: 
      pass

  def fill_input(self, input_element):
    try:
      [name, id, type, pattern] = [
        input_element.get_attribute('name'),
        input_element.get_attribute('id'),
        input_element.get_attribute('type'),
        input_element.get_attribute('pattern')
      ]

      selector = None
      dummy_data = None
      if name:
        selector = (By.NAME, name)
      elif id:
        selector = (By.ID, id)

      if pattern:
        dummy_data = exrex.getone(pattern)

      if type == InputTypes.CHECKBOX:
        if selector:
          input_element = WebDriverWait(self.driver, self.max_wait).until(
            EC.element_to_be_clickable(selector)
          )
        input_element.click()
      elif type == InputTypes.COLOR:
        if selector:
          input_element = WebDriverWait(self.driver, self.max_wait).until(
            EC.visibility_of_element_located(selector)
          )
        input_element.clear()
        input_element.send_keys(str("%06x" % random.randint(0, 0xFFFFFF)))
      elif type == InputTypes.DATE:
        if selector:
          input_element = WebDriverWait(self.driver, self.max_wait).until(
            EC.visibility_of_element_located(selector)
          )
        input_element.clear()
        input_element.send_keys(datetime.today().strftime('%Y-%m-%d'))
      elif type == InputTypes.DATETIME_LOCAL:
        if selector:
          input_element = WebDriverWait(self.driver, self.max_wait).until(
            EC.visibility_of_element_located(selector)
          )
        input_element.clear()
        input_element.send_keys(datetime.today().strftime('%Y-%m-%dT%H:%M'))
      elif type == InputTypes.EMAIL:
        if selector:
          input_element = WebDriverWait(self.driver, self.max_wait).until(
            EC.visibility_of_element_located(selector)
          )
        input_element.clear()
        input_element.send_keys(''.join(random.choice(string.ascii_letters) for x in range(7)) + "@gmail.com")
      elif type == InputTypes.MONTH:
        if selector:
          input_element = WebDriverWait(self.driver, self.max_wait).until(
            EC.visibility_of_element_located(selector)
          )
        input_element.clear()
        input_element.send_keys(datetime.today().strftime('%Y-%m'))
      elif type == InputTypes.NUMBER:
        if selector:
          input_element = WebDriverWait(self.driver, self.max_wait).until(
            EC.visibility_of_element_located(selector)
          )
        input_element.clear()
        input_element.send_keys(str(random.randint(0, 100000)))
      elif type == InputTypes.PASSWORD:
        if selector:
          input_element = WebDriverWait(self.driver, self.max_wait).until(
            EC.visibility_of_element_located(selector)
          )
        input_element.clear()
        input_element.send_keys(''.join(random.choice(string.ascii_letters + string.digits + "!@#$%^&*()") for i in range(10)))
      elif type == InputTypes.RADIO:
        if selector:
          input_element = WebDriverWait(self.driver, self.max_wait).until(
            EC.visibility_of_element_located(selector)
          )
        input_element.click()
      elif type == InputTypes.RANGE:
        pass
      elif type == InputTypes.SEARCH:
        if selector:
          input_element = WebDriverWait(self.driver, self.max_wait).until(
            EC.visibility_of_element_located(selector)
          )
        input_element.clear()
        if dummy_data:
          input_element.send_keys(dummy_data)
        else:
          input_element.send_keys('search')
      elif type == InputTypes.TEXT:
        if selector:
          input_element = WebDriverWait(self.driver, self.max_wait).until(
            EC.visibility_of_element_located(selector)
          )
        input_element.clear()
        if pattern:
          input_element.send_keys(dummy_data)
        else:
          input_element.send_keys('test')
      elif type == InputTypes.TEL:
        if selector:
          input_element = WebDriverWait(self.driver, self.max_wait).until(
            EC.visibility_of_element_located(selector)
          )
        input_element.clear()
        if pattern:
          input_element.send_keys(dummy_data)
        else:
          input_element.send_keys('0384846791')
      elif type == InputTypes.TIME:
        if selector:
          input_element = WebDriverWait(self.driver, self.max_wait).until(
            EC.visibility_of_element_located(selector)
          )
        input_element.clear()
        input_element.send_keys(datetime.today().strftime('%H:%M'))
      elif type == InputTypes.URL:
        if selector:
          input_element = WebDriverWait(self.driver, self.max_wait).until(
            EC.visibility_of_element_located(selector)
          )
        input_element.clear()
        if pattern:
          input_element.send_keys(dummy_data)
        else:
          input_element.send_keys('https://example.com/')
      # print(f'filled input type {type}')
    except:
      # print(f"fill error {type} {selector}")
      pass

  def fill_textarea(self, textarea_element):
    try:
      [name, id] = [
        textarea_element.get_attribute('name'),
        textarea_element.get_attribute('id')
      ]

      if name:
        selector = (By.NAME, name)
      elif id:
        selector = (By.ID, id)

      if selector:
        textarea_element = WebDriverWait(self.driver, self.max_wait).until(
          EC.visibility_of_element_located(selector)
        )

      textarea_element.send_keys(('textarea'))
    except:
      pass