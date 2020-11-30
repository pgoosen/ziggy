from datetime import datetime

import pytz
from game_engine.transaction import Transaction
from game_engine.goal import Goal
from game_engine.lookups import BudgetCategory, GoalType, SpendingType

class SlackComposer:
    inputId_type = "inputId_type"
    inputId_start = "inputId_start"
    inputId_end = "inputId_end"
    inputId_count_limit = "inputId_count_limit"
    inputId_value_limit = "inputId_value_limit"
    inputId_category = "inputId_category"
    inputId_spendingType = "inputId_spendingType"
    inputId_merchant_based = "inputId_merchant_based"
    inputId_merchant_name = "inputId_merchant_name"
    inputId_merchant_code = "inputId_merchant_code"

    @staticmethod
    def MessageSection_Field(field_name, value):
        field = {
            "type": "mrkdwn",
            "text": "*{}:* {}".format(field_name, value)
        }
        return field

    @staticmethod
    def MessageBlock_Divider():
        block = {
            "type": "divider"
        }
        return block

    def MessageBlock_Text(displayText):
        block = {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "{}".format(displayText)},
        }
        return block

    @staticmethod
    def MessageBlock_TextHeader(displayText):
        block = {
            "type": "header",
            "text": {"type": "plain_text", "text": "{}".format(displayText)},
        }
        return block

    @staticmethod
    def MessageBlock_Select(enum, action_id, block_id, placeholder, initial_id=None, initial_name=None):
        options = []
        for entry in enum:
            options.append(
                {
                    "text": {"type": "plain_text", "text": "{}".format(entry.name)},
                    "value": "{}".format(entry.value),
                }
            )

        block = {
            "type": "actions",
            "block_id": block_id,
            "elements": [
                {
                    "type": "static_select",
                    "placeholder": {"type": "plain_text", "text": placeholder},
                    "options": options,
                    "action_id": action_id
                }
            ],
        }

        if initial_id is not None and initial_name is not None:
            block["elements"][0]["initial_option"] = {
                "text": {"type": "plain_text", "text": "{}".format(initial_name)},
                "value": "{}".format(initial_id),
            }

        return block

    @staticmethod
    def MessageBlock_Image(imageUrl, level):
        block = {
            "type": "image",
            "image_url": "{}".format(imageUrl),
            "alt_text": "Avatar_Level_{}".format(level)
        }

        return block

    @staticmethod
    def Attachment_Transaction(transactions_json):
        print(transactions_json)

        if "budget_category" not in transactions_json:
            transactions_json["budget_category"] = None

        transaction_doc_id = transactions_json["doc_id"]
        transaction = Transaction(transactions_json, transaction_doc_id)
        # transaction_json_str = json.dumps(transactions_json)
        print(transactions_json)
        # transaction.process_transaction(transactions_json)
        # transaction._id = transaction_doc_id

        var__type = transaction._type
        var_currency_code = transaction.currency_code
        var_cents_amount = transaction.cents_amount
        var__datetime = transaction._datetime

        if transaction.category is None:
            if "budget_category" in transactions_json:
                transaction.category = transactions_json["budget_category"]

        var_budget_category_id = transaction.category

        # var_account_number = transaction.account_number
        # var_card = transaction.card
        # var_reference = transaction.reference
        # var_merchant = transaction.merchant
        # var_merchant_city = transaction.merchant["city"]
        var_merchant_name = transaction.merchant["name"]
        # var_merchant_category_code = transaction.merchant["category"]["code"]
        # var_merchant_category_key = transaction.merchant["category"]["key"]
        # var_merchant_category_name = transaction.merchant["category"]["name"]
        # var_merchant_country_name = transaction.merchant["country"]["name"]
        # var_merchant_country_code = transaction.merchant["country"]["code"]
        # var_merchant_country_alpha3 = transaction.merchant["country"]["alpha3"]

        initial_category_name = None
        color = "#FF0000"
        if var_budget_category_id is not None:
            initial_category_name = BudgetCategory(var_budget_category_id).name
            color = "#008000"

        options_category = SlackComposer.MessageBlock_Select(
            BudgetCategory,
            "categorise_transaction",
            transaction_doc_id,
            "Select a category",
            var_budget_category_id,
            initial_category_name,
        )

        attachments = [
            {
                "color": color,
                "blocks": [
                    SlackComposer.MessageBlock_TextHeader(
                        "Transaction ({})".format(var__type)
                    ),
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": "*Date:* {}".format(var__datetime),
                            },
                            {
                                "type": "mrkdwn",
                                "text": "*Merchant:* {}".format(var_merchant_name),
                            },
                            {
                                "type": "mrkdwn",
                                "text": "*Amount:* {} {}".format(var_cents_amount / 100, var_currency_code),
                            }
                        ],
                    },
                    options_category,
                ],
            }
        ]
        return attachments

    @staticmethod
    def Attachment_Goal(goals_json):
        goal = Goal()
        goal_doc_id = goals_json["doc_id"]
        goal.setup_goal(goals_json)
        var_type_id = goal.goal_type
        var_type = GoalType(var_type_id).name
        # var_var_active = goal.active
        var_startdate = goal.start_date
        var_enddate = goal.end_date

        var_detail_count_limit = None
        if "count_limit" in goal.goal_details:
            var_detail_count_limit = goal.goal_details["count_limit"]

        var_detail_value_limit = None
        if "value_limit" in goal.goal_details:
            var_detail_value_limit = goal.goal_details["value_limit"]

        var_detail_merchant_based = goal.goal_details["merchant_based"] in ["True", "true", True]
        var_detail_merchant_merchant = None
        var_detail_merchant_merchant_code = None
        if var_detail_merchant_based:
            var_detail_merchant_merchant = goal.goal_details["merchant"]["merchant"]
            var_detail_merchant_merchant_code = goal.goal_details["merchant"]["merchant_code"]

        # var_detail_count_progress_count = goal.goal_details["progress_count"]
        # var_detail_progress_value = goal.goal_details["progress_value"]
        var_spending_type_id = goal.goal_details["spending_type"]
        var_spending_type = SpendingType(var_spending_type_id).name
        var_budget_category_id = BudgetCategory.Default.value
        var_budget_category = BudgetCategory.Default.name

        merchant_text = var_detail_merchant_based
        if var_detail_merchant_based is True:
            merchant_text = "{} ({}-{})".format(merchant_text, var_detail_merchant_merchant, var_detail_merchant_merchant_code)
        else:
            var_budget_category_id = goal.goal_details["budget_category"]["category"]
            var_budget_category = BudgetCategory(var_budget_category_id).name

        blocks = [
            SlackComposer.MessageBlock_TextHeader(":dart: Goal"),
            {
                "type": "section",
                "fields": [
                    SlackComposer.MessageSection_Field("Active", "{} - {}".format(var_startdate, var_enddate)),
                    SlackComposer.MessageSection_Field("Type", var_type),
                    SlackComposer.MessageSection_Field("Spending type", var_spending_type),
                    # SlackComposer.MessageSection_Field("Category", var_budget_category),
                    # SlackComposer.MessageSection_Field("Merchant based", "{}".format(merchant_text)),
                    # SlackComposer.MessageSection_Field("Count limit", var_detail_count_limit),
                    # SlackComposer.MessageSection_Field("Value limit", var_detail_value_limit)
                ],
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Update"},
                        "style": "primary",
                        "value": "{}".format(goal_doc_id),
                        "action_id": "click_update"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Delete"},
                        "style": "danger",
                        "value": "{}".format(goal_doc_id),
                        "action_id": "click_delete"
                    },
                ],
            },
        ]

        if var_detail_merchant_based is not True:
            blocks[1]["fields"].append(SlackComposer.MessageSection_Field("Category", var_budget_category))
        else:
            blocks[1]["fields"].append(SlackComposer.MessageSection_Field("Merchant: ", "{} - ({})".format(var_detail_merchant_merchant, var_detail_merchant_merchant_code)))

        if (var_spending_type == SpendingType.NumberTransactions.name):
            blocks[1]["fields"].append(SlackComposer.MessageSection_Field("Count limit", var_detail_count_limit))

        if var_spending_type == SpendingType.TotalValue.name:
            blocks[1]["fields"].append(SlackComposer.MessageSection_Field("Value limit", var_detail_value_limit))

        return blocks

    @staticmethod
    def Modal_Goal(title, description, goal=None, goal_id=None, message_ts=None):
        var_today = datetime.now(pytz.timezone("Africa/Johannesburg"))
        var_startdate = var_today.strftime("%Y-%m-%d")
        var_enddate = var_startdate

        var_type = GoalType.NotSet.name
        var_type_id = GoalType.NotSet.value

        var_spending_type_id = SpendingType.TotalValue.value
        var_spending_type = SpendingType.TotalValue.name

        var_budget_category = BudgetCategory.Default.name
        var_budget_category_id = BudgetCategory.Default.value

        var_detail_merchant_based = False
        var_detail_merchant_merchant = None
        var_detail_merchant_merchant_code = None

        var_detail_count_limit = None
        var_detail_value_limit = None

        if goal_id is None:
            goal_id = "-"

        if message_ts is None:
            message_ts = "-"

        if goal is not None:
            var_type_id = goal.goal_type
            var_type = GoalType(var_type_id).name
            # var_var_active = goal.active
            var_startdate = goal.start_date
            if var_startdate == "":
                var_startdate = "2000-01-01"
            var_enddate = goal.end_date
            if var_enddate == "":
                var_enddate = "2030-01-01"

            if "count_limit" in goal.goal_details:
                var_detail_count_limit = goal.goal_details["count_limit"]
            if "value_limit" in goal.goal_details:
                var_detail_value_limit = goal.goal_details["value_limit"]

            var_spending_type_id = goal.goal_details["spending_type"]
            var_spending_type = SpendingType(var_spending_type_id).name

            var_detail_merchant_based = goal.goal_details["merchant_based"] in ["True", "true", True]

            if var_detail_merchant_based is True:
                var_detail_merchant_merchant = ""
                var_detail_merchant_merchant_code = ""
                if "merchant" in goal.goal_details["merchant"]:
                    if goal.goal_details["merchant"]["merchant"] != "None":
                        var_detail_merchant_merchant = goal.goal_details["merchant"]["merchant"]
                if "merchant_code" in goal.goal_details["merchant"]:
                    if goal.goal_details["merchant"]["merchant_code"] != "None":
                        var_detail_merchant_merchant_code = goal.goal_details["merchant"]["merchant_code"]
            else:
                var_budget_category_id = goal.goal_details["budget_category"]["category"]
                var_budget_category = BudgetCategory(var_budget_category_id).name

        view = {
            "type": "modal",
            "title": {"type": "plain_text", "text": "{}".format(title)},
            "submit": {"type": "plain_text", "text": "Submit"},
            "close": {"type": "plain_text", "text": "Cancel"},
            "private_metadata": goal_id,
            "callback_id": message_ts,
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": "{}".format(description),
                    },
                },
                {"type": "divider"},
            ],
        }

        # Type
        view["blocks"].append(SlackComposer.ModalInput_Select(SlackComposer.inputId_type, "Goal type", GoalType, var_type, var_type_id))

        # Start date
        view["blocks"].append(SlackComposer.ModalInput_Date(SlackComposer.inputId_start, "Start date", "Select a date", var_startdate))

        # End date
        view["blocks"].append(SlackComposer.ModalInput_Date(SlackComposer.inputId_end, "End date", "Select a date", var_enddate))

        # Spending Type
        view["blocks"].append(SlackComposer.ModalInput_Select_Action(SlackComposer.inputId_spendingType, "Spending type", SpendingType, var_spending_type, var_spending_type_id, SpendingType.NotSet.name))

        if var_spending_type_id == SpendingType.NumberTransactions.value:
            # Count_limit
            view["blocks"].append(SlackComposer.ModalInput_Text(SlackComposer.inputId_count_limit, "Count Limit", var_detail_count_limit))
        else:
            # Value_limit
            view["blocks"].append(SlackComposer.ModalInput_Text(SlackComposer.inputId_value_limit, "Value Limit", var_detail_value_limit))

        # Category
        if var_detail_merchant_based is False:
            view["blocks"].append(SlackComposer.ModalInput_Select(SlackComposer.inputId_category, "Budget category", BudgetCategory, var_budget_category, var_budget_category_id))

        # Merchant based
        view["blocks"].append(SlackComposer.ModalInput_Checkbox(SlackComposer.inputId_merchant_based, "Merchant based", var_detail_merchant_based))
        if var_detail_merchant_based is True:
            view["blocks"].append(SlackComposer.ModalInput_Text(SlackComposer.inputId_merchant_name, "Merchant name", var_detail_merchant_merchant))
            view["blocks"].append(SlackComposer.ModalInput_Text(SlackComposer.inputId_merchant_code, "Merchant code", var_detail_merchant_merchant_code))

        return view

    @staticmethod
    def ModalInput_Text(id, field_name, initial_value):
        block = {
            "type": "input",
            "block_id": "{}".format(id),
            "element": {
                "type": "plain_text_input",
                "action_id": "{}".format(id),
                # "initial_value": "{}".format(initial_value)
            },
            "label": {"type": "plain_text", "text": "{}".format(field_name)},
        }

        if initial_value is not None:
            block["element"]["initial_value"] = "{}".format(initial_value)

        return block

    @staticmethod
    def ModalInput_Date(id, field_name, placeholder, initial_value):
        block = {
            "type": "input",
            "block_id": "{}".format(id),
            "element": {
                "type": "datepicker",
                "initial_date": "{}".format(initial_value),
                "placeholder": {"type": "plain_text", "text": "{}".format(placeholder)},
                "action_id": "{}".format(id),
            },
            "label": {"type": "plain_text", "text": "{}".format(field_name)},
        }
        return block

    @staticmethod
    def ModalInput_Select(id, field_name, list, initial_name, initial_value):
        options_types = []
        for item in list:
            options_types.append(
                {
                    "text": {"type": "plain_text", "text": "{}".format(item.name)},
                    "value": "{}".format(item.value),
                }
            )

        block = {
            "type": "input",
            "block_id": "{}".format(id),
            "element": {
                "type": "static_select",
                "placeholder": {"type": "plain_text", "text": "Select an item"},
                "initial_option": {
                    "text": {
                        "type": "plain_text",
                        "text": "{}".format(initial_name),
                    },
                    "value": "{}".format(initial_value),
                },
                "options": options_types,
                "action_id": "{}".format(id),
            },
            "label": {"type": "plain_text", "text": "{}".format(field_name)},
        }

        return block

    @staticmethod
    def ModalInput_Select_Action(id, field_name, list, initial_name, initial_value, exclude_option=None):
        options_types = []
        for item in list:
            if exclude_option is not None and exclude_option == item.name:
                continue

            options_types.append(
                {
                    "text": {"type": "plain_text", "text": "{}".format(item.name)},
                    "value": "{}".format(item.value),
                }
            )

        block = {
            "type": "section",
            "block_id": "{}".format(id),
            "text": {
                "type": "mrkdwn",
                "text": "{}".format(field_name)
            },
            "accessory": {
                "type": "static_select",
                "placeholder": {"type": "plain_text", "text": "Select an item"},
                "initial_option": {
                    "text": {
                        "type": "plain_text",
                        "text": "{}".format(initial_name),
                    },
                    "value": "{}".format(initial_value),
                },
                "options": options_types,
                "action_id": "{}".format(id),
            },
        }

        return block

    @staticmethod
    def ModalInput_Checkbox(id, field_name, initial_value):
        block = {
            "type": "actions",
            "block_id": "{}".format(id),
            "elements": [{
                "type": "checkboxes",
                "action_id": "{}".format(id),
                # "initial_options": [
                #   {
                #     "value": "false",
                #     "text": {
                #       "type": "plain_text",
                #       "text": "Merchant based"
                #     }
                #   }
                # ],
                "options": [
                    {
                        "value": "True",
                        "text": {"type": "plain_text", "text": field_name},
                    }
                ],
            }],
        }

        if initial_value is True:
            block["elements"][0]["initial_options"] = [
                {
                    "value": "True",
                    "text": {"type": "plain_text", "text": field_name},
                }
            ]

        return block

    @staticmethod
    def AvatarUpdate_GetHeader(data):
        emojis = {
            "report": ":scroll::mag:",
            "level-5": ":unicorn_face::unicorn_face::unicorn_face:",
            "level-up": ":tada::tada::tada:",
            "level-down": ":skull_and_crossbones::skull_and_crossbones::skull_and_crossbones:",
            "xp-hp-up": ":rocket::rocket::rocket:",
            "xp-hp-down": ":warning::warning::warning:",
            "down": ":face_with_head_bandage::face_with_head_bandage::face_with_head_bandage:",
            "up": ":muscle::muscle::muscle:",
            "default": "Avatar :eyes:"
        }

        update_header = ":zebra_face: Avatar Update "
        report_header = ":zebra_face: Avatar Report "

        if "report" in data:
            return report_header + emojis["report"]

        if data["level_diff"] > 0 and data["level"] == 5:
            return update_header + emojis["level-5"]

        if data["level_diff"] > 0:
            return update_header + emojis["level-up"]

        if data["level_diff"] < 0:
            return update_header + emojis["level-down"]

        if data["xp_diff"] > 0 and data["hp_diff"] > 0:  # both up
            return update_header + emojis["xp-hp-up"]

        if data["xp_diff"] < 0 and data["hp_diff"] < 0:  # both down
            return update_header + emojis["xp-hp-down"]

        if data["xp_diff"] < 0 or data["hp_diff"] < 0:  # either down
            return update_header + emojis["down"]

        if data["xp_diff"] > 0 or data["hp_diff"] > 0:  # either up
            return update_header + emojis["up"]

        return emojis["default"]

    def AvatarUpdate_GetStatString(value, diff):
        emojis = {
            "up": ":arrow_up:",
            "down": ":small_red_triangle_down:"
        }

        change = ""
        template = "`[{diff}]` {emoji}"
        if diff > 0:
            change = template.format(emoji=emojis["up"], diff=("+" + str(diff)))
        elif diff < 0:
            change = template.format(emoji=emojis["down"], diff=str(diff))

        return "{val} {change}\n".format(val=str(value), change=change)

    @staticmethod
    def AvatarUpdate_GetStats(data):

        stats = ""

        stats = stats + "*Level* - " + \
            SlackComposer.AvatarUpdate_GetStatString(data["level"], data["level_diff"])
        stats = stats + "*HP* - " + \
            SlackComposer.AvatarUpdate_GetStatString(data["current_hp"], data["hp_diff"])
        stats = stats + "*XP* - " + \
            SlackComposer.AvatarUpdate_GetStatString(data["current_xp"], data["xp_diff"])

        return stats
