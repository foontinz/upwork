import requests
from main import DataBaseInterface

db = DataBaseInterface()

headers = {
    "Accept": "*/*",
    "Accept-Encoding": "Accept-Encoding: gzip, deflate, br",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
}

for product in db.get_all_products():
    if product[0]:

        ebay_id = product[1]
        ecommerce_website = product[2]
        stock_word = product[3]

        resp = requests.get(ecommerce_website, headers=headers)
        html = resp.text
        if stock_word in html:
            print('DA SUCCHKAA')
