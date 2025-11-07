import numpy as np
import faiss
import pickle
import psycopg2
from sentence_transformers import SentenceTransformer

class RetrievalSystem:
    def __init__(self):
        print("Initializing Retrieval System...")
        
        # Load embedding model
        print("Loading embedding model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Load FAISS index
        print("Loading FAISS index...")
        self.index = faiss.read_index('data/processed/faiss_index.bin')
        
        # Load chunk IDs
        print("Loading chunk IDs...")
        with open('data/processed/chunk_ids.pkl', 'rb') as f:
            self.chunk_ids = pickle.load(f)
        
        # Database connection
        self.conn = psycopg2.connect(
            host="localhost",
            database="rag_chatbot_db"
        )
        
        print(f"System ready! {self.index.ntotal} chunks indexed.")
    
    def search(self, query, top_k=5):
        """Search for relevant chunks"""
        # Generate query embedding
        query_embedding = self.model.encode([query])
        query_embedding = query_embedding.astype('float32')
        faiss.normalize_L2(query_embedding)
        
        # Search FAISS index
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Get chunk details from database
        results = []
        cursor = self.conn.cursor()
        
        for idx, (distance, index_pos) in enumerate(zip(distances[0], indices[0])):
            chunk_id = self.chunk_ids[index_pos]
            
            # Get chunk and document info
            cursor.execute("""
                SELECT 
                    dc.chunk_text,
                    dc.document_id,
                    d.title,
                    d.authors,
                    d.categories,
                    d.update_date
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.document_id
                WHERE dc.chunk_id = %s
            """, (chunk_id,))
            
            row = cursor.fetchone()
            if row:
                results.append({
                    'rank': idx + 1,
                    'similarity': float(distance),
                    'chunk_text': row[0],
                    'document_id': row[1],
                    'title': row[2],
                    'authors': row[3],
                    'categories': row[4],
                    'date': row[5]
                })
        
        cursor.close()
        return results
    
    def close(self):
        """Close database connection"""
        self.conn.close()


# Test the system
if __name__ == "__main__":
    print("\n" + "="*60)
    print("Testing Retrieval System")
    print("="*60 + "\n")
    
    # Initialize
    retriever = RetrievalSystem()
    
    # Test queries
    test_queries = [
        "deep learning for computer vision",
        "natural language processing transformers",
        "reinforcement learning robotics"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-" * 60)
        
        results = retriever.search(query, top_k=3)
        
        for result in results:
            print(f"\n{result['rank']}. Similarity: {result['similarity']:.4f}")
            print(f"   Title: {result['title'][:80]}...")
            print(f"   Categories: {result['categories']}")
            print(f"   Chunk: {result['chunk_text'][:150]}...")
    
    retriever.close()
    print("\n" + "="*60)
    print("Retrieval system test complete!")
    print("="*60)