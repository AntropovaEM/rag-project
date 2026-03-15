import chromadb
from sentence_transformers import SentenceTransformer
from functools import lru_cache


@lru_cache()
def get_model():
    return SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def create_index(chunks, source_name):
    client = chromadb.PersistentClient(path="./chroma_db")
    
    existing = client.list_collections()
    if any(c.name == "documents" for c in existing):
        client.delete_collection("documents")
    
    collection = client.create_collection("documents")
    model = get_model()
    
    collection.add(
        embeddings=model.encode(chunks).tolist(),
        documents=chunks,
        metadatas=[{"source": source_name} for _ in chunks],
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )
    
    return collection

def search(collection, query, top_k=4):
    model = get_model()
    query_embedding = model.encode([query]).tolist()
    
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=["documents", "metadatas"]
    )
    
    if results["documents"] and results["documents"][0]:
        return results["documents"][0], results["metadatas"][0]
    return [], []