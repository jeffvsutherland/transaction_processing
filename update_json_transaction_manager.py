# update_json_transaction_manager.py

import pandas as pd

class UpdateJsonTransaction:
    def __init__(self, data):
        self.data = data

    def update(self, new_data):
        self.data.update(new_data)

class UpdateJsonTransactionManager:
    def __init__(self, transactions_df, valid_employers):
        self.transactions = [UpdateJsonTransaction(row.to_dict()) for _, row in transactions_df.iterrows()]
        self.valid_employers = valid_employers

    def search_transactions(self, search_term):
        return [t for t in self.transactions if search_term.lower() in t.data['Description'].lower()]

    def update_transaction(self, transaction, new_data):
        if 'employer' in new_data and new_data['employer'] not in self.valid_employers:
            raise ValueError(f"Invalid employer: {new_data['employer']}")
        transaction.update(new_data)

    def apply_bulk_rule(self, rule):
        changes_made = 0
        for transaction in self.transactions:
            if rule['description_contains'].lower() in transaction.data['Description'].lower():
                if 'card' in rule and str(transaction.data.get('Card')) != str(rule['card']):
                    continue
                if (transaction.data.get('employer') != rule['employer'] or
                        transaction.data.get('category') != rule['category'] or
                        transaction.data.get('note') != rule.get('note', '')):
                    transaction.update({
                        'employer': rule['employer'],
                        'category': rule['category'],
                        'note': rule.get('note', '')
                    })
                    changes_made += 1
        return changes_made

    def review_vendor_transactions(self, vendor):
        return [t for t in self.transactions if vendor.lower() in t.data['Description'].lower()]

    def get_unknown_transactions(self):
        return [t for t in self.transactions if t.data.get('employer') == 'Unknown']

    def get_travel_day_transactions(self, travel_days):
        travel_days = [pd.to_datetime(day).date() for day in travel_days]
        return [t for t in self.transactions if pd.to_datetime(t.data['Date']).date() in travel_days]

    def to_dataframe(self):
        return pd.DataFrame([t.data for t in self.transactions])

if __name__ == "__main__":
    print("This script is not meant to be run directly. Please run update_json_core.py instead.")