import pandas as pd
import json
import os
from datetime import datetime, timedelta
from rules_processor import RulesProcessor


def setup_rules_processor():
    config = {
        "submitter_name": "Jeff Sutherland",
        "employee_rules": [
            {
                "name": "Jeff Sutherland",
                "travel_days": ["2022-12-06", "2022-12-07"],
                "travel_employer": "Frequency Research Foundation"
            }
        ],
        "categories_expensable_on_travel": ["Food", "Transport"],
        "employer_rules": [
            {
                "description_contains": "Starbucks",
                "employer": "Personal",
                "category": "Food"
            },
            {
                "description_contains": "UBER",
                "employer": "Personal",
                "category": "Transport"
            },
            {
                "description_contains": "Hotel",
                "employer": "Personal",
                "category": "Accommodation"
            }
        ],
        "default_employer": "Unknown"
    }

    categories = {}

    with open('temp_config.json', 'w') as f:
        json.dump(config, f)
    with open('temp_categories.json', 'w') as f:
        json.dump(categories, f)

    return RulesProcessor('temp_config.json', 'temp_categories.json')


def test_case_sensitivity():
    rules_processor = setup_rules_processor()
    df = pd.DataFrame([
        {
            "Date": datetime(2022, 12, 6),
            "Description": "STARBUCKS",
            "Amount": -5.75,
            "category": "Food",
            "employer": "Personal",
            "Bank": "TestBank",
            "Card": "1234"
        }
    ])
    result_df = rules_processor.apply_rules(df)

    assert result_df.iloc[0]['employer'] == "Frequency Research Foundation", \
        f"Expected case-insensitive match for 'STARBUCKS', but got {result_df.iloc[0]['employer']}"

    print("Test 1: Case sensitivity - Passed")


def test_partial_match():
    rules_processor = setup_rules_processor()
    df = pd.DataFrame([
        {
            "Date": datetime(2022, 12, 6),
            "Description": "Uber Eats",
            "Amount": -25.00,
            "category": "Transport",
            "employer": "Personal",
            "Bank": "TestBank",
            "Card": "1234"
        }
    ])
    result_df = rules_processor.apply_rules(df)

    assert result_df.iloc[0]['employer'] == "Frequency Research Foundation", \
        f"Expected partial match for 'Uber Eats', but got {result_df.iloc[0]['employer']}"

    print("Test 2: Partial match - Passed")


def test_travel_day_boundary():
    rules_processor = setup_rules_processor()
    df = pd.DataFrame([
        {
            "Date": datetime(2022, 12, 7, 23, 59, 59),
            "Description": "Starbucks",
            "Amount": -5.75,
            "category": "Food",
            "employer": "Personal",
            "Bank": "TestBank",
            "Card": "1234"
        },
        {
            "Date": datetime(2022, 12, 8, 0, 0, 0),
            "Description": "Starbucks",
            "Amount": -5.75,
            "category": "Food",
            "employer": "Personal",
            "Bank": "TestBank",
            "Card": "1234"
        }
    ])
    result_df = rules_processor.apply_rules(df)

    assert result_df.iloc[0]['employer'] == "Frequency Research Foundation", \
        f"Expected last second of travel day to be 'Frequency Research Foundation', but got {result_df.iloc[0]['employer']}"
    assert result_df.iloc[1]['employer'] == "Personal", \
        f"Expected first second after travel day to be 'Personal', but got {result_df.iloc[1]['employer']}"

    print("Test 3: Travel day boundary - Passed")


def test_unknown_category():
    rules_processor = setup_rules_processor()
    df = pd.DataFrame([
        {
            "Date": datetime(2022, 12, 6),
            "Description": "Starbucks",
            "Amount": -5.75,
            "category": "Unknown",
            "employer": "Personal",
            "Bank": "TestBank",
            "Card": "1234"
        }
    ])
    result_df = rules_processor.apply_rules(df)

    assert result_df.iloc[0]['employer'] == "Frequency Research Foundation", \
        f"Expected unknown category to still be processed, but got {result_df.iloc[0]['employer']}"

    print("Test 4: Unknown category - Passed")


def test_no_matching_rule():
    rules_processor = setup_rules_processor()
    df = pd.DataFrame([
        {
            "Date": datetime(2022, 12, 6),
            "Description": "Random Vendor",
            "Amount": -100.00,
            "category": "Miscellaneous",
            "employer": "Personal",
            "Bank": "TestBank",
            "Card": "1234"
        }
    ])
    result_df = rules_processor.apply_rules(df)

    assert result_df.iloc[0]['employer'] == "Personal", \
        f"Expected no matching rule to keep 'Personal', but got {result_df.iloc[0]['employer']}"

    print("Test 5: No matching rule - Passed")


if __name__ == "__main__":
    try:
        test_case_sensitivity()
        test_partial_match()
        test_travel_day_boundary()
        test_unknown_category()
        test_no_matching_rule()
        print("All advanced tests passed successfully!")
    finally:
        # Clean up temporary files
        os.remove('temp_config.json')
        os.remove('temp_categories.json')