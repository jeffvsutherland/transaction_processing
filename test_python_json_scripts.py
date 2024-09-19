import os
import ast
import json

def get_files(directory):
    """Get all Python and JSON files in the given directory."""
    python_files = [f for f in os.listdir(directory) if f.endswith('.py')]
    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
    print(f"Python files found: {python_files}")
    print(f"JSON files found: {json_files}")
    return python_files, json_files

def get_imports(file_path):
    """Get all imports from a Python file."""
    with open(file_path, 'r') as file:
        tree = ast.parse(file.read())

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.append(n.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module if node.module else ''
            for n in node.names:
                imports.append(f"{module}.{n.name}")

    print(f"Imports found in {file_path}: {imports}")
    return imports

def is_local_import(import_name, python_files):
    """Check if an import is a local file."""
    parts = import_name.split('.')
    for i in range(len(parts), 0, -1):
        potential_file = '.'.join(parts[:i]) + '.py'
        if potential_file in python_files:
            print(f"Checking if {import_name} is local: True (matches {potential_file})")
            return potential_file
    print(f"Checking if {import_name} is local: False")
    return None

def generate_dependency_tree(directory, python_files):
    """Generate a dependency tree for Python files in the directory."""
    dependency_tree = {}

    for file in python_files:
        file_path = os.path.join(directory, file)
        imports = get_imports(file_path)
        local_imports = [is_local_import(imp, python_files) for imp in imports]
        local_imports = [imp for imp in local_imports if imp]
        dependency_tree[file] = local_imports
        print(f"Dependencies for {file}: {local_imports}")

    return dependency_tree

def get_all_dependencies(dependency_tree, file, visited=None):
    """Get all dependencies for a file, including nested dependencies."""
    if visited is None:
        visited = set()

    if file not in dependency_tree or file in visited:
        return visited

    visited.add(file)
    for dependency in dependency_tree[file]:
        get_all_dependencies(dependency_tree, dependency, visited)

    return visited

def write_markdown_output(input_dir, output_dir, output_file, python_files, json_files):
    """Write the contents of the specified files to a single markdown file in the output directory."""
    os.makedirs(output_dir, exist_ok=True)
    full_output_path = os.path.join(output_dir, output_file)
    print(f"Attempting to write to file: {full_output_path}")

    try:
        with open(full_output_path, 'w') as out_file:
            # Write Python files
            for file in sorted(python_files):
                input_path = os.path.join(input_dir, file)
                print(f"Processing Python file: {input_path}")

                out_file.write(f"# {file}\n\n")
                out_file.write("```python\n")

                try:
                    with open(input_path, 'r') as in_file:
                        content = in_file.read()
                        out_file.write(content)
                        print(f"Successfully read and wrote contents of {file}")
                except Exception as e:
                    print(f"Error reading {file}: {str(e)}")

                out_file.write("\n```\n\n")

            # Write JSON files
            for file in sorted(json_files):
                input_path = os.path.join(input_dir, file)
                print(f"Processing JSON file: {input_path}")

                out_file.write(f"# {file}\n\n")
                out_file.write("```json\n")

                try:
                    with open(input_path, 'r') as in_file:
                        json_content = json.load(in_file)
                        json_str = json.dumps(json_content, indent=2)
                        out_file.write(json_str)
                        print(f"Successfully read and wrote contents of {file}")
                except Exception as e:
                    print(f"Error reading {file}: {str(e)}")

                out_file.write("\n```\n\n")

        print(f"Successfully wrote contents of {len(python_files) + len(json_files)} files to {full_output_path}")
        print(f"File size: {os.path.getsize(full_output_path)} bytes")
    except Exception as e:
        print(f"Error writing to {full_output_path}: {str(e)}")

    if os.path.exists(full_output_path):
        print(f"File {full_output_path} exists after writing.")
    else:
        print(f"File {full_output_path} does not exist after attempted writing.")

def main():
    input_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(input_dir, 'output')
    output_file = 'expense_report_scripts_and_configs.md'

    print(f"Analyzing directory: {input_dir}")
    print(f"Output will be saved in: {output_dir}")

    python_files, json_files = get_files(input_dir)
    dependency_tree = generate_dependency_tree(input_dir, python_files)

    print("\nFull dependency tree:")
    for file, deps in dependency_tree.items():
        print(f"{file}: {deps}")

    print("\n# Python Project Structure")
    print("\n## File Dependencies\n")
    if 'main.py' in dependency_tree:
        all_dependencies = get_all_dependencies(dependency_tree, 'main.py')
        all_dependencies.add('main.py')  # Ensure main.py is included

        # Print dependency tree
        for file in sorted(all_dependencies):
            print(f"- {file}")
            if file in dependency_tree:
                for dep in sorted(dependency_tree[file]):
                    print(f"  - {dep}")

        write_markdown_output(input_dir, output_dir, output_file, all_dependencies, json_files)
    else:
        print("main.py not found. Including all Python and JSON files.")
        write_markdown_output(input_dir, output_dir, output_file, python_files, json_files)

if __name__ == "__main__":
    main()