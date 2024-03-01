"""Parser for Open Office documents."""

# Standard library imports
import tempfile  # For creating temporary files and directories
from typing import List  # For type hints
from io import BytesIO  # For working with in-memory binary data

# Third-party library imports
from langchain_community.document_loaders import UnstructuredExcelLoader  # For loading unstructured Excel documents
from langchain_community.document_loaders import Docx2txtLoader  # For loading text from Word documents
from odf import text, teletype
from odf.opendocument import load

# Local imports
from . import DocumentParser

class OdtParser(DocumentParser):
    """Parser for Microsoft Word documents."""

    def __init__(self, document) -> None:
        """
        Initialize the OdtParser.

        Parameters:
            document: bytes
                The binary data, or path for the ODT document.
        """
        super().__init__(document)

    def extract_raw_text(self) -> List[str]:
        """
        Extract raw text from ODT document.

        Returns:
            List[str]:
                A list of strings representing the extracted text from the document.
        """
        # Load the ODT file
        doc = load(BytesIO(self.buffer))

        # Initialize an empty string to store the extracted text
        extracted_text = []

        # Iterate through all paragraphs in the document
        for para in doc.getElementsByType(text.P):
            # Extract text from each paragraph and append it to the result
            extracted_text.append(teletype.extractText(para))

        return extracted_text
