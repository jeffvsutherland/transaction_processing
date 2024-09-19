import json
import os

class ConfigManager:
    def __init__(self, config_path):
        self.config_path = config_path

    def load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        with open(self.config_path, 'r') as f:
            config = json.load(f)

        # Validate config
        required_keys = ['input_dir', 'output_dir', 'employers', 'employer_rules', 'date_range']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required config key: {key}")

        # Ensure directories exist
        config['input_dir'] = os.path.abspath(config['input_dir'])
        config['output_dir'] = os.path.abspath(config['output_dir'])

        if not os.path.exists(config['input_dir']):
            raise FileNotFoundError(f"Input directory not found: {config['input_dir']}")

        os.makedirs(config['output_dir'], exist_ok=True)

        return config