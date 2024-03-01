"""Base class for document parsers."""

from abc import ABC, abstractmethod
from typing import List, Union, IO
from pathlib import Path
from langchain_core.documents.base import Document  # For type hinting
from langchain.text_splitter import RecursiveCharacterTextSplitter  # Text splitting utility

class DocumentParser:
    """
    Base class for document parsers.

    Attributes:
        buffer: bytes
            The raw content of the document.
    """

    def __init__(self, document: Union[str, Path, IO[bytes]]) -> None:
        """
        Initialize the DocumentParser.

        Parameters:
            document: Union[str, Path, IO[bytes]]
                Path to the document file or file-like object containing the document content.
        """
        # Type checking.
        if isinstance(document, str):
            document = Path(document)
            reader = document.open("rb")
        elif isinstance(document, Path):
            reader = document.open("rb")
        elif isinstance(document, IO):
            reader = document
        else:
            raise TypeError(f"Unsupported type: {type(document)}")

        # Load document into buffer.
        self.buffer = reader.read()

    def parse(self, chunk_size: int, chunk_overlap: int) -> List[Document]:
        """
        Parse the document into chunks.

        Parameters:
            chunk_size: int
                The size of each chunk.
            chunk_overlap: int
                The overlap between adjacent chunks.

        Returns:
            List[Document]:
                A list of Document objects representing the parsed chunks.
        """
        extracted_text_list = self.extract_raw_text()
        extracted_text = "\n".join(extracted_text_list)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        all_splits = text_splitter.create_documents([extracted_text])
        return all_splits

    @abstractmethod
    def extract_raw_text(self) -> List[str]:
        """
        Extract raw text from the document.

        Returns:
            List[str]:
                A list of strings representing the extracted text from the document.
        """
        pass
