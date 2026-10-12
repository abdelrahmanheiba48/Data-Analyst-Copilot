#RAG.py
import chromadb
from sentence_transformers import SentenceTransformer
import data

#__CHUNKING__
text, chunks = data.load_documentation()

#__embedding__
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
chunks_embedding = embedding_model.encode(chunks, show_progress_bar=True)

#__VECTORDB__
client = chromadb.EphemeralClient()
collection = client.create_collection(name="collection1")
collection.add(
    ids=[f"chunk_{i}" for i in range(len(chunks))],
    embeddings=[emb.tolist() for emb in chunks_embedding],
    documents=chunks
)

#__RETRIEVAL__
def retrieve(search_text, n_results):
    query_embedding = embedding_model.encode(search_text).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    return results["documents"][0]