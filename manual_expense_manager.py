# manual_expense_manager.py

import pandas as pd
import json
import os
from datetime import datetime
from car_expense_calculator import CarExpenseCalculator

# Try to import dotenv, but continue if it's not available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: 'python-dotenv' library not found. Environment variables will not be loaded from .env file.")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: 'requests' library not found. Distance calculation will use manual input.")

class DistanceCalculator:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not self.api_key:
            print("Warning: Google Maps API key not found. Distance calculation will use manual input.")

    def calculate_distance(self, origin, destination):
        if not REQUESTS_AVAILABLE or not self.api_key:
            return self.manual_distance_input()

        base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        params = {
            "origins": origin,
            "destinations": destination,
            "units": "imperial",  # Use miles
            "key": self.api_key
        }

        try:
            response = requests.get(base_url, params=params)
            data = response.json()

            if data['status'] == 'OK':
                distance = data['rows'][0]['elements'][0]['distance']['text']
                miles = float(distance.split()[0])  # Extract the numeric value
                return miles
            else:
                print(f"Error calculating distance: {data['status']}")
                return self.manual_distance_input()
        except Exception as e:
            print(f"Error calculating distance: {str(e)}")
            return self.manual_distance_input()

    def manual_distance_input(self):
        while True:
            try:
                miles = float(input("Please enter the distance in miles: "))
                return miles
            except ValueError:
                print("Invalid input. Please enter a numeric value.")

class ManualExpenseManager:
    def __init__(self, config_file, output_dir):
        self.config_file = config_file
        self.output_dir = output_dir
        self.manual_expenses_file = os.path.join(output_dir, 'manual_expenses.csv')
        self.load_config()
        self.car_expense_calculator = CarExpenseCalculator()
        self.distance_calculator = DistanceCalculator()

    def load_config(self):
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)

    def add_expense(self, date, description, amount, employer, category, note=''):
        new_expense = pd.DataFrame({
            'Date': [date],
            'Description': [description],
            'Amount': [f"{float(amount):.2f}"],  # Ensure Amount has 2 decimal places
            'Bank': ['Manual Entry'],
            'Card': ['Manual'],
            'employer': [employer],
            'category': [category],
            'note': [note],
            'Vendor': [description]  # Use Description as Vendor for manual entries
        })

        if os.path.exists(self.manual_expenses_file):
            existing_expenses = pd.read_csv(self.manual_expenses_file)
            updated_expenses = pd.concat([existing_expenses, new_expense], ignore_index=True)
        else:
            updated_expenses = new_expense

        # Ensure all columns are present and in the correct order
        columns_order = ['Date', 'Description', 'Amount', 'Bank', 'Card', 'employer', 'category', 'note', 'Vendor']
        for col in columns_order:
            if col not in updated_expenses.columns:
                updated_expenses[col] = ''

        updated_expenses = updated_expenses[columns_order]

        updated_expenses.to_csv(self.manual_expenses_file, index=False)
        print(f"Expense added successfully: {description} - ${amount}")

    def add_car_expense(self, date, start_location, end_location, employer, category="Travel"):
        miles = self.distance_calculator.calculate_distance(start_location, end_location)
        amount = self.car_expense_calculator.calculate_car_expense(miles, date)
        description = f"Car travel: {start_location} to {end_location} ({miles:.2f} miles)"
        note = f"IRS standard mileage rate applied for {date[:4]}"

        print(f"\nDistance: {miles:.2f} miles")
        print(f"Mileage rate: ${amount/miles:.3f} per mile")
        print(f"Total expense: ${amount:.2f}")

        confirm = input("Do you want to add this expense? (y/n): ").lower()
        if confirm == 'y':
            self.add_expense(date, description, amount, employer, category, note)
        else:
            print("Expense not added.")

    def view_expenses(self):
        if os.path.exists(self.manual_expenses_file):
            expenses = pd.read_csv(self.manual_expenses_file)
            print(expenses.to_string(index=False))
        else:
            print("No manual expenses found.")

    def remove_expense(self, index):
        if os.path.exists(self.manual_expenses_file):
            expenses = pd.read_csv(self.manual_expenses_file)
            if 0 <= index < len(expenses):
                removed_expense = expenses.iloc[index]
                expenses = expenses.drop(index)
                expenses.to_csv(self.manual_expenses_file, index=False)
                print(f"Expense removed: {removed_expense['Description']} - ${removed_expense['Amount']}")
            else:
                print("Invalid index. No expense removed.")
        else:
            print("No manual expenses found.")

    def get_manual_expenses(self):
        if os.path.exists(self.manual_expenses_file):
            return pd.read_csv(self.manual_expenses_file)
        else:
            return pd.DataFrame()

# Example usage
if __name__ == "__main__":
    manager = ManualExpenseManager('config.json', 'output')

    # Add a manual car expense with automatic distance calculation
    manager.add_car_expense('2023-09-01', 'Boston, MA', 'New York, NY', 'Scrum Inc')

    # View all manual expenses
    manager.view_expenses()

    # Remove an expense (e.g., the first one)
    manager.remove_expense(0)