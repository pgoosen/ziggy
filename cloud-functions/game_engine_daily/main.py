import json
import time
import base64
import os

import requests
import datetime

from google.cloud import firestore
from google.cloud import pubsub_v1

from flask import jsonify
from datetime import datetime

from game_engine.transaction import Transaction
from game_engine.avatar import Avatar
from game_engine.goal import Goal
from game_engine import lookups


def ProcessDailyTasks(event, context):
    """
    Process daily tasks triggered by Cloud SCheduler event on PubSub
    """
    decoded = base64.b64decode(event["data"]).decode("utf-8")
    task = json.loads(decoded)

    if "avatar_daily_health" in task["task"]:
        update_avatar_health()
    if "process_daily_transactions" in task["task"]:
        process_daily_transactions()
    if "goal_daily_processing" in task["task"]:
        process_goals_daily()

    return "ok"


def update_avatar_health():
    """
    Increase avatar health daily
    """
    avatar = get_avatar()
    level = avatar.level
    try:
        hp_impact = avatar.increase_hp()
        level_diff = avatar.level-level 
        update_avatar(avatar)
        send_avatar_notification(avatar, hp_impact, 0, level_diff)
    except Exception as exc:
        print(exc)
    

def get_avatar():
    """
    Get the avatar from the database
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
    Update a document in firestore
    """
    db = firestore.Client()
    db.collection(collection).document(docId).update(data)


def update_avatar(avatar):   
    """
    Update the avatar document in the database
    """
    updated_info = {
        "current_hp": avatar.current_hp,
        "current_xp": avatar.current_xp,
        "level": avatar.level
    }
    update_firebase_entry(u'avatar', avatar._id, updated_info)


def process_goals_daily():
    """
    Process daily goals related tasks:
        Activate/Deactivate goals based on their start dates and end dates
        Determine if any goals have been achieved and process the impact thereof on the avatar
    """
    goals = get_goals(active=False)
    activate_goals(goals)

    goals = get_goals(active=False)
    avatar = get_avatar()
    process_goal_achievements(goals, avatar)


def get_goals(active=True):
    """
    Get all the goals from the database
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


def activate_goals(goals):
    """
    Activate goals based on their start date. Deactviate goals based on their end date.
    """
    for goal_id, goal_value in goals.items():
        goal = Goal(config=goal_value, doc_id=goal_id)
        if goal.start_date and goal.end_date and datetime.strptime(goal.start_date, "%Y-%m-%d") < datetime.now() and datetime.strptime(goal.end_date, "%Y-%m-%d") >= datetime.now():
            goal.active=True
            set_goal_active(goal_id=goal_id)
        elif not goal.end_date and goal.start_date and datetime.strptime(goal.start_date, "%Y-%m-%d") < datetime.now():
            goal.active=True
            set_goal_active(goal_id=goal_id)
        elif not goal.start_date and goal.end_date and datetime.strptime(goal.end_date, "%Y-%m-%d") >= datetime.now():
            goal.active=True
            set_goal_active(goal_id=goal_id)
        else:
            goal.active=False
            set_goal_active(goal_id=goal_id, active=False)


def set_goal_active(goal_id=None, active=True):
    """
    Save the updated goals state to the database
    """
    updated_info = {
        "active": active
    }
    if goal_id:
        db = firestore.Client()
        db.collection("goals").document(goal_id).update(updated_info)


def process_goal_achievements(goals, avatar):
    """
    Determine if any goals have been achieved or not and process teh impact thereof on the avatar.
    """
    hp_impact = 0
    xp_impact = 0
    avatar_start_level = avatar.level

    for goal_id, goal_value in goals.items():
        try:
            goal = Goal(config=goal_value, doc_id=goal_id)
            if not goal.active and not goal.complete and goal.end_date and datetime.strptime(goal.end_date, "%Y-%m-%d") < datetime.now():
                if goal.goal_type == lookups.GoalType.Spending.value:
                    if goal.goal_details["spending_type"] == lookups.SpendingType.TotalValue.value:
                        progress_value = int(goal.goal_details.get("progress_value", 0))
                        value_limit = int(goal.goal_details.get("value_limit", -1))
                        if value_limit == -1:
                            # do nothing
                            continue
                        elif progress_value > value_limit: 
                            hp_impact += avatar.decrease_hp(hp_decrease=2)
                            xp_impact += avatar.decrease_xp(xp_decrease=2)
                        else:
                            xp_impact += avatar.increase_xp(xp_increase=3)
                    elif goal.goal_details["spending_type"] == lookups.SpendingType.NumberTransactions.value: 
                        progress_count = int(goal.goal_details.get("progress_count", 0))
                        count_limit = int(goal.goal_details.get("count_limit", -1))
                        if count_limit == -1:
                            # do nothing
                            continue
                        elif progress_count > count_limit:
                            hp_impact += avatar.decrease_hp(hp_decrease=2)
                            xp_impact += avatar.decrease_xp(xp_decrease=2)
                        else:
                            xp_impact += avatar.increase_xp(xp_increase=3)

                elif goal.goal_type == lookups.GoalType.Savings.value:
                    progress_value = int(goal.goal_details.get("progress_value", 0))
                    value_limit = int(goal.goal_details.get("value_limit", -1))
                    if value_limit == -1:
                        # do nothing
                        continue
                    elif progress_value < value_limit:
                        hp_impact += avatar.decrease_hp(hp_decrease=2)
                        xp_impact += avatar.decrease_xp(xp_decrease=2)
                    else:
                        xp_impact += avatar.increase_xp(xp_increase=3)
                
                goal.complete = True
                        
                update_avatar(avatar)
                update_goal(goal, goal_id)
        except Exception as exc:
            print(exc)
        
    avatar_level_diff = avatar.level - avatar_start_level
    send_avatar_notification(avatar, hp_impact, xp_impact, avatar_level_diff)


def update_goal(goal, goal_id):
    """
    If a finished goal has been completed and processed, update the goals document in the database
    """
    updated_info = {
        "complete": goal.complete,
    }
    if goal_id:
        db = firestore.Client()
        db.collection("goals").document(goal_id).update(updated_info)


def send_avatar_notification(avatar, hp_impact=0, xp_impact=0, level_diff=0):
    """
    Send an avatar update slack notification
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


def process_daily_transactions():
    client_id = os.environ.get("CLIENT_ID", None)
    secret = os.environ.get("SECRET", None)

    client = OpenAPIClient(client_id=client_id, secret=secret)
    accounts = client.accounts()

    to_date = datetime.now()
    from_date = to_date - datetime.timedelta(days=1)

    for account in accounts["accounts"]:
        if account["productName"].lower() == "primesaver":
            transactions = client.transactions(account["accountId"], from_date=from_date, to_date=to_date)

            for transaction in transactions["transactions"]:
                transaction["centsAmount"] = transaction["amount"]*100
                # transaction["budget_category"] = lookups.BudgetCategory.Savings.value

                create_transaction(transaction)

def create_transaction(transaction):
    db = firestore.Client()
    db.collection("transactions").add(transaction)



class HTTPAuthenticateBearer(requests.auth.AuthBase):
    """Helper class to add Bearer Auth to requests"""
    def __init__(self, token: str):
        """
        Initialise with the token
        """
        self.token = token

    def __call__(self, r: requests.Request) -> requests.Request:
        """
        Sets the correct header for the request
        """
        r.headers["Authorization"] = "Bearer " + self.token
        return r


class OpenAPIClient():
    """
    >>> client = investec.Client("Your Client ID", "Your Secret")
    """

    def __init__(self, client_id: str=None, secret: str=None, timeout: int=30):
        """ Create a client instance with the provided options."""
        if not client_id or not secret:
            return

        self.client_id = client_id
        self.secret = secret
        self.timeout = timeout
        self.requests_session = requests.Session()
        self.api_host = "https://openapi.investec.com"
        self.token_expires = datetime.datetime.now()
        self.token = None
    
    def api_call(self, service_url: str, method: str="get", params: dict=None, body: str=None) -> dict:
        """ Helper function to create calls to the API."""

        if not self.token or datetime.datetime.now() >= self.token_expires:
            self.get_access_token() # Need to get a new token

        request = getattr(self.requests_session, method)
        headers = {"Accept": "application/json"}
        if method == "post":
            headers["Content-Type"] = "application/x-www-form-urlencoded; charset=utf-8"
        auth = HTTPAuthenticateBearer(self.token)

        response = request(f"{self.api_host}/{service_url}", params=params, data=body, headers=headers, auth=auth, timeout=self.timeout)
        try:
            response.raise_for_status()
            content = response.json()
            if "data" in content:
                return content["data"]
            return content
        except:
            raise requests.exceptions.HTTPError(response.status_code, response.content)

    def get_access_token(self) -> None:
        """ Get an access token."""

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "openapi.investec.com",
        }

        body = {
            "grant_type":"client_credentials",
            "scope":"accounts"
        }

        auth = requests.auth.HTTPBasicAuth(self.client_id, self.secret)
        
        url = f"{self.api_host}/identity/v2/oauth2/token"
        response = requests.post(url, data=body, headers=headers, auth=auth, timeout=self.timeout).json()

        self.token = response["access_token"]
        token_expiry = response["expires_in"] - 60 
        self.token_expires = datetime.datetime.now() + datetime.timedelta(seconds=token_expiry)

    def accounts(self) -> dict:
        """ Gets the available accounts."""
        url = f"/za/pb/v1/accounts"
        return self.api_call(url)

    def transactions(self, account_id: str, from_date: datetime=None, to_date: datetime=None) -> dict:
        """ Gets the transactions for an account."""
        if from_date and to_date and to_date < from_date:
            raise ValueError("The from_date must be before the to_date")

        params = {}
        if from_date:
            params["fromDate"] = from_date.strftime("%Y-%m-%d")
        if to_date:
            params["toDate"] = to_date.strftime("%Y-%m-%d")

        url = f"/za/pb/v1/accounts/{account_id}/transactions"
        return self.api_call(url, params=params)

    def balance(self, account_id: str) -> dict:
        """ Gets the balance for an account."""
        url = f"/za/pb/v1/accounts/{account_id}/balance"
        return self.api_call(url)
