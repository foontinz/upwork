import json

import requests
from bs4 import BeautifulSoup
from pprint import pprint

a = requests.get(
    "https://www.petfinder.com/member/us/ak/bettles/test12345-nj333/")
soup = BeautifulSoup(a.text, 'html.parser')
try:
    for i in soup.find("div", {"class": "vrArray vrArray_divided m-vrArray_6x"}).find_all("div"):
        if i.find("h2").text.strip() == "Our Mission":
            print(i.find("p").text.strip())
except:
    pass
