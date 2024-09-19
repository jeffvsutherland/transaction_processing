# list_py_files_and_imports.py
import ast
import os

def get_imports(file_path):
    with open(file_path, 'r') as file:
        tree = ast.parse(file.read())

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module
            for alias in node.names:
                imports.append(f"{module}.{alias.name}")

    return imports

def list_py_files(directory):
    return [f for f in os.listdir(directory) if f.endswith('.py')]

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    py_files = list_py_files(current_dir)

    for file in py_files:
        file_path = os.path.join(current_dir, file)
        print(f"\nImports in {file}:")
        imports = get_imports(file_path)
        for imp in imports:
            print(f"  - {imp}")