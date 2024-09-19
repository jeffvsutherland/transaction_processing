import csv
import json
import os
from pathlib import Path


def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)


def load_csv(file_path):
    with open(file_path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        return list(reader)


def main():
    try:
        # Load configuration
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, 'config.json')
        print(f"Attempting to load config from: {config_path}")
        config = load_config(config_path)

        print("Config file contents:")
        print(json.dumps(config, indent=2))

        if 'output_dir' not in config:
            print("Error: 'output_dir' key not found in config. Available keys:")
            print(", ".join(config.keys()))
            return

        csv_path = Path(config['output_dir']) / 'merged_transactions.csv'
        print(f"Attempting to load CSV from: {csv_path}")

        # Load CSV data
        data = load_csv(csv_path)

        if not data:
            print("No data found in the CSV file.")
            return

        # Print column names
        print("\nColumns in the CSV:", ', '.join(data[0].keys()))

        # Check for 'note' column
        if 'note' in data[0]:
            print("\nAnalyzing 'note' column:")
            note_values = set(row['note'] for row in data if row['note'])
            print(f"Unique non-empty values in 'note' column: {note_values}")
        else:
            print("\n'note' column not found in the CSV.")

        # Print a sample of rows
        print("\nSample rows:")
        for row in data[:5]:
            print(row)

    except FileNotFoundError as e:
        print(f"Error: File not found. {e}")
    except json.JSONDecodeError:
        print("Error: Invalid JSON in config file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        print(traceback.format_exc())


if __name__ == "__main__":
    main()