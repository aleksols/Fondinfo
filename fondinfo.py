from selenium import webdriver
from bs4 import BeautifulSoup
import time

from selenium.webdriver.chrome.options import Options
from database import Database


class Fondinfo:

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=chrome_options)
        self.db = Database()
        self.my_funds = {}
        self.load_funds()

    def load_funds(self):
        self.my_funds = self.db.get_all_fund_base_info()

    def get_page_content(self, url):
        self.driver.get(url)
        time.sleep(5)
        content = self.driver.page_source
        soup = BeautifulSoup(content)
        return soup

    def add_fund(self, fund_name, amount, invested, url):
        self.db.add_purchase(fund_name, amount, invested, url)
        self.load_funds()

    def add_current_values(self):
        for fund, values in self.my_funds.items():
            page_content = self.get_page_content(values[2])
            price = page_content.find("div", attrs={"class": "number LAST"}).text
            price = price.replace("\xa0", "").replace(",", ".")
            price = float(price)
            self.db.add_daily_value(fund, price)
            self.load_funds()

    def calculate_total_earning(self):
        earnings = 0
        for fund, values in self.my_funds.items():
            page_content = self.get_page_content(values[2])
            price = page_content.find("div", attrs={"class": "number LAST"}).text
            price = price.replace("\xa0", "").replace(",", ".")
            price = float(price)
            earnings += price * values[0] - values[1]
        return earnings


if __name__ == '__main__':
    info = Fondinfo()
    # info.add_fund("Storebrand Indeks - Alle Markeder", 8.054933, 20000,
    #               "https://bors.e24.no/#!/instrument/SP-IDXAM.OSE")
    # info.add_fund("KLP AKSJE VERDEN INDEKS", 3.654736, 10000, "https://bors.e24.no/#!/instrument/KL-AVIND.OSE")
    # info.add_fund("Storebrand Indeks - Norge", 13.456056, 20000, "https://bors.e24.no/#!/instrument/SP-INDNO.OSE")
    earnings = info.calculate_total_earning()
    print(earnings)
    info.driver.close()
