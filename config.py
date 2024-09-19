import json
import os

def load_config(config_path='config.json'):
    """
    Loads the configuration file and returns it as a dictionary.

    Args:
        config_path (str): The path to the config file. Default is 'config.json'.

    Returns:
        dict: The configuration settings.

    Raises:
        FileNotFoundError: If the configuration file is not found.
        ValueError: If the configuration file is not in valid JSON format.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file '{config_path}' not found.")

    with open(config_path, 'r') as f:
        try:
            config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON from the config file: {e}")

    # Validate the required keys
    required_keys = ['input_dir', 'output_dir', 'employers', 'employer_rules', 'date_range']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")

    # Ensure directories exist
    config['input_dir'] = os.path.abspath(config['input_dir'])
    config['output_dir'] = os.path.abspath(config['output_dir'])

    if not os.path.exists(config['input_dir']):
        raise FileNotFoundError(f"Input directory '{config['input_dir']}' not found.")

    if not os.path.exists(config['output_dir']):
        os.makedirs(config['output_dir'])

    return config

def get_date_range(config):
    """
    Extracts the start_date and end_date from the configuration.

    Args:
        config (dict): The configuration settings.

    Returns:
        tuple: A tuple containing start_date and end_date as datetime objects.
    """
    date_range = config.get('date_range', {})
    start_date = datetime.strptime(date_range.get('start_date'), '%Y-%m-%d')
    end_date = datetime.strptime(date_range.get('end_date'), '%Y-%m-%d')
    return start_date, end_date

def print_directory_structure(rootdir):
    """
    Prints the directory structure to the console
    """
    for dirpath, dirnames, filenames in os.walk(rootdir):
        level = dirpath.replace(rootdir, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f"{indent}{os.path.basename(dirpath)}/")
        subindent = ' ' * 4 * (level + 1)
        for f in filenames:
            print(f"{subindent}{f}")