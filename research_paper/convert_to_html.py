import markdown
import os

BASE_DIR = '/Users/kixel/Developer/Projects/RedSea/research_paper'
MD_FILE = os.path.join(BASE_DIR, 'REDSEA_Research_Paper_Kunal_Saini_EXTENDED.md')
HTML_FILE = os.path.join(BASE_DIR, 'REDSEA_Research_Paper_FINAL_PRINTABLE.html')

def md_to_html():
    with open(MD_FILE, 'r') as f:
        text = f.read()
        
    # Replace the manual \newpage markers with HTML page breaks
    text = text.replace('\\newpage', '<div class="page-break"></div>')

    html_content = markdown.markdown(text, extensions=['fenced_code', 'tables'])

    css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Times+New+Roman&display=swap');
        
        body {
            font-family: 'Times New Roman', Times, serif;
            font-size: 12pt;
            line-height: 2.0; /* Double spacing for thesis */
            max-width: 8.5in;
            margin: 0 auto;
            padding: 1in;
            color: #000;
        }
        
        h1, h2, h3, h4 {
            font-weight: bold;
            line-height: 1.5;
            margin-top: 2em;
        }
        
        h1 { font-size: 16pt; text-align: center; }
        h2 { font-size: 14pt; }
        h3 { font-size: 12pt; }
        
        p {
            text-align: justify;
            margin-bottom: 1em;
        }
        
        hr {
            border: 0;
            border-top: 1px solid #ccc;
            margin: 2em 0;
            page-break-after: always; /* Force page break on horizontal rules */
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 2em 0;
            font-size: 10pt;
            line-height: 1.5;
        }
        
        th, td {
            border: 1px solid #000;
            padding: 8px;
            text-align: left;
        }
        
        pre {
            background-color: #f4f4f4;
            padding: 1em;
            overflow-x: auto;
            font-family: monospace;
            font-size: 9pt;
            line-height: 1.2;
            page-break-inside: avoid;
        }
        
        code {
            font-family: monospace;
            background-color: #f4f4f4;
            padding: 2px 4px;
        }
        
        .page-break {
            page-break-before: always;
        }
        
        /* Print media query for PDF generation */
        @media print {
            body {
                padding: 0;
                margin: 0;
            }
            @page {
                margin: 1.5in 1in 1in 1in;
            }
            hr { display: none; } /* Hide the horizontal rules when printing, use them just for page breaks */
        }
    </style>
    """

    full_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>REDSEA Research Paper</title>
        {css}
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    with open(HTML_FILE, 'w') as f:
        f.write(full_html)
        
    print(f"Successfully generated {HTML_FILE}")

if __name__ == '__main__':
    md_to_html()
