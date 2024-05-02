from pathlib import Path
from typing import List, NamedTuple, IO, Tuple
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents.base import Document
from webui_config import EmbeddingModelConfig

from doc_parser import create_paeser
MAX_EMBEDDING_BATCH_SIZE = 32 # Hard limit for embedding batch size.

class RagParameters(NamedTuple):
    chunk_size: int
    chunk_overlap: int
    top_k: int
    @classmethod
    def new_rag_parameter(cls, chunk_size, chunk_overlap, top_k=3):
        return cls(chunk_size=chunk_size,
                   chunk_overlap=chunk_overlap, 
                   top_k=top_k)

def topk_documents(query: str, embedding_config: EmbeddingModelConfig, rag_param: RagParameters, document_path_list:List[str], document_preprocessed=False) -> List[Tuple[Document, float]]:

    if embedding_config.provider.lower() != "huggingface": raise NotImplemented

    # Every elements in 'document_list' is a 'path' to pdf file.
    all_document = []  # Placeholder for all seprated document segments.

    if not document_preprocessed:
        # Load all document.
        for file_path in document_path_list:
            p = create_paeser(file_path)
            document_chunks = p.parse(chunk_size=rag_param.chunk_size, chunk_overlap=rag_param.chunk_overlap)
            all_document += document_chunks
    else:
        all_document = document_path_list # FIXME: Remove after PoC.

    # Retrive top-k document segments.
    embeddings = HuggingFaceInferenceAPIEmbeddings(
        api_key="",  # type: ignore Dummy API key.
        api_url=embedding_config.endpoint
    )

    # NOTE: Current issue: 'FAISS.from_documents' will STUPIDLY throw all segments of document to embedding model.
    #       So it can cause embedding model dies if batch size is too large.
    #       In the following strategy, first we divide all segment into 'batches' w.r.t. 'MAX_EMBEDDING_BATCH_SIZE'.
    #       Then we create an initial 'vector store', for each batch, we create a temporial 'vector store' and merge to the first one.

    # Divide vector_store w.r.t. the maxium size of batch size (for not exceeding the max batch size of embedding).
    cursor = min(MAX_EMBEDDING_BATCH_SIZE, len(all_document))
    db = FAISS.from_documents(all_document[0:cursor], embeddings) # Initial batch.

    while cursor < len(all_document):
        cursor_next = min(cursor + MAX_EMBEDDING_BATCH_SIZE, len(all_document)) # Calculate next cursoe position.
        _db_temp = FAISS.from_documents(all_document[cursor:cursor_next], embeddings) # Create temp vector store.
        db.merge_from(_db_temp) # Merge vector stores.
        cursor = cursor_next # Move cursor position.
    
    docs_score = db.similarity_search_with_score(query, k=rag_param.top_k)

    return docs_score

