from abc import ABC, abstractmethod
from typing import List, Union, IO
from pathlib import Path
from langchain_core.documents.base import Document  # For type hinting
from .parserbase import DocumentParser



def create_paeser(path_like: Union[str, Path]) -> 'DocumentParser':

    if isinstance(path_like, str):
        path_like = Path(path_like)

    # Check file extension.
    if path_like.suffix in [".docx"]:  # TODO: Add '.doc'. It should be supported now, but I cannot guarantee.
        from .msoffice_parser import MsDocParser
        return MsDocParser(path_like)
    
    elif path_like.suffix in [".xlsx"]:
        from .msoffice_parser import MsExcelParser
        return MsExcelParser(path_like)
    
    elif path_like.suffix in [".pptx"]:
        from .msoffice_parser import MsPptParser
        return MsPptParser(path_like)
    
    elif path_like.suffix in [".pdf"]:
        from .misc_parser import PdfParser
        return PdfParser(path_like)
    
    elif path_like.suffix in [".odt"]: 
        from .opendocument_parser import OdtParser
        return OdtParser(path_like)
    else:
        raise ValueError(f"Unsupported file extension: {path_like.suffix}")