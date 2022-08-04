

load_dotenv()
API_KEY = os.getenv('api_key')


class Ebay(object):
    def __init__(self, API_KEY):
        self.api_key = API_KEY
        self.connection = Connection(appid=)

    def fetch(self):
        pass

    def parse(self):
        pass


if __name__ == '__main__':
    e = Ebay(API_KEY)
    e.fetch()
    e.parse()
