import os
from config_manager import ConfigManager
from config import print_directory_structure

def main():
    # Get the current script's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the full path to the config.json file
    config_path = os.path.join(current_dir, 'config.json')

    print(f"Working directory: {current_dir}")
    print(f"Config file path: {config_path}")

    if os.path.exists(config_path):
        print(f"Config file found: {config_path}")
    else:
        print(f"Config file not found: {config_path}")
        return

    config_manager = ConfigManager(config_path)

    try:
        config = config_manager.load_config()
        print("Config loaded successfully")
        print(f"Input directory: {config['input_dir']}")
        print(f"Output directory: {config['output_dir']}")

        print("\nDirectory structure:")
        print_directory_structure(config['input_dir'])
    except Exception as e:
        print(f"Error loading config: {str(e)}")

if __name__ == "__main__":
    main()