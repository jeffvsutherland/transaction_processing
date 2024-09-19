# bank_data_manager.py

import os
import csv
import logging

class BankDataManager:
    def __init__(self, input_dir):
        self.input_dir = input_dir
        self.bank_files = []
        self.file_structures = {}
        self.load_bank_files()

    def load_bank_files(self):
        for filename in os.listdir(self.input_dir):
            if filename.lower().endswith('.csv'):
                file_path = os.path.join(self.input_dir, filename)
                self.bank_files.append(file_path)
                self.analyze_file_structure(file_path)

    def analyze_file_structure(self, file_path):
        try:
            with open(file_path, 'r') as csvfile:
                reader = csv.reader(csvfile)
                headers = next(reader, None)  # Read the first row as headers
                if headers:
                    self.file_structures[os.path.basename(file_path)] = headers
                else:
                    logging.warning(f"No headers found in {file_path}")
        except Exception as e:
            logging.error(f"Error reading {file_path}: {str(e)}")

    def get_file_structures(self):
        return self.file_structures

    def get_bank_files(self):
        return self.bank_files