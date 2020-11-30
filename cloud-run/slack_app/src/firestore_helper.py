import uuid
from google.cloud import firestore
from flask import Response, jsonify

def GetTransactions(request_json):
    # request_json = request.get_json()
    db = firestore.Client()

    goals_ref = []
    docs = []
    if "doc_id" in request_json:
        goals_ref = db.collection(u'transactions').document(u'{}'.format(request_json["doc_id"]))
        doc = goals_ref.get()
        docs.append(doc)
    elif "transaction_ids" in request_json:
        for doc_id in request_json["transaction_ids"]:
            goals_ref = db.collection(u'transactions').document(u'{}'.format(doc_id))
            doc = goals_ref.get()
            docs.append(doc)
    else:
        goals_ref = db.collection(u'transactions')
        docs = goals_ref.stream()

    result = {}
    for i, doc in enumerate(docs):
        _doc = doc.to_dict()
        if request_json.get("only_uncategorised", False):
            if not ("budget_category" in _doc):
                _doc["doc_id"] = doc.id
                result[i] = _doc
        else:
            _doc["doc_id"] = doc.id
            result[i] = _doc

    return jsonify(result)

def GetGoals(request_json):
    # request_json = request.get_json()
    db = firestore.Client()

    goals_ref = []
    docs = []
    if "doc_id" in request_json:
        goals_ref = db.collection(u'goals').document(u'{}'.format(request_json["doc_id"]))
        doc = goals_ref.get()
        docs.append(doc)
        # print(docs)
    else:
        goals_ref = db.collection(u'goals')
        docs = goals_ref.stream()

    result = {}
    for i, doc in enumerate(docs):
        # print(doc.id)
        _doc = doc.to_dict()
        if request_json.get("active", False) is True:
            if _doc["active"] is True:
                _doc["doc_id"] = doc.id
                result[i] = _doc
        else:
            _doc["doc_id"] = doc.id
            result[i] = _doc

    return jsonify(result)

def DeleteGoals(request_json):

    # request_json = request.get_json()
    db = firestore.Client()
    goals_ref = db.collection(u'goals')

    # TODO Implement logging instead
    failed = False
    doc_ids = request_json.get("doc_ids", [])
    for _id in doc_ids:
        try:
            goals_ref.document(str(_id)).delete()
        except Exception as exc:
            failed = True

    if failed:
        return "failed"
    else:
        return "success"

def AddFirebaseEntry(collection, docId, data):
    db = firestore.Client()
    db.collection(collection).document(docId).create(data)

def UpdateFirebaseEntry(collection, docId, data):
    db = firestore.Client()
    db.collection(collection).document(docId).update(data)

def AddGoal(request_json):
    # Try to get json from post
    # request_json = request.get_json()
    if request_json is None:
        print("failed - json")
        return Response("failed - json", status=400)

    # If minimum number of fields set
    if all(key in request_json for key in ["goal_type", "active", "start_date", "end_date"]):
        try:
            AddFirebaseEntry("goals", str(uuid.uuid4()), request_json)
            return "ok"
        except Exception as e:
            print(e)
            return Response("failed", status=500)

    # Finally fail
    print("failed - incomplete data")
    return Response("failed - incomplete data", status=400)

def UpdateGoal(request_json, goal_uuid):
    # Try to get json from post
    # request_json = request.get_json()
    if request_json is None:
        print("failed - json")
        return Response("failed - json", status=400)

    # If minimum number of fields set
    if all(key in request_json for key in ["goal_type", "active", "start_date", "end_date"]):
        try:
            UpdateFirebaseEntry("goals", goal_uuid, request_json)
            return "ok"
        except Exception as e:
            print(e)
            return Response("failed", status=500)

    # Finally fail
    print("failed - incomplete data")
    return Response("failed - incomplete data", status=400)

def UpdateTransaction(request_json, transaction_uuid):
    # Try to get json from post
    # request_json = request.get_json()
    if request_json is None:
        print("failed - json")
        return Response("failed - json", status=400)

    # If minimum number of fields set
    if all(key in request_json for key in ["accountNumber", "card", "centsAmount", "dateTime", "merchant", "reference", "type"]):
        try:
            UpdateFirebaseEntry("transactions", transaction_uuid, request_json)
            return "ok"
        except Exception as e:
            print(e)
            return Response("failed", status=500)

    # Finally fail
    print("failed - incomplete data")
    return Response("failed - incomplete data", status=400)

def AvatarReport_PrepareData():
    db = firestore.Client()
    avatar_ref = db.collection(u'avatar')
    docs = avatar_ref.stream()
    result = {}
    for doc in docs:
        _doc = doc.to_dict()
        result[doc.id] = _doc
    avatar = result[list(result.keys())[0]]

    data = {
        "report": True,
        "current_hp": avatar.get("current_hp", 0),
        "current_xp": avatar.get("current_xp", 0),
        "level": avatar.get("level", 1),
        "xp_diff": 0,
        "hp_diff": 0,
        "level_diff": 0
    }
    return data
