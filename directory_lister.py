import os

def generate_directory_listing(directory, output_directory):
    output_file = os.path.join(output_directory, 'script_list_with_contents.txt')
    with open(output_file, 'w') as f:
        for root, dirs, files in os.walk(directory):
            # Exclude __pycache__ and env directories
            dirs[:] = [d for d in dirs if d not in ('__pycache__', 'env', '.venv', 'venv')]

            for file in files:
                if file.endswith('.py') or file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    local_filename = os.path.relpath(file_path, directory)
                    f.write(f"Filename: {local_filename}\n")
                    f.write("Contents:\n")
                    with open(file_path, 'r') as content_file:
                        f.write(content_file.read())
                    f.write("\n\n")  # Separate each file with a newline for clarity

    return output_file

if __name__ == "__main__":
    directory_to_search = '/Users/jeffsutherland/Frequency Research Foundation Inc. Dropbox/Frequency Lab/Python/Expenses/chatGPT4o scripts/transaction_processor'
    output_directory = os.path.join(os.getcwd(), 'output')
    os.makedirs(output_directory, exist_ok=True)
    output_file = generate_directory_listing(directory_to_search, output_directory)
    print(f"File names and their contents have been written to {output_file}")