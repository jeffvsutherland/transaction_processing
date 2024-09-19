import json
import pandas as pd
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class RulesProcessor:
    def __init__(self, config_file, categories_file):
        self.config_file = config_file
        self.categories_file = categories_file
        self.load_files()

    def load_files(self):
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)
        with open(self.categories_file, 'r') as f:
            self.categories = json.load(f)
        logger.info(f"Loaded {len(self.config.get('employer_rules', []))} rules from config file")

    def is_travel_day(self, employee_name, current_date):
        for employee in self.config.get('employee_rules', []):
            if employee['name'] == employee_name:
                travel_days = [datetime.strptime(day, '%Y-%m-%d').date() for day in employee['travel_days']]
                if isinstance(current_date, datetime):
                    current_date = current_date.date()
                elif isinstance(current_date, str):
                    current_date = datetime.strptime(current_date, '%Y-%m-%d').date()
                if current_date in travel_days:
                    return True, employee.get('travel_employer', 'Unknown')
        return False, None

    def is_expensable_on_travel(self, category, description):
        expensable_categories = [cat.lower() for cat in self.config.get('categories_expensable_on_travel', [])]
        is_restaurant = self.is_restaurant(description)
        is_amazon = 'amazon' in description.lower()

        return (category.lower() in expensable_categories or
                'food' in category.lower() or
                'meal' in category.lower() or
                is_restaurant) and not is_amazon

    def is_restaurant(self, description):
        restaurant_keywords = ['restaurant', 'cafe', 'diner', 'eatery', 'bistro', 'grill', 'pizzeria', 'steakhouse']
        return any(keyword in description.lower() for keyword in restaurant_keywords)

    def apply_rules(self, df):
        def categorize_expense(row):
            current_date = pd.to_datetime(row['Date']).date() if isinstance(row['Date'], str) else row['Date']

            is_travel, travel_employer = self.is_travel_day(self.config['submitter_name'], current_date)
            logger.debug(f"Processing transaction: {row['Description']} on {current_date}")
            logger.debug(f"Is travel day: {is_travel}, Travel employer: {travel_employer}")

            # First, check if it's a travel day and the category is expensable
            if is_travel and self.is_expensable_on_travel(row.get('category', ''), row['Description']):
                logger.debug(f"Categorized as travel expense: {row['Description']}")
                return {
                    'employer': travel_employer,
                    'category': 'Travel Meal' if self.is_restaurant(row['Description']) else row.get('category',
                                                                                                     'Travel'),
                    'note': f"Travel expense on {current_date.strftime('%Y-%m-%d')}"
                }
            elif is_travel and 'amazon' in row['Description'].lower():
                logger.debug(f"Amazon purchase on travel day, not expensed: {row['Description']}")
                return {
                    'employer': self.config.get('default_employer', 'Personal'),
                    'category': 'Personal Purchase on Travel Day',
                    'note': f"Amazon purchase on travel day {current_date.strftime('%Y-%m-%d')}, not expensed"
                }

            # Sort rules by specificity (more specific rules first)
            sorted_rules = sorted(self.config.get('employer_rules', []),
                                  key=lambda x: len(x['description_contains']),
                                  reverse=True)

            # Then, check for specific rules
            for rule in sorted_rules:
                if self.match_description(rule['description_contains'], row['Description']):
                    logger.debug(f"Matched rule: {rule['description_contains']} for {row['Description']}")
                    return {
                        'employer': rule['employer'],
                        'category': rule['category'],
                        'note': rule.get('note', '')
                    }

            # If no specific rule matches, use the default
            logger.debug(f"No rule matched, using default: {row['Description']}")
            return {
                'employer': self.config.get('default_employer', 'Unknown'),
                'category': row.get('category', 'Uncategorized'),
                'note': 'No matching rule found'
            }

        results = df.apply(categorize_expense, axis=1)

        df['employer'] = results.apply(lambda x: x.get('employer', df['employer']))
        df['category'] = results.apply(lambda x: x.get('category', df.get('category', 'Uncategorized')))
        df['note'] = results.apply(lambda x: self.process_note(x.get('note', df.get('note', ''))))

        return df

    def match_description(self, rule_description, transaction_description):
        return rule_description.lower() in transaction_description.lower()

    def process_note(self, note):
        if isinstance(note, pd.Series):
            return note.to_string()
        elif note is None:
            return ''
        else:
            return str(note)


if __name__ == "__main__":
    print(
        "This script is not meant to be run directly. Please import and use the RulesProcessor class in other scripts.")