from flask import Response
from google.cloud import firestore
import os


def AddFirebaseEntry(collection, docId, data):
    db = firestore.Client()
    db.collection(collection).document(docId).create(data)


def AddTransaction(request):
    # Check if environmental variables set
    varNames = ["VALID_USERNAME", "VALID_PASSWORD"]
    varList = {}
    for i, variable in enumerate(varNames):
        value = os.environ.get(variable)
        if value is None or value == '':
            message = f'failed - environmental variable {(i+1)} not set'
            print(message)
            return Response(message, status=500)
        varList[variable] = value

    # Try to get json from post
    request_json = request.get_json()
    if request_json is None:
        message = "failed - json"
        print(message)
        return Response(message, status=400)

    # Authenticate request
    transaction = {}
    if all(key in request_json for key in ["username", "password", "transaction"]):
        # Validate username and password
        if request_json["username"] != varList["VALID_USERNAME"] \
        or request_json["password"] != varList["VALID_PASSWORD"]:
            message = "unauthorised - invalid credentials"
            print(message)
            return Response(message, status=401)

        transaction = request_json["transaction"]

    # If minimum number of transaction fields set
    if all(key in transaction for key in ["accountNumber", "centsAmount", "dateTime"]):
        collection = "transactions"
        dateString = transaction["dateTime"].replace(
            "-", "").replace(":", "").replace(".", "-").replace("T", "-").replace("Z", "-")
        docId = dateString + transaction["accountNumber"]

        try:
            AddFirebaseEntry(collection, docId, transaction)
            return Response("ok", status=200)
        except Exception as e:
            print(e)
            return Response("failed", status=500)

    # Finally fail
    message = "failed - invalid data"
    print(message)
    return Response(message, status=400)
