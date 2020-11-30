import datetime
import json
import typing
import hashlib


class Transaction:
    logs = None
    _id = None
    account_number = None
    merchant = None
    card = None
    reference = None
    _type = None
    currency_code = "zar"
    cents_amount = 0
    _datetime = None
    category = None
    hash = None

    def __init__(self, transaction=None, transaction_id=None):
        self._id = transaction_id
        self.process_transaction(transaction)
        self.calculate_hash(transaction)

    #     self.process_log(transaction_log)

    # def convert_epoch_to_datetime(self, epoch):
    #     date = datetime.datetime.fromtimestamp(epoch)
    #     return date

    # def convert_log(self, log):
    #     result = json.loads(log)
    #     return result

    # def process_log(self, log=None):
    #     if not log:
    #         return

    #     log = self.convert_log(log)
    #     self.account_number = log.get("accountNumber", None)
    #     self.merchant = log.get("merchant", None)
    #     self.card = log.get("card", None)
    #     self.reference = log.get("reference", None)
    #     self._type = log.get("type", None)
    #     self.currency_code = log.get("currencyCode", None)
    #     self.cents_amount = int(log.get("centsAmount", 0))
    #     self._datetime = datetime.datetime.strptime(log.get("dateTime", None), "%Y-%m-%dT%H:%M:%S.%fZ")

    def process_transaction(self, transaction):
        self.account_number = transaction["accountNumber"]
        self.merchant = transaction["merchant"]
        self.card = transaction["card"]
        self.reference = transaction["reference"]
        self._type = transaction["type"]
        self.currency_code = transaction["currencyCode"]
        self.cents_amount = int(transaction["centsAmount"])
        self.category = transaction["budget_category"]
        self._datetime = transaction["dateTime"]

    def calculate_hash(self, transaction):
        pass