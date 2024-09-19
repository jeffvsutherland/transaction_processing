# update_json_processor.py

import logging

logger = logging.getLogger(__name__)

class UpdateJsonProcessor:
    def __init__(self, rule_manager, transaction_manager):
        self.rule_manager = rule_manager
        self.transaction_manager = transaction_manager

    def apply_rules_to_transactions(self):
        changes_made = 0
        for rule in self.rule_manager.rules:
            changes = self.transaction_manager.apply_bulk_rule(rule.to_dict())
            changes_made += changes
        logger.info(f"Applied rules to all transactions. {changes_made} changes made.")

    def process_kindle_transactions(self):
        kindle_transactions = self.transaction_manager.search_transactions('kindle')
        changes_made = 0
        for transaction in kindle_transactions:
            old_employer = transaction.data['employer']
            old_category = transaction.data['category']
            self.apply_rules_to_transactions()
            if transaction.data['employer'] != old_employer or transaction.data['category'] != old_category:
                changes_made += 1
        logger.info(f"Processed Kindle transactions. {changes_made} changes made.")

    def run_acceptance_test(self):
        kindle_transactions = self.transaction_manager.search_transactions('kindle')
        incorrect_kindle = [
            t for t in kindle_transactions
            if (t.data['Card'] == '3785' and (t.data['employer'] != 'Personal' or t.data['category'] != 'Arline')) or
               (t.data['Card'] != '3785' and (t.data['employer'] != 'Scrum Inc' or t.data['category'] != 'Employee Development'))
        ]
        return len(incorrect_kindle) == 0