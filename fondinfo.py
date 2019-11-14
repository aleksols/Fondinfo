import threading
from datetime import date

import matplotlib
from selenium import webdriver
from bs4 import BeautifulSoup
import time
import matplotlib.pyplot as plt
import numpy as np

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
        time.sleep(4)
        while soup is None:
            content = driver.page_source
            soup = BeautifulSoup(content, features="html.parser").find("div", attrs={"class": "number LAST"})
            time.sleep(1)
        price = soup.text
        price = price.replace("\xa0", "").replace(",", ".")
        price = float(price)
        self.db.add_daily_value(fund, price)
        driver.close()

    def add_fund(self, fund_name, amount, invested, url):
        self.db.add_purchase(fund_name, amount, invested, url)
        self.add_prices()
        self.load_funds()


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

    def _get_datapoints(self):
        history = self.db.get_all_history()
        data_dict = {}
        for entry in history:
            key = entry["_id"]["name"]
            day = entry["_id"]["date"]
            value = entry["value"] * self.my_funds[key][0] - self.my_funds[key][1]
            if day not in data_dict.keys():
                data_dict[day] = {key: value}
            else:
                data_dict[day][key] = value

        return data_dict

    def plot_earnings(self):
        datapoints = self._get_datapoints()
        y_values = []
        for i in range((len(self.my_funds.keys()) + 1)):
            y_values.append([])
        x_values = []
        indices = {key: i for i, key in enumerate(self.my_funds.keys())}
        for date, funds in datapoints.items():
            for fund in self.my_funds.keys():
                if fund not in funds.keys():
                    y_values[indices[fund]].append(0)
            for fund, value in funds.items():
                y_values[indices[fund]].append(value)
            y_values[-1].append(sum(funds.values()))
            x_values.append(date)
        for y in y_values:
            print(y)
        matplotlib.use("TkAgg")
        for i, y in enumerate(y_values):
            print(y)
            k = "Total"
            for key, value in indices.items():
                if value == i:
                    k = key
                    break
            y_data = np.array(y)
            x_data = np.array(x_values)
            print(y_data.shape)
            print(x_data.shape)
            plt.plot(x_data, y_data, label=k)


        for y in range(1000, 13000, 1000):
            plt.plot(x_values, [y]*len(x_values), "r--")

        plt.show()





if __name__ == '__main__':
    info = Fondinfo()
    start = time.time()
    info.add_prices()
    print(time.asctime())
    print("Earning", info.calculate_total_earning())
    print(time.time() - start)
    data = info._get_datapoints()
    info.plot_earnings()
