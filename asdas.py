from pyshadow.main import Shadow
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement

browser = webdriver.Chrome()
browser.get('https://ing.ingdirect.es/pfm/#login')
shadow = Shadow(browser)

shadow.set_explicit_wait(20, 5)
shadow.find_element("#aceptar").click()
element = shadow.find_element("#ing-uic-native-input_0")
print(element.get_attribute('id'))
