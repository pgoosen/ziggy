from google.cloud import firestore
from google.cloud import pubsub_v1

import json
import base64
import os

from flask import jsonify
from datetime import datetime

from game_engine.transaction import Transaction
from game_engine.avatar import Avatar
from game_engine.goal import Goal


def ProcessTransaction(event, context):
    """
    Process transaction after they have been categorised
    """
    if not event.get("updateMask", None):
        print("no update")
        return "ok"

    if not "budget_category" in event["updateMask"]["fieldPaths"]:
        print("nothing to do")
        return "ok"

    event_format = format_dictionary(event["value"]["fields"])

    avatar = get_avatar()
    transaction_name = event["value"]["name"]
    transaction_id = transaction_name.split("/")[-1]
    transaction = Transaction(transaction=event_format, transaction_id=transaction_id)

    total_hp = 0
    total_xp = 0
    level = avatar.level

    goals = get_goals(active=True)
    for goal_id, goal_value in goals.items():
        goal = Goal(config=goal_value, doc_id=goal_id)
        goal.set_avatar(avatar)
        hp_impact, xp_impact = goal.match_transaction_to_goal(transaction)
        total_hp += hp_impact
        total_xp += xp_impact
        avatar = goal.avatar
        update_avatar(goal.avatar)

    avatar = get_avatar()
    level_diff = avatar.level - level
    send_avatar_notification(avatar, total_hp, total_xp, level_diff)

    return "ok"


def send_avatar_notification(avatar, hp_impact=0, xp_impact=0, level_diff=0):
    """"
    Send an avatar update slack notification
    """
    if hp_impact==0 and xp_impact==0 and level_diff==0:
        return

    project_id = os.environ.get("PROJECT_ID", None)
    topic_id = os.environ.get("TOPIC_ID", None)

    if not project_id or not topic_id:
        print("Environment variables not set")
        return
    
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)

    payload = { 
        "type": "avatar_update",
        "content": {
            "current_hp": avatar.current_hp,
            "current_xp": avatar.current_xp,
            "level": avatar.level,
            "xp_diff": xp_impact,
            "hp_diff": hp_impact,
            "level_diff": level_diff
        }
    }

    data = json.dumps(payload).encode("utf-8")
    publisher.publish(topic_path, data)


def get_avatar():
    """"
    Get avatar from database
    """
    db = firestore.Client()
    avatar_ref = db.collection(u'avatar')
    docs = avatar_ref.stream()

    result = {}
    for doc in docs:
        _doc = doc.to_dict()
        result[doc.id] = _doc

    avatar_id = list(result.keys())[0]
    avatar = Avatar(config=result[avatar_id], avatar_id=avatar_id)
    return avatar


def format_dictionary(event):
    """
    Format the firebase event triggered payload into a more usable dictionary.
    Args:
        firebase_payload (dict): firebase event triggered payload to format
    Returns:
        details (dict): formatted dictionary
    """
    details = {}

    details["budget_category"] = event["budget_category"]["stringValue"]

    details["accountNumber"] = event["accountNumber"]["stringValue"]
    details["centsAmount"] = event["centsAmount"]["integerValue"]
    details["currencyCode"] = event["currencyCode"]["stringValue"]
    try:
        details["dateTime"] = event["dateTime"]["timestampValue"]
    except KeyError:
        try:
            details["dateTime"] = event["dateTime"]["stringValue"]
        except:
            details["dateTime"] = datetime.now()

    details["reference"] = event["reference"]["stringValue"]
    details["type"] = event["type"]["stringValue"]

    card_details = event["card"]["mapValue"]["fields"]
    details["card"] =  {}
    details["card"]["id"] = card_details["id"]["stringValue"]

    merchant_details = event["merchant"]["mapValue"]["fields"]["category"]["mapValue"]["fields"]
    details["merchant"] = {}
    details["merchant"]["category"] = {}
    details["merchant"]["category"]["code"] = merchant_details["code"]["stringValue"]
    details["merchant"]["category"]["key"] = merchant_details["key"]["stringValue"]
    details["merchant"]["category"]["name"] = merchant_details["name"]["stringValue"]

    details["merchant"]["city"] = event["merchant"]["mapValue"]["fields"]["city"]["stringValue"]

    country_details = event["merchant"]["mapValue"]["fields"]["country"]["mapValue"]["fields"]
    details["merchant"]["country"] = {}
    details["merchant"]["country"]["alpha3"] = country_details["alpha3"]["stringValue"]
    details["merchant"]["country"]["code"] = country_details["code"]["stringValue"]
    details["merchant"]["country"]["name"] = country_details["name"]["stringValue"]

    details["merchant"]["name"] = event["merchant"]["mapValue"]["fields"]["name"]["stringValue"]

    return details


def get_goals(active=True):
    """
    Get goals from database.
    Args: 
        active (boolean): Specifies whether only active goals must be returned or all goals.
    """
    db = firestore.Client()
    goals_ref = db.collection(u'goals')
    docs = goals_ref.stream()
    
    result = {}
    for doc in docs:
        _doc = doc.to_dict()
        if active:
            if _doc["active"]:
                result[doc.id] = _doc
        else:
            result[doc.id] = _doc
    return result


def update_firebase_entry(collection, docId, data):
    """
    Update document in database
    """
    db = firestore.Client()
    db.collection(collection).document(docId).update(data)


def update_avatar(avatar): 
    """
    Update avatar document in database
    """  
    updated_info = {
        "current_hp": avatar.current_hp,
        "current_xp": avatar.current_xp,
        "level": avatar.level
    }
    update_firebase_entry(u'avatar', avatar._id, updated_info)

