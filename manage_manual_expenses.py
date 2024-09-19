# manage_manual_expenses.py

import os
import sys

# Add the directory containing the script to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

from manual_expense_manager import ManualExpenseManager


def main():
    config_file = 'config.json'
    output_dir = 'output'

    manager = ManualExpenseManager(config_file, output_dir)

    while True:
        print("\n1. Add a new expense")
        print("2. Add a car expense")
        print("3. View all expenses")
        print("4. Remove an expense")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            date = input("Enter date (YYYY-MM-DD): ")
            description = input("Enter description: ")
            amount = float(input("Enter amount: "))
            employer = input("Enter employer: ")
            category = input("Enter category: ")
            note = input("Enter note (optional): ")
            manager.add_expense(date, description, amount, employer, category, note)
        elif choice == '2':
            date = input("Enter date (YYYY-MM-DD): ")
            start_location = input("Enter start location: ")
            end_location = input("Enter end location: ")
            employer = input("Enter employer: ")
            category = input("Enter category (default: Travel): ") or "Travel"
            manager.add_car_expense(date, start_location, end_location, employer, category)
        elif choice == '3':
            manager.view_expenses()
        elif choice == '4':
            index = int(input("Enter the index of the expense to remove: "))
            manager.remove_expense(index)
        elif choice == '5':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()