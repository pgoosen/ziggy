import uuid
import json
import re
from datetime import datetime
import os
import base64

from flask import Response
from google.cloud import firestore
from google.cloud import pubsub_v1

from merchant import merchant

def CategoriseTransaction(event, context):
    """Triggered by a change to a Firestore document.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    if not event:
        print("No data in event payload")
        return Response("No data in event payload", status=500)

    try:
        reference = event["value"]["fields"]["reference"]["stringValue"]
    except:
        reference = None

    if reference == "saving":
        category = "41af5158-5dcd-41c7-857f-9f22549fd4cc"
    else:
        transaction = format_dictionary(event["value"]["fields"])
        category = get_merchant_category(transaction["merchant"])

    transaction_id =  event["value"]["name"].split("/")[-1]

    # Save transaction to db
    if category:
        updated_info = {"budget_category": category}
        try:
            update_firebase_entry("transactions", transaction_id, updated_info)
            send_transaction_notification(transaction_id)
            return "ok"
        except Exception as exc:
            print(exc)
            send_transaction_notification(transaction_id)
            return Response("failed", status=500)

    send_transaction_notification(transaction_id)
    return "ok"


def format_dictionary(firebase_payload):
    """
    Format the firebase event triggered payload into a more usable dictionary.
    Args:
        firebase_payload (dict): firebase event triggered payload to format
    Returns:
        details (dict): formatted dictionary
    """
    details = {}

    details["accountNumber"] = firebase_payload["accountNumber"]["stringValue"]
    details["centsAmount"] = firebase_payload["centsAmount"]["integerValue"]
    details["currencyCode"] = firebase_payload["currencyCode"]["stringValue"]
    try:
        details["dateTime"] = firebase_payload["dateTime"]["timestampValue"]
    except KeyError:
        try:
            details["dateTime"] = firebase_payload["dateTime"]["stringValue"]
        except:
            details["dateTime"] = datetime.now()

    details["reference"] = firebase_payload["reference"]["stringValue"]
    details["type"] = firebase_payload["type"]["stringValue"]

    card_details = firebase_payload["card"]["mapValue"]["fields"]
    details["card"] =  {}
    details["card"]["id"] = card_details["id"]["stringValue"]

    merchant_details = firebase_payload["merchant"]["mapValue"]["fields"]["category"]["mapValue"]["fields"]
    details["merchant"] = {}
    details["merchant"]["category"] = {}
    details["merchant"]["category"]["code"] = merchant_details["code"]["stringValue"]
    details["merchant"]["category"]["key"] = merchant_details["key"]["stringValue"]
    details["merchant"]["category"]["name"] = merchant_details["name"]["stringValue"]

    details["merchant"]["city"] = firebase_payload["merchant"]["mapValue"]["fields"]["city"]["stringValue"]

    country_details = firebase_payload["merchant"]["mapValue"]["fields"]["country"]["mapValue"]["fields"]
    details["merchant"]["country"] = {}
    details["merchant"]["country"]["alpha3"] = country_details["alpha3"]["stringValue"]
    details["merchant"]["country"]["code"] = country_details["code"]["stringValue"]
    details["merchant"]["country"]["name"] = country_details["name"]["stringValue"]

    details["merchant"]["name"] = firebase_payload["merchant"]["mapValue"]["fields"]["name"]["stringValue"]

    return details


def get_merchant_category(merchant_details):
    """"
    Determine the budget category for a merchant based on merchant code. Return None if merchant does not belong to a category.
    """
    category = None 
    code = merchant_details["category"]["code"]

    if merchant.MERCHANT_CATEGORIES[code]:
        merchant_category = merchant.MERCHANT_CATEGORIES[code]
    else:
        merchant_category = None

    if "category" in merchant_category:
        category = merchant_category["category"]

    return category


def update_firebase_entry(collection, docId, data):
    # Update firebase document
    db = firestore.Client()
    db.collection(collection).document(docId).update(data)


def send_transaction_notification(transaction_id):
    """
    Post a notification to Google PubSub with the transactions ids.
    """
    project_id = os.environ.get("PROJECT_ID", None)
    topic_id = os.environ.get("TOPIC_ID", None)

    if not project_id or not topic_id:
        print("Unable to post to PubSub. No project_id/topic_id set.")
        return

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    payload = { 
        "transaction_ids": [transaction_id]
    }

    data = json.dumps(payload).encode("utf-8")
    publisher.publish(topic_path, data)



