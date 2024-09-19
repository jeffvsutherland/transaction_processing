# update_json_rule_manager.py

class UpdateJsonRule:
    def __init__(self, description_contains, employer, category, note="", card=None):
        self.description_contains = description_contains
        self.employer = employer
        self.category = category
        self.note = note
        self.card = card

    def to_dict(self):
        rule_dict = {
            "description_contains": self.description_contains,
            "employer": self.employer,
            "category": self.category,
        }
        if self.note:
            rule_dict["note"] = self.note
        if self.card:
            rule_dict["card"] = self.card
        return rule_dict

class UpdateJsonRuleManager:
    def __init__(self, rules):
        self.rules = [UpdateJsonRule(**rule) for rule in rules]

    def add_rule(self, rule):
        self.rules.append(UpdateJsonRule(**rule))

    def modify_rule(self, index, new_rule):
        if 0 <= index < len(self.rules):
            self.rules[index] = UpdateJsonRule(**new_rule)
        else:
            raise IndexError("Invalid rule index")

    def remove_rule(self, index):
        if 0 <= index < len(self.rules):
            del self.rules[index]
        else:
            raise IndexError("Invalid rule index")

    def display_rules(self):
        for i, rule in enumerate(self.rules):
            print(f"{i}: {rule.description_contains} -> {rule.employer}, {rule.category}")

    def to_list(self):
        return [rule.to_dict() for rule in self.rules]