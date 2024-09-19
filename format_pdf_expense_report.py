# format_pdf_expense_report.py

import subprocess
import sys
import os

def convert_markdown_to_pdf(input_md_path, output_pdf_path):
    try:
        subprocess.run(["pandoc", input_md_path, "-o", output_pdf_path], check=True)
        print(f"PDF successfully created at {output_pdf_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting Markdown to PDF: {e}")
        raise
    except FileNotFoundError:
        print("Pandoc is not installed. Please install Pandoc to generate PDF reports.")
        print("For installation instructions, visit: https://pandoc.org/installing.html")
        raise

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python format_pdf_expense_report.py <input_markdown_path> <output_pdf_path>")
        sys.exit(1)

    input_md_path = sys.argv[1]
    output_pdf_path = sys.argv[2]

    if not os.path.exists(input_md_path):
        print(f"Error: Input markdown file '{input_md_path}' does not exist.")
        sys.exit(1)

    convert_markdown_to_pdf(input_md_path, output_pdf_path)