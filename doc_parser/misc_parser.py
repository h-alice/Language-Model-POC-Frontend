"""Parser for PDF documents."""

# Standard library imports
import tempfile  # For creating temporary files and directories
from typing import List  # For type hints

# Third-party library imports
from langchain_community.document_loaders import UnstructuredExcelLoader  # For loading unstructured Excel documents
from langchain_community.document_loaders import Docx2txtLoader  # For loading text from Word documents
from pptx import Presentation  # For working with PowerPoint presentations
from io import BytesIO  # For working with in-memory binary data
from PyPDF2 import PdfReader # For working with PDF documents.

# Local imports
from .parserbase import DocumentParser

class PdfParser(DocumentParser):
    """Parser for Microsoft Word documents."""

    def __init__(self, document) -> None:
        """
        Initialize the PdfParser.

        Parameters:
            document: bytes
                Path or binary date of the PDF document.
        """
        super().__init__(document)

    def extract_raw_text(self) -> List[str]:
        """
        Extract raw text from PDF document.

        Returns:
            List[str]:
                A list of strings representing the extracted text from the document.
        """
        file_like = BytesIO(self.buffer)
        pdf_reader = PdfReader(file_like)
        all_pages = []
        # Get the total number of pages in the PDF
        num_pages = len(pdf_reader.pages)
        for i in range(num_pages):
            page = pdf_reader.pages[i]
            text = page.extract_text()
            all_pages.append(text)

        return all_pages