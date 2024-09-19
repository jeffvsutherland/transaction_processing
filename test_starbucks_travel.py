import pandas as pd
import json
import os
from datetime import datetime
from rules_processor import RulesProcessor

def test_starbucks_travel():
    # Create a mock config
    config = {
        "submitter_name": "Jeff Sutherland",
        "employee_rules": [
            {
                "name": "Jeff Sutherland",
                "travel_days": ["2022-12-06"],
                "travel_employer": "Frequency Research Foundation"
            }
        ],
        "categories_expensable_on_travel": ["Food"],
        "employer_rules": [
            {
                "description_contains": "Starbucks",
                "employer": "Personal",
                "category": "Food"
            }
        ],
        "default_employer": "Unknown"
    }

    # Create a mock categories file (empty for this test)
    categories = {}

    # Write config and categories to temporary files
    with open('temp_config.json', 'w') as f:
        json.dump(config, f)
    with open('temp_categories.json', 'w') as f:
        json.dump(categories, f)

    try:
        # Create a RulesProcessor instance
        rules_processor = RulesProcessor('temp_config.json', 'temp_categories.json')

        # Create a mock DataFrame with a Starbucks transaction on a travel day
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

        # Apply the rules
        result_df = rules_processor.apply_rules(df)

        # Check if the Starbucks transaction was correctly recategorized
        assert result_df.iloc[0]['employer'] == "Frequency Research Foundation", \
            f"Expected employer to be 'Frequency Research Foundation', but got {result_df.iloc[0]['employer']}"
        assert result_df.iloc[0]['category'] == "Food", \
            f"Expected category to be 'Food', but got {result_df.iloc[0]['category']}"
        assert "Travel expense on 2022-12-06" in result_df.iloc[0]['note'], \
            f"Expected note to contain 'Travel expense on 2022-12-06', but got {result_df.iloc[0]['note']}"

        print("Test passed successfully!")

    finally:
        # Clean up temporary files
        os.remove('temp_config.json')
        os.remove('temp_categories.json')

if __name__ == "__main__":
    test_starbucks_travel()