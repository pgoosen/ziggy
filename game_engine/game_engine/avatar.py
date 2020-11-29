import typing
from game_engine import lookups

class Avatar:
    max_hp = 50
    _id =  None

    def __init__(self, config=None, avatar_id=None):
        self._id = avatar_id
        if not config:
            self.current_xp = 0
            self.current_hp = self.max_hp  
            self.level = 1
        else:
            self.current_xp = config.get("current_xp", 0)
            self.current_hp = config.get("current_hp", 0)
            self.level = config.get("level", 1)
        

    def get_xp_to_next_level(self):
        xp_to_level = 0
        if self.level < 5:
            return self.level*25
        else:
            xp_to_level = round(0.25*self.level*self.level+10*self.level+139.75)
            
        return xp_to_level

    def increase_hp(self, hp_increase = 1.5):
        if self.current_hp + hp_increase > self.max_hp:
            hp_increase = self.max_hp - self.current_hp
            self.current_hp = self.max_hp
        else:
            self.current_hp += hp_increase
        
        return hp_increase

    def decrease_hp(self, hp_decrease=1.5, critical_hit=False, critical_details=None):
        if critical_hit:
            if critical_details:
                spending_type = critical_details["spending_type"]
                
                if spending_type == lookups.SpendingType.TotalValue.value:
                    value_limit = critical_details["value_limit"]
                    progress_value = critical_details["progress_value"]
                    increase_factor = (progress_value - value_limit) / value_limit * 1.0
                    hp_decrease *= increase_factor
 
                if spending_type == lookups.SpendingType.NumberTransactions.value:
                    count_limit = critical_details["count_limit"]
                    progress_count = critical_details["progress_count"]
                    increase_factor = (progress_count - count_limit) / count_limit * 1.0
                    hp_decrease *= increase_factor


        if self.current_hp - hp_decrease > 0:
            self.current_hp -= hp_decrease
        else:
            hp_decrease = self.current_hp
            self.die()

        return -1*hp_decrease

    def increase_xp(self, xp_increase=1):
        needed_xp = self.get_xp_to_next_level()
        if needed_xp - (self.current_xp + xp_increase) > 0:
            self.current_xp += xp_increase
        else:
            self.current_xp = (self.current_xp + xp_increase) - needed_xp
            self.level += 1

        return xp_increase

    def decrease_xp(self, xp_decrease=1, critical_hit=False, critical_details=None):
        if critical_hit:
            if critical_details:
                spending_type = critical_details["spending_type"]
                
                if spending_type == lookups.SpendingType.TotalValue.value:
                    value_limit = critical_details["value_limit"]
                    progress_value = critical_details["progress_value"]
                    increase_factor = progress_value/value_limit*1.0
                    xp_decrease *= increase_factor

                elif spending_type == lookups.SpendingType.NumberTransactions.value:
                    count_limit = critical_details["count_limit"]
                    progress_count = critical_details["progress_count"]
                    increase_factor = progress_count/count_limit*1.0
                    xp_decrease *= increase_factor

                    
        if self.current_xp - xp_decrease >= 0:
            self.current_xp -= xp_decrease
        else:
            xp_decrease = self.current_xp
            self.current_xp = 0
            
        return -1*xp_decrease

    def die(self):
        if self.level > 1:
            self.level -= 1
        self.current_xp = 0
        self.current_hp = self.max_hp
