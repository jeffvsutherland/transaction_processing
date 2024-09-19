import pandas as pd

def read_and_print_csv(file_path):
    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path)

        # Print the DataFrame to the console
        print(df.to_string())  # Use to_string() to ensure the entire DataFrame is printed
    except Exception as e:
        print(f"Error reading the file: {e}")

if __name__ == "__main__":
    # Define the path to the intermediate file
    file_path = 'output/intermediate_2022 crypto_com visa card 7712.csv'

    # Call the function to read and print the CSV file
    read_and_print_csv(file_path)