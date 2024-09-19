# utils.py

import json
import logging
import os
import subprocess
import pandas as pd

logger = logging.getLogger(__name__)


def setup_logging(log_file=None):
    """Set up logging configuration."""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format)

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(log_format))
        logging.getLogger().addHandler(file_handler)


def load_json(file_path):
    """Load JSON data from a file."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        logger.info(f"JSON data loaded from {file_path}")
        return data
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in file: {file_path}")
        raise


def save_json(file_path, data):
    """Save JSON data to a file."""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"JSON data saved to {file_path}")
    except IOError:
        logger.error(f"Error writing to file: {file_path}")
        raise


def load_config(config_path):
    """Load configuration from a JSON file."""
    return load_json(config_path)


def load_notes(notes_path):
    """Load notes from a JSON file."""
    try:
        return load_json(notes_path)
    except FileNotFoundError:
        logger.warning(f"Notes file not found: {notes_path}")
        return {}


def get_directory_structure(rootdir):
    """Get the directory structure as a string."""
    structure = ""
    for dirpath, dirnames, filenames in os.walk(rootdir):
        level = dirpath.replace(rootdir, '').count(os.sep)
        indent = ' ' * 4 * level
        structure += f"{indent}{os.path.basename(dirpath)}/\n"
        subindent = ' ' * 4 * (level + 1)
        for f in filenames:
            structure += f"{subindent}{f}\n"
    return structure


def list_input_files(input_dir):
    """List input CSV files and their columns."""
    input_files = {}
    for file in os.listdir(input_dir):
        if file.lower().endswith('.csv'):
            filepath = os.path.join(input_dir, file)
            df = pd.read_csv(filepath, nrows=0)  # Read only the header
            input_files[file] = list(df.columns)
    return input_files


def ensure_dir(directory):
    """Ensure that a directory exists, creating it if necessary."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.info(f"Created directory: {directory}")


def convert_to_pdf(input_path, output_path):
    """Convert a Markdown file to PDF using Pandoc."""
    try:
        subprocess.run(["pandoc", input_path, "-o", output_path], check=True)
        logger.info(f"Converted {input_path} to PDF: {output_path}")
    except subprocess.CalledProcessError:
        logger.error(f"Failed to convert {input_path} to PDF")
        raise
    except FileNotFoundError:
        logger.error("Pandoc is not installed or not in the system PATH")
        raise


def is_pdf_conversion_available():
    """Check if Pandoc is available for PDF conversion."""
    try:
        subprocess.run(["pandoc", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


if __name__ == "__main__":
    # This allows for easy testing of this module independently
    setup_logging()

    # Test config loading
    config = load_config('config.json')
    print("Loaded config:", config)

    # Test notes loading
    notes = load_notes('note.json')
    print("Loaded notes:", notes)

    # Test directory structure
    print("Directory structure:")
    print(get_directory_structure('.'))

    # Test listing input files
    if 'input_dir' in config:
        input_files = list_input_files(config['input_dir'])
        print("Input files:", input_files)

    # Test directory creation
    ensure_dir('test_output')

    # Test PDF conversion availability
    pdf_available = is_pdf_conversion_available()
    print("PDF conversion available:", pdf_available)

    if pdf_available:
        # Test PDF conversion (assuming you have a test.md file)
        if os.path.exists('test.md'):
            convert_to_pdf('test.md', 'test_output/test.pdf')
        else:
            print("test.md not found, skipping PDF conversion test")

    print("Utility tests completed.")