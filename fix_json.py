import json
import os
import sys


def fix_json_file(file_path):
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        # Remove any trailing commas
        content = content.replace(',}', '}').replace(',]', ']')

        # Try to parse the JSON
        data = json.loads(content)

        # If successful, write back the correctly formatted JSON
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Successfully fixed and formatted {file_path}")
        return True

    except json.JSONDecodeError as e:
        print(f"JSON decode error: {str(e)}")
        print("Attempting to fix the error...")

        lines = content.split('\n')
        problematic_line = lines[e.lineno - 1]
        print(f"Problematic line ({e.lineno}): {problematic_line}")

        # Try to fix common issues
        if e.msg.startswith('Expecting value'):
            # Remove the problematic line if it's empty or just contains whitespace
            if not problematic_line.strip():
                lines.pop(e.lineno - 1)
                print(f"Removed empty line at {e.lineno}")
            else:
                print(f"Unable to automatically fix the error at line {e.lineno}. Please check this line manually.")
                return False

        # Join the lines back and try to save
        fixed_content = '\n'.join(lines)
        try:
            # Try to parse the JSON again
            json.loads(fixed_content)

            # If successful, write back the fixed content
            with open(file_path, 'w') as f:
                f.write(fixed_content)
            print(f"Fixed the JSON error in {file_path}")
            return True
        except json.JSONDecodeError:
            print("Unable to automatically fix all JSON errors. Please check the file manually.")
            return False

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return False


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config.json')

    if not os.path.exists(config_path):
        print(f"config.json not found at {config_path}")
        sys.exit(1)

    if fix_json_file(config_path):
        print("JSON file fixed successfully. You can now run the main script again.")
    else:
        print("Failed to fix the JSON file automatically. Please check and correct it manually.")


if __name__ == "__main__":
    main()