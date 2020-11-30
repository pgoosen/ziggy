from game_engine.lookups import BudgetCategory, GoalType, SpendingType
from slack_composer import SlackComposer
from slack_app import SlackApp

import os
import base64
import json
from flask import make_response
from slack_sdk.signature import SignatureVerifier
# from slack_sdk.errors import SlackApiError

# Main
def ziggy(request):
    print(">>YOU REACHED ZIGGY")
    SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
    SLACK_VERIFICATION_TOKEN = os.environ["SLACK_VERIFICATION_TOKEN"]
    SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
    SLACK_CHANNEL_ID = os.environ["SLACK_CHANNEL_ID"]
    BUCKET_PATH = os.environ["BUCKET_PATH"]

    slackApp = SlackApp(
        SLACK_BOT_TOKEN,
        SLACK_VERIFICATION_TOKEN,
        SLACK_SIGNING_SECRET,
        SLACK_CHANNEL_ID,
        BUCKET_PATH
    )

    # print(">>>>>HEADERS")
    # print(request.headers)
    # print(">>>>>DATA")
    # print(request.get_data())
    # print(">>>>>JSON")
    # print(request.get_json())

    # Only POST requests are accepted
    if (request.method != "POST"):
        return "nope", 405

    if "User-Agent" not in request.headers:
        return "nope", 405

    if ("Slackbot" in request.headers["User-Agent"]):
        return process_request_from_slack(request, slackApp, SLACK_SIGNING_SECRET)

    if ("APIs-Google" in request.headers["User-Agent"] and "google.cloud.pubsub.topic.v1.messagePublished" in request.headers["Ce-Type"]):
        return process_pubsub(request, slackApp)

    return make_response("", 404)

def process_request_from_slack(request, slackApp, SLACK_SIGNING_SECRET):
    print(">>ZIGGY LISTENING TO SLACK")

    # Only respond to requests from Slack (removed after this was put begin the API Gateway)
    signature_verifier = SignatureVerifier(SLACK_SIGNING_SECRET)
    if (not signature_verifier.is_valid_request(request.get_data(), request.headers)):
        return make_response("invalid request", 403)

    payload = json.loads(request.form["payload"])

    # print(payload)

    trigger_id = None
    if ("trigger_id" in payload):
        trigger_id = payload["trigger_id"]

    payload_type = payload["type"]

    if payload_type == "shortcut":
        # List goals
        if (payload["callback_id"] == "list_goals"):
            return goals_list(slackApp)

        # List transactions
        if (payload["callback_id"] == "list_transactions"):
            return transactions_list(slackApp)

        # Create goal modal
        if (payload["callback_id"] == "create_goal"):
            return goal_add_modal(slackApp, trigger_id)

        # Show avatar
        if (payload["callback_id"] == "show_avatar"):
            message = {
                "type": "avatar_report",
                "content": ""
            }
            message_json_str = json.dumps(message)
            return avatar_report(slackApp, message_json_str)

    elif (payload_type == "block_actions"):
        action_id = payload["actions"][0]["action_id"]

        # Categorise transaction
        if (action_id == "categorise_transaction"):
            return transactions_categorise(slackApp, payload)

        # Delete goal
        if (action_id == "click_delete"):
            return goal_delete(slackApp, payload)

        # Update goal modal
        if (action_id == "click_update"):
            return goal_update_modal(slackApp, payload, trigger_id)

        # Goal modal refresh on block action
        block_id = payload["actions"][0]["block_id"]
        if (block_id == SlackComposer.inputId_merchant_based or block_id == SlackComposer.inputId_spendingType):
            return goal_modal_action(slackApp, payload)

    elif (payload_type == "view_submission"):
        # Create goal
        if (payload["view"]["title"]["text"] == "New Goal"):
            return goal_add(slackApp, payload)

        # Update goal
        if (payload["view"]["title"]["text"] == "Update Goal"):
            return goal_update(slackApp, payload)

    return make_response("", 404)

def process_pubsub(request, slackApp):
    print(">>ZIGGY LISTENING TO PUBSUB")

    request_json = request.get_json()
    pubsub_message = request_json['message']
    # print(request_json)
    # print(pubsub_message)
    # print(request.headers["Ce-Source"])
    if not isinstance(pubsub_message, dict):
        print("failed - payload incomplete")
        return

    payload = base64.b64decode(pubsub_message["data"]).decode('utf-8').strip()

    if payload is None or payload == "" or len(payload) < 2:
        print("failed - payload incomplete")
        return

    if "topics/new-transactions" in request.headers["Ce-Source"]:
        return transactions_list_on_event(slackApp, payload)

    if "topics/avatar-change" in request.headers["Ce-Source"]:
        return avatar_report(slackApp, payload)

    return make_response("", 404)

# Functions
def transactions_list(slackApp):
    print(">>LIST UNCATEGORISED TRANSACTIONS")

    return slackApp.list_transactions()

def transactions_list_on_event(slackApp, message):
    print(">>LIST NEW TRANSACTIONS")

    return slackApp.post_transactions_to_channel(message)

def transactions_categorise(slackApp, payload):
    print(">>CATEGORISE TRANSACTION")

    transaction_id = payload["actions"][0]["block_id"]
    category_id = payload["actions"][0]["selected_option"]["value"]
    message_ts = payload["container"]["message_ts"]

    return slackApp.categorise_transaction(transaction_id, category_id, message_ts)

def goals_list(slackApp):
    print(">>LIST GOALS")

    return slackApp.list_goals()

def goal_delete(slackApp, payload):
    print(">>DELETE GOAL")

    goal_id = payload["actions"][0]["value"]
    message_ts = payload["container"]["message_ts"]

    return slackApp.delete_goal(goal_id, message_ts)

def goal_add(slackApp, payload):
    print(">>ADD GOAL")

    validation_response = goal_inputs_validation_message(payload)
    if validation_response is not None:
        return validation_response

    request_json_py = slackApp.convert_view_to_data(payload)

    return slackApp.new_goal(request_json_py)

def goal_inputs_validation_message(payload):
    state_values = payload["view"]["state"]["values"]

    validation_fail_block_id = None
    validation_fail_message = "Invalid input"

    if (SlackComposer.inputId_type in state_values):
        if state_values[SlackComposer.inputId_type][SlackComposer.inputId_type]["selected_option"]["value"] == GoalType.NotSet.value:
            validation_fail_block_id = SlackComposer.inputId_type
            validation_fail_message = "Please choose an option"

    if (SlackComposer.inputId_spendingType in state_values) and (validation_fail_block_id is None):
        if state_values[SlackComposer.inputId_spendingType][SlackComposer.inputId_spendingType]["selected_option"]["value"] == SpendingType.NotSet.value:
            validation_fail_block_id = SlackComposer.inputId_spendingType
            validation_fail_message = "Please choose an option"

    if (SlackComposer.inputId_count_limit in state_values) and (validation_fail_block_id is None):
        try:
            input_count_limit = int(state_values[SlackComposer.inputId_count_limit][SlackComposer.inputId_count_limit]["value"])
        except ValueError:
            validation_fail_block_id = SlackComposer.inputId_count_limit
            validation_fail_message = "Please provide a valid limit"

    if (SlackComposer.inputId_value_limit in state_values) and (validation_fail_block_id is None):
        try:
            input_value_limit = int(state_values[SlackComposer.inputId_value_limit][SlackComposer.inputId_value_limit]["value"])
        except ValueError:
            validation_fail_block_id = SlackComposer.inputId_value_limit
            validation_fail_message = "Please provide a valid limit"

    if (SlackComposer.inputId_category in state_values) and (validation_fail_block_id is None):
        if state_values[SlackComposer.inputId_category][SlackComposer.inputId_category]["selected_option"]["value"] == BudgetCategory.Default.value:
            validation_fail_block_id = SlackComposer.inputId_category
            validation_fail_message = "Please choose an option"

    if validation_fail_block_id is not None:
        validation_message = {
            "response_action": "errors",
            "errors": {
                "{}".format(validation_fail_block_id): "{}".format(validation_fail_message)
            }
        }
        print(">> USER INPUT VALIDATION FAILED")
        return make_response(validation_message, 200)

    return None

def goal_update(slackApp, payload):
    print(">>UPDATE GOAL")

    validation_response = goal_inputs_validation_message(payload)
    if validation_response is not None:
        return validation_response

    goal_uuid = payload["view"]["private_metadata"]
    message_ts = payload["view"]["callback_id"]

    request_json_py = slackApp.convert_view_to_data(payload)

    return slackApp.update_goal(request_json_py, goal_uuid, message_ts)

def goal_add_modal(slackApp, trigger_id):
    print(">>SHOW NEW GOAL MODAL")

    return slackApp.new_goal_modal(trigger_id)

def goal_update_modal(slackApp, payload, trigger_id):
    print(">>SHOW UPDATE GOAL MODAL")

    goal_id = payload["actions"][0]["value"]
    message_ts = payload["container"]["message_ts"]

    return slackApp.update_goal_modal(goal_id, trigger_id, message_ts)

def goal_modal_action(slackApp, payload):
    print(">>REFRESH GOAL MODAL")

    view_id = payload["view"]["id"]

    title = payload["view"]["title"]["text"]
    description = payload["view"]["blocks"][0]["text"]["text"]

    goal_id = payload["view"]["private_metadata"]
    message_ts = payload["view"]["callback_id"]

    request_json_py = slackApp.convert_view_to_data(payload)

    return slackApp.refresh_goal_modal(request_json_py, view_id, goal_id, message_ts, title, description)

def avatar_report(slackApp, pubsub_message):
    print(">>AVATAR REPORT")

    payload = json.loads(pubsub_message)

    # Verify data/payload
    try:
        if "type" not in payload:
            print("failed - missing payload type")
            return

        if "content" not in payload:
            print("failed - missing payload content")
            return
    except Exception as e:
        print("failed - " + repr(e))
        return

    # Send slack messages
    return slackApp.Avatar_SendToSlack(payload)
