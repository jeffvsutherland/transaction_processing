# update_json_ui.py

from tabulate import tabulate
import pandas as pd


class UpdateJsonUI:
    def __init__(self, core):
        self.core = core

    def main_menu(self):
        while True:
            print("\n--- Main Menu ---")
            print("1. Process all transactions")
            print("2. View current rules")
            print("3. Add new rule")
            print("4. Modify existing rule")
            print("5. Apply bulk rule")
            print("6. Review vendor-specific transactions")
            print("7. Process unknown transactions")
            print("8. Search and update transactions")
            print("9. Manual review of Amazon/Kindle transactions")
            print("10. List and update travel day transactions")
            print("11. Save and exit")

            choice = input("Enter your choice (1-11): ")

            if choice == '1':
                self.core.processor.apply_rules_to_transactions()
            elif choice == '2':
                self.core.rule_manager.display_rules()
            elif choice == '3':
                self.add_new_rule()
            elif choice == '4':
                self.modify_existing_rule()
            elif choice == '5':
                self.apply_bulk_rule()
            elif choice == '6':
                self.review_vendor_transactions()
            elif choice == '7':
                self.process_unknown_transactions()
            elif choice == '8':
                self.search_and_update_transactions()
            elif choice == '9':
                self.manual_review_amazon_kindle()
            elif choice == '10':
                self.list_and_update_travel_day_transactions()
            elif choice == '11':
                self.core.save_progress()
                print("All changes saved. Exiting the program.")
                return
            else:
                print("Invalid choice. Please enter a number between 1 and 11.")

            input("Press Enter to continue...")

    def add_new_rule(self):
        description = input("Enter the description to match: ")
        employer = input("Enter the employer: ")
        category = input("Enter the category: ")
        note = input("Enter a note (optional): ")
        card = input("Enter a specific card number (optional): ")

        new_rule = {
            "description_contains": description,
            "employer": employer,
            "category": category
        }
        if note:
            new_rule["note"] = note
        if card:
            new_rule["card"] = card

        self.core.rule_manager.add_rule(new_rule)
        print("New rule added successfully.")

    def modify_existing_rule(self):
        self.core.rule_manager.display_rules()
        rule_index = int(input("Enter the index of the rule you want to modify: "))
        rules = self.core.rule_manager.rules
        if 0 <= rule_index < len(rules):
            rule = rules[rule_index]
            print(f"Modifying rule: {rule.to_dict()}")

            new_rule = {
                "description_contains": input(
                    f"Enter new description (current: {rule.description_contains}): ") or rule.description_contains,
                "employer": input(f"Enter new employer (current: {rule.employer}): ") or rule.employer,
                "category": input(f"Enter new category (current: {rule.category}): ") or rule.category,
                "note": input(f"Enter new note (current: {rule.note}): ") or rule.note,
            }

            card = input(f"Enter new card number (current: {rule.card}, leave blank to remove): ")
            if card:
                new_rule["card"] = card
            elif rule.card:
                new_rule["card"] = None

            self.core.rule_manager.modify_rule(rule_index, new_rule)
            print("Rule modified successfully.")
        else:
            print("Invalid rule index.")

    def apply_bulk_rule(self):
        description = input("Enter the description to match: ")
        employer = input("Enter the employer: ")
        category = input("Enter the category: ")
        note = input("Enter a note (optional): ")
        card = input("Enter a specific card number (optional): ")

        rule = {
            "description_contains": description,
            "employer": employer,
            "category": category
        }
        if note:
            rule["note"] = note
        if card:
            rule["card"] = card

        changes_made = self.core.transaction_manager.apply_bulk_rule(rule)
        print(f"Bulk rule applied. {changes_made} transactions updated.")

    def review_vendor_transactions(self):
        vendor = input("Enter the vendor name to review: ")
        transactions = self.core.transaction_manager.review_vendor_transactions(vendor)
        if transactions:
            df = pd.DataFrame([t.data for t in transactions])
            print(tabulate(df[['Date', 'Description', 'Amount', 'Card', 'employer', 'category']], headers='keys',
                           tablefmt='pipe'))
        else:
            print(f"No transactions found for vendor '{vendor}'")

    def process_unknown_transactions(self):
        unknown_transactions = self.core.transaction_manager.get_unknown_transactions()
        if not unknown_transactions:
            print("No unknown transactions found.")
            return

        print("Processing unknown transactions:")
        for transaction in unknown_transactions:
            print(f"\nDate: {transaction.data['Date']} | Bank: {transaction.data['Bank']}")
            print(
                f"Transaction: {transaction.data['Description']} | Amount: {transaction.data['Amount']} | Card: {transaction.data['Card']}")
            employer = input("Enter employer (or 'skip' to move to next): ")
            if employer.lower() == 'skip':
                continue
            category = input("Enter category: ")
            note = input("Enter note (optional): ")

            new_data = {'employer': employer, 'category': category}
            if note:
                new_data['note'] = note
            self.core.transaction_manager.update_transaction(transaction, new_data)

            add_rule = input("Add this as a new rule? (y/n): ")
            if add_rule.lower() == 'y':
                new_rule = {
                    "description_contains": transaction.data['Description'],
                    "employer": employer,
                    "category": category
                }
                if note:
                    new_rule["note"] = note

                self.core.rule_manager.add_rule(new_rule)
                print("New rule added.")

        print("Unknown transactions processed.")

    def search_and_update_transactions(self):
        search_term = input("Enter search term: ")
        transactions = self.core.transaction_manager.search_transactions(search_term)
        if not transactions:
            print("No matching transactions found.")
            return

        df = pd.DataFrame([t.data for t in transactions])
        print("\nMatching transactions:")
        print(tabulate(df[['Date', 'Description', 'Amount', 'Card', 'employer', 'category']], headers='keys',
                       tablefmt='pipe'))

        update = input("Do you want to update these transactions? (y/n): ")
        if update.lower() == 'y':
            new_employer = input("Enter new employer (or press enter to skip): ")
            new_category = input("Enter new category (or press enter to skip): ")
            new_note = input("Enter new note (or press enter to skip): ")

            new_data = {}
            if new_employer:
                new_data['employer'] = new_employer
            if new_category:
                new_data['category'] = new_category
            if new_note:
                new_data['note'] = new_note

            for transaction in transactions:
                self.core.transaction_manager.update_transaction(transaction, new_data)

            print("Transactions updated successfully.")

            add_rule = input("Do you want to add this as a new rule? (y/n): ")
            if add_rule.lower() == 'y':
                new_rule = {
                    "description_contains": search_term,
                    "employer": new_employer,
                    "category": new_category
                }
                if new_note:
                    new_rule["note"] = new_note

                self.core.rule_manager.add_rule(new_rule)
                print("New rule added to config.json")
        else:
            print("Update cancelled.")

    def manual_review_amazon_kindle(self):
        kindle_transactions = self.core.transaction_manager.search_transactions('kindle')
        amazon_transactions = self.core.transaction_manager.search_transactions('amazon')
        transactions_to_review = kindle_transactions + amazon_transactions

        if not transactions_to_review:
            print("No Amazon or Kindle transactions to review.")
            return

        print(f"Found {len(transactions_to_review)} Amazon/Kindle transactions to review.")
        for transaction in transactions_to_review:
            print(f"\nTransaction: {transaction.data['Description']}")
            print(f"Amount: {transaction.data['Amount']}")
            print(f"Date: {transaction.data['Date']}")
            print(f"Card: {transaction.data['Card']}")
            print(f"Current Employer: {transaction.data['employer']}")
            print(f"Current Category: {transaction.data['category']}")

            update = input("Do you want to update this transaction? (y/n): ")
            if update.lower() == 'y':
                employer = input("Enter employer (Personal/Scrum Inc/Frequency Research Foundation/etc.): ")
                category = input("Enter category: ")
                note = input("Enter note (optional): ")

                new_data = {'employer': employer, 'category': category}
                if note:
                    new_data['note'] = note
                self.core.transaction_manager.update_transaction(transaction, new_data)

                print(
                    f"Updated transaction: {transaction.data['Description']} - Employer: {employer}, Category: {category}")

        print("Manual review of Amazon/Kindle transactions completed.")

    def list_and_update_travel_day_transactions(self):
        employee_rules = self.core.config.get('employee_rules', [])
        travel_days = []
        travel_employer = None
        for rule in employee_rules:
            if rule['name'] == self.core.config.get('submitter_name'):
                travel_days = rule.get('travel_days', [])
                travel_employer = rule.get('travel_employer')
                break

        if not travel_days:
            print("No travel days found in the configuration for the current submitter.")
            return

        travel_transactions = self.core.transaction_manager.get_travel_day_transactions(travel_days)

        if not travel_transactions:
            print("No transactions found on travel days.")
            return

        print(f"\nTransactions on travel days ({', '.join(travel_days)})")
        df = pd.DataFrame([t.data for t in travel_transactions])
        print(tabulate(df[['Date', 'Description', 'Amount', 'Card', 'employer', 'category']], headers='keys',
                       tablefmt='pipe'))

        update = input("Do you want to update these transactions? (y/n): ")
        if update.lower() == 'y':
            new_employer = input(
                f"Enter new employer (default: {travel_employer}, press enter to skip): ") or travel_employer
            new_category = input("Enter new category (or press enter to skip): ")
            new_note = input("Enter new note (or press enter to skip): ")

            new_data = {}
            if new_employer:
                new_data['employer'] = new_employer
            if new_category:
                new_data['category'] = new_category
            if new_note:
                new_data['note'] = new_note

            for transaction in travel_transactions:
                self.core.transaction_manager.update_transaction(transaction, new_data)

            print("Travel day transactions updated successfully.")
        else:
            print("Update cancelled.")


if __name__ == "__main__":
    print("This script is not meant to be run directly. Please run update_json_core.py instead.")