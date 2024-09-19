import os
import ast
import json
import sys
import traceback
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

def get_files(directory):
    """Get all Python and JSON files in the given directory."""
    try:
        python_files = [f for f in os.listdir(directory) if f.endswith('.py')]
        json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
        print(f"Python files found: {python_files}")
        print(f"JSON files found: {json_files}")
        return python_files, json_files
    except Exception as e:
        print(f"Error in get_files: {str(e)}")
        return [], []

def get_imports(file_path):
    """Get all imports from a Python file."""
    try:
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
    except Exception as e:
        print(f"Error in get_imports for {file_path}: {str(e)}")
        return []

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

def write_markdown_and_pdf_output(input_dir, output_dir, output_file, python_files, json_files):
    """Write the contents of the specified files to a single markdown file and a PDF file in the output directory."""
    os.makedirs(output_dir, exist_ok=True)
    md_output_path = os.path.join(output_dir, f"{output_file}.md")
    pdf_output_path = os.path.join(output_dir, f"{output_file}.pdf")
    print(f"Attempting to write to files: {md_output_path} and {pdf_output_path}")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    title = f"QuickAIReports Code and Config - {timestamp}"

    md_content = [f"# {title}\n\n"]
    pdf_content = []
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(name='Center', alignment=TA_CENTER, fontSize=14, spaceAfter=20)

    try:
        # Add title to PDF content
        pdf_content.append(Paragraph(title, title_style))
        pdf_content.append(Spacer(1, 12))

        # Process files and generate content for both Markdown and PDF
        for file in sorted(python_files):
            input_path = os.path.join(input_dir, file)
            print(f"Processing Python file: {input_path}")

            md_content.append(f"## {file}\n\n")
            md_content.append("```python\n")
            pdf_content.append(Paragraph(f"## {file}", styles['Heading2']))

            try:
                with open(input_path, 'r') as in_file:
                    content = in_file.read()
                    md_content.append(content)
                    pdf_content.append(Preformatted(content, styles['Code']))
                    print(f"Successfully read contents of {file}")
            except Exception as e:
                print(f"Error reading {file}: {str(e)}")

            md_content.append("\n```\n\n")
            pdf_content.append(Spacer(1, 12))

        for file in sorted(json_files):
            input_path = os.path.join(input_dir, file)
            print(f"Processing JSON file: {input_path}")

            md_content.append(f"## {file}\n\n")
            md_content.append("```json\n")
            pdf_content.append(Paragraph(f"## {file}", styles['Heading2']))

            try:
                with open(input_path, 'r') as in_file:
                    json_content = json.load(in_file)
                    json_str = json.dumps(json_content, indent=2)
                    md_content.append(json_str)
                    pdf_content.append(Preformatted(json_str, styles['Code']))
                    print(f"Successfully read contents of {file}")
            except Exception as e:
                print(f"Error reading {file}: {str(e)}")

            md_content.append("\n```\n\n")
            pdf_content.append(Spacer(1, 12))

        # Write Markdown file
        with open(md_output_path, 'w') as md_file:
            md_file.writelines(md_content)

        # Generate PDF file
        doc = SimpleDocTemplate(pdf_output_path, pagesize=letter)
        doc.build(pdf_content)

        print(f"Successfully wrote contents of {len(python_files) + len(json_files)} files to {md_output_path} and {pdf_output_path}")
        print(f"Markdown file size: {os.path.getsize(md_output_path)} bytes")
        print(f"PDF file size: {os.path.getsize(pdf_output_path)} bytes")
    except Exception as e:
        print(f"Error writing output: {str(e)}")

    if os.path.exists(md_output_path) and os.path.exists(pdf_output_path):
        print(f"Files {md_output_path} and {pdf_output_path} exist after writing.")
    else:
        print(f"One or both output files do not exist after attempted writing.")

def main():
    try:
        print("Starting script execution...")
        input_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(input_dir, 'output')
        output_file = 'expense_report_scripts_and_configs'

        print(f"Analyzing directory: {input_dir}")
        print(f"Output will be saved in: {output_dir}")

        python_files, json_files = get_files(input_dir)
        dependency_tree = generate_dependency_tree(input_dir, python_files)

        print("\nFull dependency tree:")
        for file, deps in dependency_tree.items():
            print(f"{file}: {deps}")

        print("\n# Python Project Structure")
        print("\n## File Dependencies\n")

        all_dependencies = set()
        update_json_files = [
            'update_json.py',
            'update_json_category_manager.py',
            'update_json_file_handler.py',
            'update_json_processor.py',
            'update_json_rule.py',
            'update_json_rule_manager.py',
            'update_json_transaction.py',
            'update_json_transaction_manager.py',
            'update_json_transaction_processor.py'
        ]

        for root_file in ['main.py'] + update_json_files:
            if root_file in dependency_tree:
                file_dependencies = get_all_dependencies(dependency_tree, root_file)
                file_dependencies.add(root_file)
                all_dependencies.update(file_dependencies)

                print(f"\n### Dependencies for {root_file}:")
                for file in sorted(file_dependencies):
                    print(f"- {file}")
                    if file in dependency_tree:
                        for dep in sorted(dependency_tree[file]):
                            print(f"  - {dep}")
            else:
                print(f"\n### {root_file} not found in the dependency tree.")

        # Ensure all update_json files are included even if they're not in the dependency tree
        all_dependencies.update(update_json_files)

        if all_dependencies:
            write_markdown_and_pdf_output(input_dir, output_dir, output_file, all_dependencies, json_files)
        else:
            print("No files found. Including all Python and JSON files.")
            write_markdown_and_pdf_output(input_dir, output_dir, output_file, python_files, json_files)

        print("Script execution completed successfully.")
    except Exception as e:
        print(f"An error occurred during script execution: {str(e)}")
        print("Traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    main()
    print("Script has finished executing.")