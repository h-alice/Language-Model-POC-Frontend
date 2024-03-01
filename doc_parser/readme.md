## Supported Document Types

- Microsoft Word (.docx)
- Microsoft Excel (.xlsx)
- Microsoft PowerPoint (.pptx)
- PDF (.pdf)
- OpenDocument Text (.odt)

## Usage

```python
from document_parser import create_parser

# Specify the path to the document
document_path = "path/to/your/document.docx"

# Create parser based on the document type
parser = create_parser(document_path)

# Parse the document
parsed_chunks = parser.parse(chunk_size=1000, chunk_overlap=100)

# Process the parsed chunks
for chunk in parsed_chunks:
    print(chunk)
    
```