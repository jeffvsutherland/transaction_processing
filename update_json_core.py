# update_json_core.py

import json
import pandas as pd
import logging
from update_json_rule_manager import UpdateJsonRuleManager
from update_json_transaction_manager import UpdateJsonTransactionManager
from update_json_category_manager import UpdateJsonCategoryManager
from update_json_processor import UpdateJsonProcessor
from update_json_ui import UpdateJsonUI

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UpdateJsonCore:
    def __init__(self, config_file, categories_file, transactions_file):
        self.config_file = config_file
        self.categories_file = categories_file
        self.transactions_file = transactions_file
        self.load_files()
        self.rule_manager = UpdateJsonRuleManager(self.config['employer_rules'])
        self.transaction_manager = UpdateJsonTransactionManager(self.transactions_df, self.config['employers'])
        self.category_manager = UpdateJsonCategoryManager(self.categories, self.config['employers'])
        self.processor = UpdateJsonProcessor(self.rule_manager, self.transaction_manager)
        self.ui = UpdateJsonUI(self)

    def load_files(self):
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)
        with open(self.categories_file, 'r') as f:
            self.categories = json.load(f)
        self.transactions_df = pd.read_csv(self.transactions_file)

    def save_progress(self):
        self.transactions_df = self.transaction_manager.to_dataframe()
        self.transactions_df.to_csv(self.transactions_file, index=False)
        logger.info(f"Progress saved to {self.transactions_file}")

        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
        logger.info(f"Config saved to {self.config_file}")

        with open(self.categories_file, 'w') as f:
            json.dump(self.categories, f, indent=2)
        logger.info(f"Categories saved to {self.categories_file}")

    def run(self):
        self.ui.main_menu()

def main():
    config_file = 'config.json'
    categories_file = 'categories.json'
    transactions_file = 'output/merged_transactions.csv'

    core = UpdateJsonCore(config_file, categories_file, transactions_file)
    core.run()

if __name__ == "__main__":
    main()