# test_Product_Spec.py

import json
import os
from datetime import datetime

def load_product_spec(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def generate_markdown(spec):
    markdown = f"# {spec['title']}\n\n"

    markdown += "## Prime Directives\n\n"
    for directive in spec['prime_directives']:
        markdown += f"- {directive}\n"
    markdown += "\n"

    markdown += "## Key Rules\n\n"
    for rule in spec['key_rules']:
        markdown += f"### {rule['title']}\n\n"
        markdown += f"{rule['content']}\n\n"

    return markdown

def save_final_report(content, output_dir):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Final_Report_{timestamp}.md"
    file_path = os.path.join(output_dir, filename)

    with open(file_path, 'w') as f:
        f.write(content)

    return file_path

def main():
    # Set up paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    spec_path = os.path.join(current_dir, 'Product_Spec.json')
    output_dir = os.path.join(current_dir, 'output')

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Load product spec
    spec = load_product_spec(spec_path)

    # Generate markdown content
    markdown_content = generate_markdown(spec)

    # Save final report
    report_path = save_final_report(markdown_content, output_dir)

    print(f"Final report generated and saved to: {report_path}")

if __name__ == "__main__":
    main()