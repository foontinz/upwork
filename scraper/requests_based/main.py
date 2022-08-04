import requests
from bs4 import BeautifulSoup


def make_payload(query):
    payload = {'api_key': '3d780e97ae570c7d906b94e1da17ab99',
               'apiParams': {
                   "country_code": "ua"},
               'url': f'http://www.google.com{query}',
               }
    return payload


def make_request(payload):
    return requests.get('http://api.scraperapi.com', params=payload).text


def get_soup(html):
    return BeautifulSoup(html, 'html.parser')


def find_all_results_on_page(soup: BeautifulSoup):
    findings_text_containing = soup.find_all('div', class_="yuRUbf")
    findings_text_containing.extend(soup.find_all('div', class_="ct3b9e"))
    return findings_text_containing


def find_td_tag(soup: BeautifulSoup):
    return soup.find_all('td', class_='d6cvqb BBwThe')[1]


def find_a_tag(td_tag):
    return td_tag.find_all_next('a')[0]


def find_next_page_url(soup):
    return find_a_tag(find_td_tag(soup))['href']


payload = make_payload('/search?q=daxak+GO+GOG')
response = make_request(payload)
soup = get_soup(response)

for i in find_all_results_on_page(soup):
    print(i)

payload = make_payload(find_next_page_url(soup))
response = make_request(payload)
soup = get_soup(response)

for i in find_all_results_on_page(soup):
    print(i)


# with open("output.html", "r", encoding='utf-8') as file:
#     content = file.read()
#     soup = get_soup(content)
