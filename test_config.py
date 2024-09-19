# test_config.py

import json
import os
import sys

def load_json(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: {file_path} is not a valid JSON file.")
        print(f"JSON decoding error: {str(e)}")
        return None
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return None

def validate_config(config):
    errors = []

    # Check for required keys
    required_keys = ['input_dir', 'output_dir', 'employers', 'default_employer', 'employer_rules', 'date_range']
    for key in required_keys:
        if key not in config:
            errors.append(f"Missing required key: {key}")

    # Check data types
    if not isinstance(config.get('input_dir', ''), str):
        errors.append("'input_dir' must be a string")
    if not isinstance(config.get('output_dir', ''), str):
        errors.append("'output_dir' must be a string")
    if not isinstance(config.get('employers', []), list):
        errors.append("'employers' must be a list")
    if not isinstance(config.get('default_employer', ''), str):
        errors.append("'default_employer' must be a string")
    if not isinstance(config.get('employer_rules', []), list):
        errors.append("'employer_rules' must be a list")

    # Check employer_rules structure
    for rule in config.get('employer_rules', []):
        if not isinstance(rule, dict):
            errors.append("Each rule in 'employer_rules' must be a dictionary")
        elif not all(key in rule for key in ['description_contains', 'employer', 'category', 'note']):
            errors.append("Each rule must contain 'description_contains', 'employer', 'category', and 'note'")

    # Check date_range
    date_range = config.get('date_range', {})
    if not isinstance(date_range, dict):
        errors.append("'date_range' must be a dictionary")
    elif 'start_date' not in date_range or 'end_date' not in date_range:
        errors.append("'date_range' must contain 'start_date' and 'end_date'")

    return errors

def validate_categories(categories):
    errors = []

    if not isinstance(categories, dict):
        errors.append("Categories must be a dictionary")
        return errors

    if 'specific_transactions' not in categories:
        errors.append("Missing 'specific_transactions' key in categories")
    elif not isinstance(categories['specific_transactions'], dict):
        errors.append("'specific_transactions' must be a dictionary")
    else:
        for key, value in categories['specific_transactions'].items():
            if not isinstance(value, list) or len(value) != 3:
                errors.append(f"Invalid value for transaction '{key}': must be a list with 3 elements")

    return errors

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(base_dir, 'config.json')
    categories_file = os.path.join(base_dir, 'categories.json')

    print("Validating configuration files...")

    # Validate config.json
    config = load_json(config_file)
    if config:
        config_errors = validate_config(config)
        if config_errors:
            print("Errors in config.json:")
            for error in config_errors:
                print(f"- {error}")
        else:
            print("config.json is valid.")
    else:
        print("Failed to load config.json")

    print()

    # Validate categories.json
    categories = load_json(categories_file)
    if categories:
        categories_errors = validate_categories(categories)
        if categories_errors:
            print("Errors in categories.json:")
            for error in categories_errors:
                print(f"- {error}")
        else:
            print("categories.json is valid.")
    else:
        print("Failed to load categories.json")

    if (config and config_errors) or (categories and categories_errors):
        sys.exit(1)
    else:
        print("\nAll configuration files are valid.")
        sys.exit(0)

if __name__ == "__main__":
    main()