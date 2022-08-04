import csv
import datetime
import time
from threading import Thread
from colorama import Fore, Style, init
from binance.client import Client
from keys import API_KEY, API_SECRET
import webbrowser


class Candle:
    google_path = 'C:/Program Files/Google/Chrome/Application/chrome.exe %s'

    # 1 - TIME
    # 2 - OPEN
    # 3 - HIGH
    # 4 - LOW
    # 5 - CLOSE
    # 6 - TICKER VOLUME
    # 7 - CLOSE TIME
    # 8 - USDT VOLUME

    def __init__(self, ticker, vol24, client):
        self._candle_before = ''
        self._candle_current = ''
        self._candle_future = ''
        self._time = ''
        self.session = client
        self._ticker = ticker
        self._vol24 = vol24
        self._req_tries = 0
        self.url = f'https://www.binance.com/en/trade/{self.ticker[:-4:]}_usdt?theme=dark&type=spot'

    def get_ticker_data(self):
        self.req_tries += 1
        if self.req_tries <= 3:
            try:
                temp_data = self.session.get_historical_klines(f"{self.ticker}", Client.KLINE_INTERVAL_1MINUTE,
                                                               "3 minute ago UTC")
                self.candle_before = temp_data[0]
                self.candle_current = temp_data[1]
                self.candle_future = temp_data[2]
                self.time = datetime.datetime.utcfromtimestamp(float(self.candle_current[0]) / 1000 + 36000).strftime(
                    '%Y-%m-%d %H:%M:%S')
                if not all((self.candle_before[0], self.candle_current[0], self.candle_future[0])):
                    if not all((self.candle_before[7], self.candle_current[7], self.candle_future[7])):
                        self.get_ticker_data()
            except Exception as ex:
                self.get_ticker_data()

    def check_requirements(self):
        if float(self.candle_current[1]) < float(self.candle_future[1]):
            if float(self.candle_current[7]) / float(self.candle_before[7]) >= 4:
                if float(self.candle_current[7]) >= 50000:
                    return True
                return False

    def open_browser_tab(self):
        webbrowser.get(self.google_path).open(self.url)

    @property
    def candle_before(self):
        return self._candle_before

    @candle_before.setter
    def candle_before(self, candle):
        self._candle_before = candle

    @property
    def candle_current(self):
        return self._candle_current

    @candle_current.setter
    def candle_current(self, candle):
        self._candle_current = candle

    @property
    def candle_future(self):
        return self._candle_future

    @candle_future.setter
    def candle_future(self, candle):
        self._candle_future = candle

    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        self._time = value

    @property
    def req_tries(self):
        return self._req_tries

    @req_tries.setter
    def req_tries(self, value):
        self._req_tries = value

    @property
    def ticker(self):
        return self._ticker

    @property
    def vol24(self):
        return self._vol24


def get_all_tickers(client, excluded_words):
    for ticker in client.get_all_tickers():
        if ticker['symbol'][-4:] == 'USDT':
            if not any(word in ticker['symbol'] for word in excluded_words):
                if ticker['symbol'][-6:-4] != 'UP':
                    if ticker['symbol'][-8:-4] != 'DOWN':
                        yield ticker['symbol']


def thread_main(ticker, client):
    volume24 = float(client.get_ticker(symbol=ticker)['quoteVolume'])
    if volume24 > 20000000:
        candle = Candle(ticker, volume24, client)
        candle.get_ticker_data()
        if candle.check_requirements():
            CANDLES.append(candle)
            candle.open_browser_tab()


def main():
    session = Client(
        api_key=API_KEY,
        api_secret=API_SECRET)

    for ticker in get_all_tickers(session, excluded_tickers):
        TICKERS.append(ticker)

    for ticker in TICKERS:
        THREADS.append(Thread(target=thread_main, args=(ticker, session)))

    for thread in THREADS:
        thread.start()

    for thread in THREADS:
        thread.join()

    CANDLES.sort(key=lambda x: x.vol24, reverse=True)

    if len(CANDLES) > 0:
        now = round(datetime.datetime.now().timestamp() * 1000)
        with open(f'{now}.csv', 'w') as f:

            writer = csv.writer(f)
            print(f'{Fore.GREEN}CSV file created {now}.csv{Style.RESET_ALL}')

            for candle in CANDLES:
                writer.writerow((candle.ticker, candle.vol24, candle.time))
                print(f'{Fore.GREEN}{candle.ticker},{candle.vol24},{candle.time}{Style.RESET_ALL}')


def countdown(am_time, minute_now):
    while not 0 == am_time:
        print(f'\rSleeping for {am_time - 1} seconds', end='')
        am_time -= 1
        time.sleep(1)

    print(f'. Round {minute_now}. Finished')


if __name__ == '__main__':
    round_counter = 0
    init(convert=True)
    start_time = datetime.datetime.now().second
    print(f'{Fore.CYAN}Sleeping to start, calibrating time{Style.RESET_ALL}')
    while not (10 <= start_time <= 15):
        time.sleep(1)
        start_time = datetime.datetime.now().second

    while True:
        round_counter += 1
        excluded_tickers = ['BUSD', 'USDC', 'TUSD', 'USTC', 'USDP', 'DAI', 'SVU', 'BEAR', 'BULL', 'EUR']
        TICKERS = []
        THREADS = []
        CANDLES = []
        start_time = datetime.datetime.now().timestamp() * 1000
        main()
        finish_time = datetime.datetime.now().timestamp() * 1000
        time_delta = 60 - (finish_time - start_time) / 1000

        t = Thread(target=countdown, args=(int(time_delta), round_counter))
        t.run()
        time.sleep(time_delta - int(time_delta))
