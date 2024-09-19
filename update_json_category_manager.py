# update_json_category_manager.py

class UpdateJsonCategoryManager:
    def __init__(self, categories, valid_employers):
        self.categories = categories
        self.valid_employers = valid_employers

    def update_categories(self, transaction_manager):
        for transaction in transaction_manager.transactions:
            category = transaction.data['category']
            employer = transaction.data['employer']
            if category not in self.categories:
                self.categories[category] = []
            if employer in self.valid_employers and employer not in self.categories[category]:
                self.categories[category].append(employer)

    def display_categories(self):
        for category, employers in self.categories.items():
            print(f"{category}: {', '.join(employers)}")