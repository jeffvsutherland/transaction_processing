print("Starting imports")
import os
print("Imported os")
import pandas as pd
print("Imported pandas")
from datetime import datetime
print("Imported datetime")
from utils import load_config, get_directory_structure, list_input_files
print("Imported from utils")
from transaction_processing import process_bank_file, merge_transactions, log
print("Imported from transaction_processing")
from create_merged_files import create_final_merged_file, save_merged_file
print("Imported from create_merged_files")
print("All imports completed")

def main():
    print("Main function executed successfully")

if __name__ == "__main__":
    main()