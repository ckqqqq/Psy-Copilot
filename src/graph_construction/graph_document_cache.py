import pickle
from typing import Dict, Optional, List
import os
from langchain_community.graphs.graph_document import Node, Relationship, GraphDocument

class GraphDocumentCacheManager:
    def __init__(self, cache_file: str = "graph_document_cache_9_29.pkl"):
        self.cache_file = cache_file
        self.cache: Dict[str, List[GraphDocument]] = {}
        self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, "rb") as f:
                self.cache = pickle.load(f)

    def _save_cache(self):
        with open(self.cache_file, "wb") as f:
            pickle.dump(self.cache, f)

    def get_graph_document(self, document_id: str) -> Optional[GraphDocument]:
        return self.cache.get(document_id, [])

    def add_or_update_graph_document(self, document_id: str, graph_documents: List[GraphDocument]):
        self.cache[document_id] = graph_documents
        self._save_cache()

    def remove_graph_document(self, document_id: str):
        if document_id in self.cache:
            del self.cache[document_id]
            self._save_cache()