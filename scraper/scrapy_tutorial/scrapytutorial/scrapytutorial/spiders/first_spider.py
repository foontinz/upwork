import scrapy
from urllib.parse import urlencode

API_KEY = '3d780e97ae570c7d906b94e1da17ab99'


def get_scraperapi_url(url):
    payload = {'api_key': API_KEY, 'url': url}
    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    return proxy_url


class WinesSpider(scrapy.Spider):
    name = "minfin"

    def start_requests(self):

        urls = ['https://minfin.com.ua/ua/currency/auction/usd/buy/odessa/']

        for url in urls:
            yield scrapy.Request(url=get_scraperapi_url(url), callback=self.parse)

    def parse(self, response):
        for exchange in response.css('div.CardWrapper'):
            yield {
                'price': exchange.css('div.point-currency').css('div::text').get(),
                'phone': exchange.css('div.icons-point').css('button.action').css('a').attrib['href'][5:],
                'link': f'https://minfin.com.ua/ua/currency/auction/exchanger/odessa/id-{exchange.attrib["id"]}/'
            }
        yield response.follow('https://minfin.com.ua/ua/currency/auction/usd/sell/odessa/', callback=self.parse)
