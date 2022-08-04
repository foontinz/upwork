import csv

import requests
from bs4 import BeautifulSoup
from threading import Thread


class Scraper:
    companies = []

    def __init__(self, city):
        self.url = f'https://www.houzz.com/professionals/hardwood-flooring-dealers/c/{city}/p/0'
        self.soup = self.create_soup()

    def request_url(self):
        return requests.get(self.url).text

    def create_soup(self):
        return BeautifulSoup(self.request_url(), 'html.parser')

    def get_all_companies(self) -> list:
        return self.soup.find_all('li', class_='hz-pro-search-results__item')

    def move_page(self, href):
        self.url = f'https://www.houzz.com{href}'
        self.soup = self.create_soup()

    def get_next_page(self) -> bool:
        a_tag = self.soup.find('a', class_='hz-pagination-link hz-pagination-link--next')
        if a_tag:
            self.move_page(a_tag["href"])
            return True
        return False


def thread_main(city):
    print('New city')
    response = True
    scraper = Scraper(city)
    while response:
        print('next page')
        Scraper.companies.extend(scraper.get_all_companies())
        response = scraper.get_next_page()


def main():
    threads = []
    cities = ['New-York', 'Los-Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'Dallas', 'Austin',
              'Columbus', 'San-Diego', 'Detroit', 'Denver', 'Washington', 'Boston', 'Jacksonville', 'Charlotte',
              ''
              ]

    for city in cities:
        threads.append(Thread(target=thread_main, args=(city,)))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    companies = list(set(Scraper.companies))
    with open('output.csv', 'w') as file:
        csvwriter = csv.writer(file)
        for company in companies:
            csvwriter.writerow((company.find_all_next('a', class_='hz-pro-ctl')[0]['href'],))


if __name__ == '__main__':
    main()
