from datetime import datetime
import json

from flask import make_response
import pytz
from slack_sdk import WebClient

from firestore_helper import (
    AddGoal, AvatarReport_PrepareData,
    DeleteGoals,
    GetGoals,
    GetTransactions,
    UpdateGoal,
    UpdateTransaction,
)

from game_engine.goal import Goal
from game_engine.lookups import BudgetCategory
from slack_composer import SlackComposer

class SlackApp:
    # Slack client for Web API requests
    client = WebClient()

    SLACK_BOT_TOKEN = None
    SLACK_VERIFICATION_TOKEN = None
    SLACK_SIGNING_SECRET = None
    SLACK_CHANNEL_ID = None
    BUCKET_PATH = None

    def __init__(
        self,
        SLACK_BOT_TOKEN,
        SLACK_VERIFICATION_TOKEN,
        SLACK_SIGNING_SECRET,
        SLACK_CHANNEL_ID,
        BUCKET_PATH
    ):
        self.SLACK_BOT_TOKEN = SLACK_BOT_TOKEN
        self.SLACK_VERIFICATION_TOKEN = SLACK_VERIFICATION_TOKEN
        self.SLACK_SIGNING_SECRET = SLACK_SIGNING_SECRET
        self.SLACK_CHANNEL_ID = SLACK_CHANNEL_ID
        self.BUCKET_PATH = BUCKET_PATH

        self.client = WebClient(self.SLACK_BOT_TOKEN)

    def list_goals(self):
        request_json_py = {"active": "true"}
        request_json_str = json.dumps(request_json_py)
        request_json = json.loads(request_json_str)
        goals_response = GetGoals(request_json)
        goals_json = goals_response.get_json()

        var_today = datetime.now(pytz.timezone("Africa/Johannesburg"))
        var_today_str = var_today.strftime("%Y-%m-%d")

        parent_message = self.client.chat_postMessage(
            channel=self.SLACK_CHANNEL_ID,
            blocks=[
                SlackComposer.MessageBlock_Divider(),
                SlackComposer.MessageBlock_TextHeader(":dart: You have {} goals ({})".format(len(goals_json),var_today_str))
            ]
        )

        parent_ts = parent_message["ts"]

        for index in goals_json:
            self.client.chat_postMessage(
                channel=self.SLACK_CHANNEL_ID,
                blocks=SlackComposer.Attachment_Goal(goals_json[index]),
                reply_broadcast="false",
                thread_ts=parent_ts
            )
        return make_response("", 200)

    def list_transactions(self):
        request_json_py = {"only_uncategorised": "True"}
        request_json_str = json.dumps(request_json_py)
        request_json = json.loads(request_json_str)
        transactions_response = GetTransactions(request_json)
        transactions_json = transactions_response.get_json()

        var_today = datetime.now(pytz.timezone("Africa/Johannesburg"))
        var_today_str = var_today.strftime("%Y-%m-%d")

        parent_message = self.client.chat_postMessage(
            channel=self.SLACK_CHANNEL_ID,
            blocks=[SlackComposer.MessageBlock_Divider(), SlackComposer.MessageBlock_TextHeader(":construction: You have {} uncategorised transactions ({})".format(len(transactions_json), var_today_str))]
        )

        parent_ts = parent_message["ts"]

        for index in transactions_json:
            self.client.chat_postMessage(
                channel=self.SLACK_CHANNEL_ID,
                attachments=SlackComposer.Attachment_Transaction(transactions_json[index]),
                reply_broadcast="false",
                thread_ts=parent_ts
            )

        return make_response("", 200)

    def post_transactions_to_channel(self, transaction_ids):
        request_json = json.loads(transaction_ids)

        transactions_response = GetTransactions(request_json)

        transactions_json = transactions_response.get_json()

        for index in transactions_json:
            self.client.chat_postMessage(
                channel=self.SLACK_CHANNEL_ID,
                attachments=SlackComposer.Attachment_Transaction(transactions_json[index]),
                reply_broadcast="false"
            )

        return make_response("", 200)

    def categorise_transaction(self, transaction_uuid, category_id, message_ts):
        # Get transaction
        request_json_py = {"doc_id": transaction_uuid}
        request_json_str = json.dumps(request_json_py)
        request_json = json.loads(request_json_str)
        response = GetTransactions(request_json)
        transaction_json = response.get_json()
        transaction_json["0"]["budget_category"] = category_id

        # Update transaction
        UpdateTransaction(transaction_json["0"], transaction_uuid)

        # Get transaction
        request_json_py = {"doc_id": transaction_uuid}
        request_json_str = json.dumps(request_json_py)
        request_json = json.loads(request_json_str)
        response = GetTransactions(request_json)
        transaction_json = response.get_json()

        # Update transaction on Slack
        self.client.chat_update(
            channel=self.SLACK_CHANNEL_ID,
            ts=message_ts,
            attachments=SlackComposer.Attachment_Transaction(
                transaction_json["0"]
            ),
        )
        return make_response("", 200)

    def delete_goal(self, goal_id, message_ts):
        request_json_py = {"doc_ids": [goal_id]}
        request_json_str = json.dumps(request_json_py)
        request_json = json.loads(request_json_str)
        DeleteGoals(request_json)

        self.client.chat_update(
            channel=self.SLACK_CHANNEL_ID,
            ts=message_ts,
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "*DELETED:* ~{}~".format(goal_id),
                    },
                }
            ],
        )
        return make_response("", 200)

    def refresh_goal_modal(self, current_goal_data, view_id, goal_id, message_ts, title, description):
        # request_json_py = {"active": "true", "doc_id": goal_id}
        # request_json_str = json.dumps(request_json_py)
        # request_json = json.loads(request_json_str)
        # goals_response = GetGoals(request_json)
        # goals_json = goals_response.get_json()

        goal = Goal()
        goal.setup_goal(current_goal_data)
        view = SlackComposer.Modal_Goal(title, description, goal, goal_id, message_ts)

        self.client.views_update(view=view, view_id=view_id)
        return make_response("", 200)

    def new_goal_modal(self, trigger_id):
        view = SlackComposer.Modal_Goal("New Goal", "The following form will help you to create a new goal.")

        self.client.views_open(trigger_id=trigger_id, view=view)
        return make_response("", 200)

    def new_goal(self, request_json_py):
        request_json_str = json.dumps(request_json_py)
        request_json = json.loads(request_json_str)
        AddGoal(request_json)

        return make_response("", 200)

    def update_goal_modal(self, goal_id, trigger_id, message_ts):
        request_json_py = {"active": "true", "doc_id": goal_id}
        request_json_str = json.dumps(request_json_py)
        request_json = json.loads(request_json_str)
        goals_response = GetGoals(request_json)
        goals_json = goals_response.get_json()

        goal = Goal()
        # goal_doc_id = goals_json["0"]["doc_id"]

        goal.setup_goal(goals_json["0"])

        view = SlackComposer.Modal_Goal("Update Goal", "The following form will help you to update a goal.", goal, goal_id, message_ts)

        self.client.views_open(trigger_id=trigger_id, view=view)

        return make_response("", 200)

    def update_goal(self, request_json_py, goal_uuid, message_ts):
        request_json_str = json.dumps(request_json_py)
        request_json = json.loads(request_json_str)
        UpdateGoal(request_json, goal_uuid)

        # Get goal
        request_json_py = {"doc_id": goal_uuid}
        request_json_str = json.dumps(request_json_py)
        request_json = json.loads(request_json_str)
        response = GetGoals(request_json)
        goal_json = response.get_json()

        # Update transaction on Slack
        self.client.chat_update(
            channel=self.SLACK_CHANNEL_ID,
            ts=message_ts,
            blocks=SlackComposer.Attachment_Goal(goal_json["0"]),
        )

        return make_response("", 200)

    def convert_view_to_data(self, payload):
        state_values = payload["view"]["state"]["values"]

        input_type = state_values[SlackComposer.inputId_type][SlackComposer.inputId_type]["selected_option"]["value"]
        input_spendingType = state_values[SlackComposer.inputId_spendingType][SlackComposer.inputId_spendingType]["selected_option"]["value"]
        input_start = state_values[SlackComposer.inputId_start][SlackComposer.inputId_start]["selected_date"]
        input_end = state_values[SlackComposer.inputId_end][SlackComposer.inputId_end]["selected_date"]

        input_count_limit = None
        input_value_limit = None

        if SlackComposer.inputId_count_limit in state_values:
            if state_values[SlackComposer.inputId_count_limit][SlackComposer.inputId_count_limit]["value"] is not None:
                input_count_limit = int(state_values[SlackComposer.inputId_count_limit][SlackComposer.inputId_count_limit]["value"])
        if SlackComposer.inputId_value_limit in state_values:
            if state_values[SlackComposer.inputId_value_limit][SlackComposer.inputId_value_limit]["value"] is not None:
                input_value_limit = int(state_values[SlackComposer.inputId_value_limit][SlackComposer.inputId_value_limit]["value"])

        input_category = BudgetCategory.Default.value
        input_merchant_based = False

        input_merchant_name = None
        input_merchant_code = None
        if (
            len(
                state_values[SlackComposer.inputId_merchant_based][SlackComposer.inputId_merchant_based]["selected_options"]
            ) > 0
        ):
            input_merchant_based = bool(state_values[SlackComposer.inputId_merchant_based][SlackComposer.inputId_merchant_based]["selected_options"][0]["value"])

        if (SlackComposer.inputId_merchant_name in state_values):
            input_merchant_name = state_values[SlackComposer.inputId_merchant_name][SlackComposer.inputId_merchant_name]["value"]

        if (SlackComposer.inputId_merchant_code in state_values):
            input_merchant_code = state_values[SlackComposer.inputId_merchant_code][SlackComposer.inputId_merchant_code]["value"]

        if (SlackComposer.inputId_category in state_values):
            input_category = state_values[SlackComposer.inputId_category][SlackComposer.inputId_category]["selected_option"]["value"]

        # if (SlackComposer.inputId_count_limit in state_values):
        #     input_count_limit = state_values[SlackComposer.inputId_count_limit][SlackComposer.inputId_count_limit]["value"]

        # if (SlackComposer.inputId_value_limit in state_values):
        #     input_value_limit = state_values[SlackComposer.inputId_value_limit][SlackComposer.inputId_value_limit]["value"]

        request_json_py = {
            "goal_type": "{}".format(input_type),
            "start_date": "{}".format(input_start),
            "end_date": "{}".format(input_end),
            "active": True,
            "goal_details": {
                "spending_type": "{}".format(input_spendingType),
                "merchant_based": input_merchant_based,
                # "merchant": {
                #     "merchant": "{}".format(input_merchant_name),
                #     "merchant_code": "{}".format(input_merchant_code),
                # },
                # "value_limit": "{}".format(input_value_limit),
                # "count_limit": "{}".format(input_count_limit),
                "budget_category": {"category": "{}".format(input_category)},
            },
        }

        if input_merchant_based is True:
            request_json_py["goal_details"]["merchant"] = {
                "merchant": "{}".format(input_merchant_name),
                "merchant_code": "{}".format(input_merchant_code),
            }

        if input_value_limit is not None:
            request_json_py["goal_details"]["value_limit"] = input_value_limit

        if input_count_limit is not None:
            request_json_py["goal_details"]["count_limit"] = input_count_limit

        return request_json_py

    def Avatar_SendToSlack(self, payload):
        # Switch to different slack messages
        if payload["type"] == "avatar_update":
            return self.AvatarUpdate_FormatMessage(payload["content"])
        elif payload["type"] == "avatar_report":
            # Load avatar date from DB
            data = AvatarReport_PrepareData()
            return self.AvatarUpdate_FormatMessage(data)
        else:
            print("failed - unknown payload type")
            return

    def AvatarUpdate_FormatMessage(self, data):
        # Only send avatar image if level changed or if report type
        imageUrl = None
        level = None
        if data["level_diff"] != 0 or "report" in data:
            if self.BUCKET_PATH is False:
                return
            level = str(data["level"])
            imageUrl = self.BUCKET_PATH.replace("{REPLACE_LEVEL}", level)
            # imageBlock = SlackComposer.MessageBlock_Image(imageUrl, level)

        # Load header and stats
        header = SlackComposer.AvatarUpdate_GetHeader(data)
        stats = SlackComposer.AvatarUpdate_GetStats(data)

        message_blocks = [
            SlackComposer.MessageBlock_Divider(),
            SlackComposer.MessageBlock_TextHeader(header),
            SlackComposer.MessageBlock_Text(stats)
        ]

        if imageUrl is not None:
            message_blocks.append(SlackComposer.MessageBlock_Image(imageUrl, level))

        parent_message = self.client.chat_postMessage(
            channel=self.SLACK_CHANNEL_ID,
            blocks=message_blocks
        )

        return make_response("", parent_message.status_code)
