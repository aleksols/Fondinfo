import threading
from datetime import date

from selenium import webdriver
from bs4 import BeautifulSoup
import time
import html.parser

from selenium.webdriver.chrome.options import Options
from database import Database


class Fondinfo:

    def __init__(self):
        self.db = Database(local=True)
        self.my_funds = {}
        self.load_funds()


    def load_funds(self):
        self.my_funds = self.db.get_all_fund_base_info()

    def get_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        return webdriver.Chrome("/usr/local/bin/chromedriver", options=chrome_options)

    def add_current_price(self, fund, url):
        driver = self.get_driver()
        driver.get(url)
        soup = None
        while soup is None:
            content = driver.page_source
            soup = BeautifulSoup(content, features="html.parser").find("div", attrs={"class": "number LAST"})
            time.sleep(0.5)
        price = soup.text
        price = price.replace("\xa0", "").replace(",", ".")
        price = float(price)
        self.db.add_daily_value(fund, price)
        driver.close()

    def add_fund(self, fund_name, amount, invested, url):
        self.db.add_purchase(fund_name, amount, invested, url)
        self.add_prices()
        self.load_funds()

    # def add_current_price(self):
    #     for fund, values in self.my_funds.items():
    #         page_content = self.get_page_content(values[2])
    #         price = page_content.find("div", attrs={"class": "number LAST"}).text
    #         price = price.replace("\xa0", "").replace(",", ".")
    #         price = float(price)
    #         self.db.add_daily_value(fund, price * values[0])
    #         self.load_funds()

    def add_prices(self):
        threads = []
        for fund, values in info.my_funds.items():
            url = values[-1]
            t = threading.Thread(target=self.add_current_price, args=(fund, url))
            t.start()
            threads.append(t)

        [t.join() for t in threads]

    def calculate_total_earning(self):
        earnings = 0
        for fund, values in self.my_funds.items():
            amount = values[0]
            invested = values[1]
            current_value = self.db.get_daily_price(fund, str(date.today()))
            earnings += amount * current_value - invested
        return earnings




if __name__ == '__main__':
    info = Fondinfo()
    # info.add_fund("Storebrand Indeks - Alle Markeder", 8.054933, 20000,
    #               "https://bors.e24.no/#!/instrument/SP-IDXAM.OSE")
    # info.add_fund("KLP AKSJE VERDEN INDEKS", 3.654736, 10000, "https://bors.e24.no/#!/instrument/KL-AVIND.OSE")
    # info.add_fund("Storebrand Indeks - Norge", 13.456056, 20000, "https://bors.e24.no/#!/instrument/SP-INDNO.OSE")
    # earnings = info.calculate_total_earning()
    # print(earnings)
    # info.driver.close()
    start = time.time()
    info.add_prices()
    # info.add_fund("KLP AKSJEASIA INDEKS III", 6.792743, 10000, "https://bors.e24.no/#!/instrument/KL-AKAI3.OSE")
    print(time.asctime())
    print("Earning", info.calculate_total_earning())
    print(time.time() - start)
