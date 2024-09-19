# categorize.py

from utils import load_json, save_json

def categorize_transaction(description, employer_rules, categories):
    description_lower = description.strip().lower()

    # First, check specific rules
    for keyword, rule_data in categories.items():
        if keyword.lower() in description_lower:
            return rule_data[0], rule_data[1], rule_data[2]

    # If no specific rule matches, check general rules
    for rule in employer_rules:
        if rule['description_contains'].lower() in description_lower:
            return rule['category'], rule['employer'], rule['note']

    return "Uncategorized", "Unknown", ""