import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import psycopg2

print("Starting embedding generation...")

# Load the embedding model
print("Loading sentence-transformers model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print(f"Model loaded. Embedding dimension: {model.get_sentence_embedding_dimension()}")

# Load chunks from database
print("Loading chunks from database...")
conn = psycopg2.connect(
    host="localhost",
    database="rag_chatbot_db"
)
cursor = conn.cursor()

cursor.execute("""
    SELECT chunk_id, chunk_text 
    FROM document_chunks 
    ORDER BY chunk_id
""")
chunks = cursor.fetchall()
print(f"Loaded {len(chunks)} chunks")

# Generate embeddings in batches
print("Generating embeddings (this takes 15-20 minutes)...")
batch_size = 256
all_embeddings = []
chunk_ids = []

for i in range(0, len(chunks), batch_size):
    batch = chunks[i:i + batch_size]
    batch_texts = [chunk[1] for chunk in batch]
    batch_ids = [chunk[0] for chunk in batch]
    
    # Generate embeddings
    embeddings = model.encode(batch_texts, show_progress_bar=False)
    
    all_embeddings.extend(embeddings)
    chunk_ids.extend(batch_ids)
    
    if (i // batch_size + 1) % 10 == 0:
        print(f"  Processed {i + len(batch)} / {len(chunks)} chunks...")

# Convert to numpy array
embeddings_array = np.array(all_embeddings).astype('float32')
print(f"\nEmbeddings shape: {embeddings_array.shape}")

# Save embeddings
print("Saving embeddings...")
np.save('data/processed/embeddings.npy', embeddings_array)
with open('data/processed/chunk_ids.pkl', 'wb') as f:
    pickle.dump(chunk_ids, f)

# Update database with embedding indices
print("Updating database with embedding indices...")
for idx, chunk_id in enumerate(chunk_ids):
    cursor.execute("""
        UPDATE document_chunks 
        SET embedding_index = %s 
        WHERE chunk_id = %s
    """, (idx, chunk_id))
    
    if (idx + 1) % 10000 == 0:
        conn.commit()
        print(f"  Updated {idx + 1} / {len(chunk_ids)} chunks...")

conn.commit()
cursor.close()
conn.close()

print("\nEmbedding generation complete!")
print(f"  Total embeddings: {len(all_embeddings)}")
print(f"  Saved to: data/processed/embeddings.npy")
print(f"  Chunk IDs saved to: data/processed/chunk_ids.pkl")