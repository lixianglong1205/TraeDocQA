import chromadb
from chromadb.config import Settings
from langchain_chroma import Chroma
from langchain_community.embeddings.dashscope import DashScopeEmbeddings
from langchain_core.documents import Document
import uuid


class VectorStoreManager:
    """
    Manages vector storage using Chroma and DashScope embeddings
    """

    def __init__(self):
        self.embeddings = DashScopeEmbeddings(
            model="ext-embedding-v1",
            api_key=get_api_key("DASHS_API_KEY")
            # dashscope_api_key=get_api_key("DASHS_API_KEY")
        )
        self.collection_name = "faq_collection_" + str(uuid.uuid4())
        self.vector_store = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings
        )
        self.doc_counter = 0

    def add_faqs(self, faqs: list):
        """
        Add FAQs to the vector store
        """
        documents = []
        metadatas = []

        for faq in faqs:
            # Create a document for each FAQ with question as content
            doc = Document(
                page_content=faq.get("问题", ""),
                metadata={
                    "question": faq.get("问题", ""),
                    "answer": faq.get("答案", ""),
                    "id": str(self.doc_counter)
                }
            )
            documents.append(doc)
            self.doc_counter += 1

        # Add documents to vector store
        if documents:
            self.vector_store.add_documents(documents)

    def similarity_search(self, query: str, top_k: int = 5) -> list:
        """
        Perform similarity search in the vector store
        """
        results = self.vector_store.similarity_search_with_relevance_scores(
            query,
            k=top_k
        )

        # Extract FAQ pairs from results
        faqs = []
        for doc, score in results:
            faq_pair = {
                "question": doc.metadata.get("question", ""),
                "answer": doc.metadata.get("answer", ""),
                "relevance_score": score
            }
            faqs.append(faq_pair)

        return faqs


if __name__ == "__main__":
    manager = VectorStoreManager()
    # Example usage would go here