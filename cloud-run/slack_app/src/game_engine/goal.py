import typing
from google.cloud import firestore

from game_engine import lookups

class Goal:
    avatar = None
    goal_type = lookups.GoalType.NotSet
    start_date = None
    end_date = None
    active = False
    goal_details = None
    doc_id = None
    transaction_history = {}
    avatar = None

    def __init__(self, config=None, doc_id=None):
        if config:
            self.setup_goal(config)
        self.doc_id = doc_id

    def set_avatar(self, avatar):
        self.avatar = avatar

    def setup_goal(self, config=None):
        self.start_date = config.get("start_date", None)
        self.end_date = config.get("end_date", None)
        self.goal_type = config.get("goal_type", lookups.GoalType.NotSet)
        self.goal_details = config.get("goal_details", None)
        self.active = config.get("active", False)
        self.transaction_history = config.get("transaction_history", {})
        self.complete = config.get("complete", False)

        if self.start_date == "":
            self.start_date = None
        if self.end_date == "":
            self.end_date = None

    
    def match_transaction_to_goal(self, transaction=None):
        if self.complete:
            return

        if not transaction:
            print("tx empty")

        if self.goal_type == lookups.GoalType.NotSet.value:
            print("goal type not set")

        hp_impact = 0
        xp_impact = 0

        if transaction._id in list(self.transaction_history.keys()):
            hp_impact, xp_impact = self.reverse_transaction(transaction)
            self.update_goal()

        if self.goal_type == lookups.GoalType.Savings.value:
            hp_impact, xp_impact = self.process_saving_goal(transaction)
            self.update_goal()
        
        if self.goal_type == lookups.GoalType.Spending.value and not transaction._id in list(self.transaction_history.keys()):
            hp_impact, xp_impact = self.process_spending_goal(transaction)
            self.update_goal()
            
        return hp_impact, xp_impact

    def process_saving_goal(self, transaction):
        return 0, 0
             
    def process_spending_goal(self, transaction):
        spending_type = self.goal_details.get("spending_type", lookups.SpendingType.NotSet)
        merchant_based = self.goal_details.get("merchant_based", False)
        merchant = self.goal_details.get("merchant", {})
        progress_total = int(self.goal_details.get("progress_value", -1))
        progress_count = int(self.goal_details.get("progress_count", -1))
        impact_hp = 0
        impact_xp = 0

        if merchant_based: #Merchant based
            if merchant != {}:
                if transaction.merchant["category"]["code"] == merchant["merchant_code"]: 
                    impact_hp, impact_xp = self.process_avatar_impact(spending_type, progress_total, progress_count, transaction)
                    self.transaction_history[transaction._id] = {
                        "avatar_hp": impact_hp,
                        "avatar_xp": impact_xp,
                    }
                elif merchant.get("merchant", None) and  merchant["merchant"].lower() in transaction.merchant["category"]["name"].lower():
                    impact_hp, impact_xp = self.process_avatar_impact(spending_type, progress_total, progress_count, transaction)
                    self.transaction_history[transaction._id] = {
                        "avatar_hp": impact_hp,
                        "avatar_xp": impact_xp,
                    }
                    
        else: #Budget category based
            budget = self.goal_details.get("budget_category", None)
            if transaction.category == budget.get("category", None):
                impact_hp, impact_xp = self.process_avatar_impact(spending_type, progress_total, progress_count, transaction)
                self.transaction_history[transaction._id] = {
                    "avatar_hp": impact_hp,
                    "avatar_xp": impact_xp,
                }

        return impact_hp, impact_xp


    def process_avatar_impact(self, spending_type, progress_total, progress_count, transaction ):
        impact_hp = 0 
        if spending_type == lookups.SpendingType.TotalValue.value:
            progress_total += transaction.cents_amount
            goal_limit = int(self.goal_details.get("value_limit", -1))
            if goal_limit > -1 and progress_total > goal_limit:
                critical_hit = {
                    "spending_type": spending_type,
                    "value_limit": goal_limit,
                    "progress_value": progress_total,
                }
                impact_hp = self.avatar.decrease_hp(critical_hit=True, critical_details = critical_hit)
                impact_xp = self.avatar.decrease_xp(xp_decrease=1)
            else: 
                impact_xp = self.avatar.increase_xp(xp_increase=0.5)
                impact_hp = self.avatar.decrease_hp()
            self.goal_details["progress_value"] = progress_total
            
        elif spending_type == lookups.SpendingType.NumberTransactions.value:
            progress_count += 1
            goal_limit = int(self.goal_details.get("count_limit", -1))
            if goal_limit > -1 and progress_count > goal_limit :
                critical_hit = {
                    "spending_type": spending_type,
                    "count_limit": goal_limit,
                    "progress_count": progress_count,
                }
                impact_hp = self.avatar.decrease_hp(critical_hit=True, critical_details = critical_hit)
                impact_xp = self.avatar.decrease_xp(xp_decrease=1, critical_hit=True, critical_details=critical_hit)
            else: 
                impact_xp = self.avatar.increase_xp(xp_increase=0.5)
                impact_hp = self.avatar.decrease_hp()
            self.goal_details["progress_count"] = progress_count
        
        return impact_hp, impact_xp


    def update_goal(self):
        updated_info = {
            "goal_details": self.goal_details,
            "transaction_history" : self.transaction_history
        }

        if self.doc_id:
            db = firestore.Client()
            db.collection("goals").document(self.doc_id).update(updated_info)


    def _format_goal(self):
        _dict = self.__dict__
        _dict["goal_type"] = self.goal_type.value
        if "budget_category" in _dict["goal_details"]:
            _dict["goal_details"]["budget_category"]["category"] = self.goal_details["budget_category"]["category"].value
        if "spending_type" in _dict["goal_details"]:
            _dict["goal_details"]["spending_type"] = self.goal_details["spending_type"].value

        return _dict


    def reverse_transaction(self, transaction):
        hp_impact = self.transaction_history[transaction._id]["avatar_hp"]
        xp_impact = self.transaction_history[transaction._id]["avatar_xp"]

        if -1*hp_impact > 0:
            self.avatar.increase_hp(hp_increase=hp_impact)
        else:
            self.avatar.decrease_hp(hp_decrease=hp_impact)

        if -1*xp_impact > 0:
            self.avatar.increase_xp(xp_increase=xp_impact)
        else:
            self.avatar.decrease_xp(xp_decrease=xp_impact)

        self.transaction_history.pop(transaction._id)

        spending_type = self.goal_details.get("spending_type", lookups.SpendingType.NotSet)
        if spending_type == lookups.SpendingType.TotalValue.value:
            progress_total = int(self.goal_details.get("progress_value", -1))
            self.goal_details["progress_value"] = progress_total
        elif spending_type == lookups.SpendingType.NumberTransactions.value:
            progress_count = int(self.goal_details.get("progress_count", -1))
            self.goal_details["progress_count"] = progress_count

        return hp_impact, xp_impact