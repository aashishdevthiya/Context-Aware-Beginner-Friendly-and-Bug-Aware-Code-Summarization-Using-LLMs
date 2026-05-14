import os
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import TextLoader
from langchain.text_splitter import Language, RecursiveCharacterTextSplitter

class RAGContextRetriever:
    """Uses FAISS to find semantically related files instead of just AST."""

    def __init__(self, project_root: str, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.project_root = project_root
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
        self.vectorstore = None
        self._build_index()

    def _build_index(self):
        documents = []
        splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PYTHON, chunk_size=1000, chunk_overlap=100
        )
        for root, _, files in os.walk(self.project_root):
            for file in files:
                if file.endswith('.py'):
                    path = os.path.join(root, file)
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    chunks = splitter.split_text(content)
                    for chunk in chunks:
                        documents.append({"text": chunk, "source": path})
        # LangChain expects list of Document objects
        from langchain.schema import Document
        docs = [Document(page_content=d["text"], metadata={"source": d["source"]}) for d in documents]
        if docs:
            self.vectorstore = FAISS.from_documents(docs, self.embeddings)

    def get_related_context(self, query_code: str, k: int = 3) -> str:
        """Retrieve top‑k code chunks similar to query_code."""
        if not self.vectorstore:
            return ""
        results = self.vectorstore.similarity_search(query_code, k=k)
        context = ""
        for doc in results:
            context += f"# From {doc.metadata['source']}\n{doc.page_content}\n\n"
        return context