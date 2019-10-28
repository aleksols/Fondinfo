import pymongo
import json
from datetime import date


class Database:
    def __init__(self):
        with open("./dbconfig.json", "r") as file:
            dbconfig = json.load(file)

        self.client = pymongo.MongoClient(dbconfig["client"])
        self.db = self.client["fondinfo"]
        self.purchase_info = self.db["purchase_info"]
        self.history = self.db["history"]

    def add_purchase(self, fund_name, amount, invested, url):
        if self.key_exist(fund_name, self.purchase_info):
            self.purchase_info.update_one({"_id": fund_name}, {"$inc": {"amount": amount, "invested": invested}})
        else:
            self.purchase_info.insert_one({"_id": fund_name, "amount": amount, "invested": invested, "url": url})

    def get_single_fund_base_info(self, fund_name):
        # TODO ref todo in get_all_fund_base_info
        fund = self.purchase_info.find_one({"_id": fund_name})

        return {fund["_id"]: (fund["amount"], fund["invested"], fund["url"])}

    @staticmethod
    def key_exist(key, collection):
        return collection.count_documents({"_id": key}) > 0

    def get_all_fund_base_info(self):
        out = {}
        cursor = self.purchase_info.find()
        for element in cursor:
            out.update(self.get_single_fund_base_info(element["_id"]))  # TODO this is stupid
        return out

    def add_daily_value(self, fund_name, value):
        key = {"name": fund_name, "date": str(date.today())}
        self.history.update_one({"_id": key}, {"$set": {"value": value}}, upsert=True)

    def get_daily_price(self, fund_name, date):
        key = {"name": fund_name, "date": date}
        if self.key_exist(key, self.history):
            return self.history.find_one({"_id": key})["value"]


if __name__ == '__main__':
    db = Database()
    # db.add_purchase("Storebrand Indeks - Alle Markeder", 8.054933, 20000,
    #                 "https://bors.e24.no/#!/instrument/SP-IDXAM.OSE")
    # db.add_purchase("KLP AKSJE VERDEN INDEKS", 3.654736, 10000, "https://bors.e24.no/#!/instrument/KL-AVIND.OSE")
    # db.add_purchase("Storebrand Indeks - Norge", 13.456056, 20000, "https://bors.e24.no/#!/instrument/SP-INDNO.OSE")
    # print(db.get_single_fund_base_info("Storebrand Indeks - Alle Markeder"))
    print(db.get_all_fund_base_info())
