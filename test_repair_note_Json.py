import json
import os
import re


def load_json_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f), None
    except json.JSONDecodeError as e:
        with open(file_path, 'r') as f:
            content = f.read()
        return None, (str(e), content)


def fix_common_json_errors(content):
    # Remove trailing commas
    content = re.sub(r',\s*}', '}', content)
    content = re.sub(r',\s*]', ']', content)

    # Add missing quotes to keys
    content = re.sub(r'(\w+)(?=\s*:)', r'"\1"', content)

    # Replace single quotes with double quotes
    content = content.replace("'", '"')

    return content


def repair_json_file(file_path):
    print(f"Attempting to repair {file_path}...")

    # Try to load the original file
    data, error = load_json_file(file_path)

    if data is not None:
        print("The JSON file is valid. No repairs needed.")
        return

    error_message, content = error
    print(f"Original error: {error_message}")

    # Attempt to fix common errors
    fixed_content = fix_common_json_errors(content)

    # Try to parse the fixed content
    try:
        data = json.loads(fixed_content)
        print("JSON successfully repaired!")

        # Save the repaired JSON
        backup_path = file_path + '.bak'
        os.rename(file_path, backup_path)
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Original file backed up to {backup_path}")
        print(f"Repaired JSON saved to {file_path}")
    except json.JSONDecodeError as e:
        print("Unable to automatically repair the JSON.")
        print("Here's the partially fixed content:")
        print(fixed_content)
        print(f"Error: {str(e)}")
        print("You may need to manually edit the file to fix remaining issues.")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    note_json_path = os.path.join(script_dir, 'note.json')

    if not os.path.exists(note_json_path):
        print(f"Error: {note_json_path} not found.")
        return

    repair_json_file(note_json_path)


if __name__ == "__main__":
    main()