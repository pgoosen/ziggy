import datetime
import json
import typing
import hashlib

class Transaction:
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