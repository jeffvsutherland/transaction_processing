# complete_expense_manager.py

import pandas as pd
import json
import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import re

# Load environment variables from .env file
load_dotenv()

class DistanceCalculator:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        if not self.api_key:
            raise ValueError("Google Maps API key not found. Please set GOOGLE_MAPS_API_KEY in your environment variables.")

    def calculate_distance(self, origin, destination):
        base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        params = {
            "origins": origin,
            "destinations": destination,
            "units": "imperial",  # Use miles
            "key": self.api_key
        }

        response = requests.get(base_url, params=params)
        data = response.json()

        if data['status'] == 'OK':
            distance = data['rows'][0]['elements'][0]['distance']['text']
            miles = float(distance.split()[0])  # Extract the numeric value
            return miles
        else:
            raise ValueError(f"Error calculating distance: {data['status']}")

class CarExpenseCalculator:
    def __init__(self):
        self.mileage_rates = self.get_mileage_rates()

    def get_mileage_rates(self):
        # This method scrapes the IRS website for the latest mileage rates
        # Note: Web scraping might break if the IRS changes their website structure
        url = "https://www.irs.gov/tax-professionals/standard-mileage-rates"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        rates = {}
        current_year = datetime.now().year
        for year in range(current_year - 5, current_year + 1):  # Get rates for the last 5 years and current year
            year_pattern = re.compile(f"{year}.*?(\d+\.?\d*)")
            match = soup.find(string=year_pattern)
            if match:
                rate = float(year_pattern.search(match).group(1))
                rates[year] = rate / 100  # Convert cents to dollars

        return rates

    def calculate_car_expense(self, miles, date):
        year = datetime.strptime(date, "%Y-%m-%d").year
        if year in self.mileage_rates:
            rate = self.mileage_rates[year]
        else:
            # If we don't have the rate for the specific year, use the most recent rate
            rate = self.mileage_rates[max(self.mileage_rates.keys())]

        expense = miles * rate
        return round(expense, 2)

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
            'Amount': [amount],
            'Bank': ['Manual Entry'],
            'Card': ['N/A'],
            'employer': [employer],
            'category': [category],
            'note': [note],
            'Vendor': [description]
        })

        if os.path.exists(self.manual_expenses_file):
            existing_expenses = pd.read_csv(self.manual_expenses_file)
            updated_expenses = pd.concat([existing_expenses, new_expense], ignore_index=True)
        else:
            updated_expenses = new_expense

        updated_expenses.to_csv(self.manual_expenses_file, index=False)
        print(f"Expense added successfully: {description} - ${amount}")

    def add_car_expense(self, date, start_location, end_location, employer, category="Travel"):
        try:
            miles = self.distance_calculator.calculate_distance(start_location, end_location)
            amount = self.car_expense_calculator.calculate_car_expense(miles, date)
            description = f"Car travel: {start_location} to {end_location} ({miles:.2f} miles)"
            note = f"IRS standard mileage rate applied for {date[:4]}"
            self.add_expense(date, description, amount, employer, category, note)
        except ValueError as e:
            print(f"Error calculating distance: {str(e)}")

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

def get_user_input(prompt, data_type=str):
    while True:
        try:
            return data_type(input(prompt))
        except ValueError:
            print(f"Invalid input. Please enter a valid {data_type.__name__}.")

def main():
    config_file = 'config.json'
    output_dir = 'output'

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Create a dummy config file if it doesn't exist
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            json.dump({"default_employer": "Unknown"}, f)

    manager = ManualExpenseManager(config_file, output_dir)

    while True:
        print("\n1. Add manual expense")
        print("2. Add car expense (with automatic distance calculation)")
        print("3. View manual expenses")
        print("4. Remove manual expense")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            date = get_user_input("Enter date (YYYY-MM-DD): ")
            description = get_user_input("Enter description: ")
            amount = get_user_input("Enter amount: ", float)
            employer = get_user_input("Enter employer: ")
            category = get_user_input("Enter category: ")
            note = get_user_input("Enter note (optional): ")

            manager.add_expense(date, description, amount, employer, category, note)

        elif choice == '2':
            date = get_user_input("Enter date (YYYY-MM-DD): ")
            start_location = get_user_input("Enter start location (e.g., 'Boston, MA'): ")
            end_location = get_user_input("Enter end location (e.g., 'New York, NY'): ")
            employer = get_user_input("Enter employer: ")

            manager.add_car_expense(date, start_location, end_location, employer)

        elif choice == '3':
            manager.view_expenses()

        elif choice == '4':
            manager.view_expenses()
            index = get_user_input("Enter the index of the expense to remove: ", int)
            manager.remove_expense(index)

        elif choice == '5':
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()