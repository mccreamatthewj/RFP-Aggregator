# Indiana Crawler

import requests
from bs4 import BeautifulSoup

class IndianaCrawler:
    def __init__(self):
        self.start_url = 'https://www.in.gov/idoa/procurement/'

    def fetch_html(self, url):
        response = requests.get(url)
        return response.text

    def parse_data(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        # Add your parsing logic here

    def run(self):
        html = self.fetch_html(self.start_url)
        self.parse_data(html)

if __name__ == '__main__':
    crawler = IndianaCrawler()
    crawler.run()