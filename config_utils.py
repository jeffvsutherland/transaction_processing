import os
import json

def load_config(config_path):
    with open(config_path, 'r') as file:
        return json.load(file)

def get_directory_structure(rootdir):
    dir_structure = {}
    for dirpath, dirnames, filenames in os.walk(rootdir):
        dir_structure[dirpath] = {'dirs': dirnames, 'files': filenames}
    return dir_structure

def list_input_files(input_dir, extension):
    return [f for f in os.listdir(input_dir) if f.endswith(extension)]