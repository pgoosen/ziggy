from flask import Response
from google.cloud import firestore
from google.cloud import pubsub_v1

import uuid
import json
import os

from game_engine.avatar import Avatar


def ProcessAddGoal(event, context):
    """
    Process new goals - add xp points to avatar
    """
    avatar = get_avatar()
    level = avatar.level
    xp_impact = avatar.increase_xp(xp_increase=3)
    level_diff = avatar.level - level
    update_avatar(avatar)
    send_avatar_notification(avatar, 0, xp_impact, level_diff)


def get_avatar():
    """
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


def send_avatar_notification(avatar, hp_impact=0, xp_impact=0, level_diff=0):
    """
    Send avatar update slack notification
    """
    if hp_impact == 0 and xp_impact == 0 and level_diff == 0:
        return

    project_id = os.environ.get("PROJECT_ID", None)
    topic_id = os.environ.get("TOPIC_ID", None)

    if not project_id or not topic_id:
        print("Unable to post to PubSub. No project_id/topic_id set.")
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