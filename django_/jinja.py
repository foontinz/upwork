import time

from seleniumwire import webdriver

# To use Chrome browser


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')

driver = webdriver.Chrome(options=chrome_options,
    executable_path="C:\\Users\dimay\\PycharmProjects\\upwork_reloaded\\spreadsheet_japan_eBay\\chromedriver.exe")

driver.get("https://jp.mercari.com/item/m24682736412")
driver.wait_for_request("https://api.mercari.jp/items/get", timeout=30)


for request in driver.requests:
    if 'get?id=' in request.url:
        for item in request.headers.items():
            if item[0] == 'dpop':
                print(item[1])
