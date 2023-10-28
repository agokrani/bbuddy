from embedchain.embedder.openai import OpenAIEmbedder
from embedchain.config import BaseEmbedderConfig
from embedchain.vectordb.chroma import ChromaDB

class VectorStoreClient:
    _instance = None

    def __new__(cls, model="text-embedding-ada-002", **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, **kwargs)
            cls._instance.initialize_db(model = model)
        return cls._instance

    def initialize_db(self, model="text-embedding-ada-002"):
        self.db = ChromaDB()
        embedder = OpenAIEmbedder(config=BaseEmbedderConfig(model=model))
        self.db._set_embedder(embedder=embedder)
        self.db._initialize()

    def get_db(self):
        return self.db

vClient = VectorStoreClient()