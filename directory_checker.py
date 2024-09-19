# directory_checker.py
import os
import sys

def get_directory_structure(rootdir):
    """
    Creates a nested dictionary that represents the folder structure of rootdir
    """
    dir_structure = {}
    for dirpath, dirnames, filenames in os.walk(rootdir):
        rel_path = os.path.relpath(dirpath, rootdir)
        if rel_path == '.':
            rel_path = ''
        dir_structure[rel_path] = filenames
    return dir_structure

def check_directory_structure(current_dir, expected_structure):
    """
    Checks if the current directory structure matches the expected structure.
    """
    exclude_dirs = ['.venv', '__pycache__', '.git']  # Define exclude_dirs
    current_structure = get_directory_structure(current_dir)
    errors = []

    for dir_path, expected_files in expected_structure.items():
        if dir_path in exclude_dirs:
            continue
        if dir_path not in current_structure:
            errors.append(f"Missing directory: {dir_path}")
        else:
            current_files = current_structure[dir_path]
            for expected_file in expected_files:
                if expected_file not in current_files:
                    errors.append(f"Missing file: {os.path.join(dir_path, expected_file)}")

    return errors