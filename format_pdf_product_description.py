from markdown2 import markdown
from weasyprint import HTML, CSS

def convert_product_overview_to_pdf(input_md_path, output_pdf_path):
    # Load the markdown content
    with open(input_md_path, 'r') as file:
        md_content = file.read()

    # Convert markdown to HTML
    html_content = markdown(md_content, extras=["tables"])

    # Define CSS for a more colorful and engaging format
    css = CSS(string="""
        body { font-family: Arial, sans-serif; line-height: 1.6; }
        h1 { color: #4CAF50; font-size: 24pt; text-align: center; margin-bottom: 20px; }
        h2 { color: #2196F3; font-size: 20pt; margin-bottom: 15px; }
        h3 { color: #FF9800; font-size: 18pt; margin-bottom: 15px; }
        p { margin-bottom: 10px; font-size: 12pt; }
        ul { margin-left: 20px; font-size: 12pt; }
        li { margin-bottom: 10px; }
        .key-feature { background-color: #E8F5E9; padding: 10px; border-radius: 5px; margin-bottom: 15px; }
        .key-feature h3 { color: #388E3C; }
        .benefit { background-color: #FFF3E0; padding: 10px; border-radius: 5px; margin-bottom: 15px; }
        .benefit h3 { color: #F57C00; }
        .technical { background-color: #E3F2FD; padding: 10px; border-radius: 5px; margin-bottom: 15px; }
        .technical h3 { color: #1976D2; }
    """)

    # Convert HTML to PDF with the custom CSS
    HTML(string=html_content).write_pdf(output_pdf_path, stylesheets=[css])

    return f"PDF successfully created at {output_pdf_path}"

# Paths for the input markdown file and output PDF
input_md_path = '/Users/jeffsutherland/Frequency Research Foundation Inc. Dropbox/Frequency Lab/Python/Expenses/chatGPT4o scripts/transaction_processor/product_description.md'
output_pdf_path = '/Users/jeffsutherland/Frequency Research Foundation Inc. Dropbox/Frequency Lab/Python/Expenses/chatGPT4o scripts/transaction_processor/Output/Formatted_Product_Overview.pdf'

# Create the PDF
convert_product_overview_to_pdf(input_md_path, output_pdf_path)