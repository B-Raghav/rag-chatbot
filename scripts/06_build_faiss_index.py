import numpy as np
import faiss
import pickle

print("Building FAISS index...")

# Load embeddings
print("Loading embeddings from disk...")
embeddings = np.load('data/processed/embeddings.npy')
print(f"Loaded embeddings shape: {embeddings.shape}")

# Load chunk IDs
with open('data/processed/chunk_ids.pkl', 'rb') as f:
    chunk_ids = pickle.load(f)
print(f"Loaded {len(chunk_ids)} chunk IDs")

# Normalize embeddings for cosine similarity
print("Normalizing embeddings...")
faiss.normalize_L2(embeddings)

# Build FAISS index
print("Building FAISS index...")
dimension = embeddings.shape[1]
index = faiss.IndexFlatIP(dimension)  # Inner Product = Cosine similarity after normalization
index.add(embeddings)

print(f"Index built with {index.ntotal} vectors")

# Save index
print("Saving FAISS index...")
faiss.write_index(index, 'data/processed/faiss_index.bin')

print("\nFAISS index creation complete!")
print(f"  Dimension: {dimension}")
print(f"  Total vectors: {index.ntotal}")
print(f"  Saved to: data/processed/faiss_index.bin")

# Test the index
print("\nTesting index with sample query...")
test_query = embeddings[0:1]  # Use first embedding as test
faiss.normalize_L2(test_query)
distances, indices = index.search(test_query, k=5)
print(f"  Top 5 similar chunks: {indices[0]}")
print(f"  Similarity scores: {distances[0]}")
print("\nIndex is ready for retrieval!")