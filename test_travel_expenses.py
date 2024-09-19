import pandas as pd
import json
import os
from datetime import datetime
from rules_processor import RulesProcessor


def setup_rules_processor():
    config = {
        "submitter_name": "Jeff Sutherland",
        "employee_rules": [
            {
                "name": "Jeff Sutherland",
                "travel_days": ["2022-12-06"],
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
                "description_contains": "Uber",
                "employer": "Personal",
                "category": "Transport"
            },
            {
                "description_contains": "Amazon",
                "employer": "Personal",
                "category": "Shopping"
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


def test_starbucks_travel_day():
    rules_processor = setup_rules_processor()
    df = pd.DataFrame([
        {
            "Date": datetime(2022, 12, 6),
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
        f"Expected employer to be 'Frequency Research Foundation', but got {result_df.iloc[0]['employer']}"
    assert "Travel expense on 2022-12-06" in result_df.iloc[0]['note'], \
        f"Expected note to contain 'Travel expense on 2022-12-06', but got {result_df.iloc[0]['note']}"

    print("Test 1: Starbucks on travel day - Passed")


def test_starbucks_non_travel_day():
    rules_processor = setup_rules_processor()
    df = pd.DataFrame([
        {
            "Date": datetime(2022, 12, 7),
            "Description": "Starbucks",
            "Amount": -5.75,
            "category": "Food",
            "employer": "Personal",
            "Bank": "TestBank",
            "Card": "1234"
        }
    ])
    result_df = rules_processor.apply_rules(df)

    assert result_df.iloc[0]['employer'] == "Personal", \
        f"Expected employer to be 'Personal', but got {result_df.iloc[0]['employer']}"
    assert 'note' not in result_df.columns or pd.isna(result_df.iloc[0]['note']) or result_df.iloc[0]['note'] == '', \
        f"Expected no travel note or empty note, but got {result_df.iloc[0].get('note', 'No note')}"

    print("Test 2: Starbucks on non-travel day - Passed")


def test_multiple_transactions():
    rules_processor = setup_rules_processor()
    df = pd.DataFrame([
        {
            "Date": datetime(2022, 12, 6),
            "Description": "Starbucks",
            "Amount": -5.75,
            "category": "Food",
            "employer": "Personal",
            "Bank": "TestBank",
            "Card": "1234"
        },
        {
            "Date": datetime(2022, 12, 6),
            "Description": "Uber",
            "Amount": -25.00,
            "category": "Transport",
            "employer": "Personal",
            "Bank": "TestBank",
            "Card": "1234"
        },
        {
            "Date": datetime(2022, 12, 6),
            "Description": "Amazon",
            "Amount": -50.00,
            "category": "Shopping",
            "employer": "Personal",
            "Bank": "TestBank",
            "Card": "1234"
        },
        {
            "Date": datetime(2022, 12, 7),
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
        f"Expected Starbucks on travel day to be 'Frequency Research Foundation', but got {result_df.iloc[0]['employer']}"
    assert result_df.iloc[1]['employer'] == "Frequency Research Foundation", \
        f"Expected Uber on travel day to be 'Frequency Research Foundation', but got {result_df.iloc[1]['employer']}"
    assert result_df.iloc[2]['employer'] == "Personal", \
        f"Expected Amazon on travel day to remain 'Personal', but got {result_df.iloc[2]['employer']}"
    assert result_df.iloc[3]['employer'] == "Personal", \
        f"Expected Starbucks on non-travel day to remain 'Personal', but got {result_df.iloc[3]['employer']}"

    print("Test 3: Multiple transactions - Passed")


if __name__ == "__main__":
    try:
        test_starbucks_travel_day()
        test_starbucks_non_travel_day()
        test_multiple_transactions()
        print("All tests passed successfully!")
    finally:
        # Clean up temporary files
        os.remove('temp_config.json')
        os.remove('temp_categories.json')