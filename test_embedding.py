import os
from dotenv import load_dotenv
from langchain_community.embeddings.dashscope import DashScopeEmbeddings  # Correct import

load_dotenv()

embeddings = DashScopeEmbeddings(
    model="text-embedding-v1",
    dashscope_api_key=os.getenv("DASHS_API_KEY")  # Use os.getenv directly
)

# Test the embeddings
query = "你好"
query_embedding = embeddings.embed_query(query)
print(f"Embedding for '{query}': {query_embedding[:5]}...")  # Print first 5 dimensions