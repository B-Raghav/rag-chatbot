from flask import Flask, render_template, request, jsonify
import sys
import os
import time
import psycopg2
import numpy as np
import faiss
import pickle
from sentence_transformers import SentenceTransformer
import requests
import json

app = Flask(__name__)

# Initialize retrieval system
class SimpleRetriever:
    def __init__(self):
        print("Loading retrieval system...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.index = faiss.read_index('data/processed/faiss_index.bin')
        
        with open('data/processed/chunk_ids.pkl', 'rb') as f:
            self.chunk_ids = pickle.load(f)
        
        self.conn = psycopg2.connect(
            host="localhost",
            database="rag_chatbot_db"
        )
        print("System ready!")
    
    def search(self, query, top_k=3):
        query_embedding = self.model.encode([query]).astype('float32')
        faiss.normalize_L2(query_embedding)
        
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        cursor = self.conn.cursor()
        
        for idx, (distance, index_pos) in enumerate(zip(distances[0], indices[0])):
            chunk_id = self.chunk_ids[index_pos]
            
            cursor.execute("""
                SELECT dc.chunk_text, dc.document_id, d.title, d.authors, d.categories
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
                    'categories': row[4]
                })
        
        cursor.close()
        return results

# Initialize
retriever = None

def get_retriever():
    global retriever
    if retriever is None:
        retriever = SimpleRetriever()
    return retriever

def call_ollama(prompt):
    payload = {
        "model": "mistral:latest",
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload)
        if response.status_code == 200:
            return response.json()['response']
        else:
            return f"Error: Status {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        # Retrieve
        ret = get_retriever()
        results = ret.search(query, top_k=3)
        
        # Build context
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(
                f"[Paper {i}]\n"
                f"Title: {result['title']}\n"
                f"Content: {result['chunk_text']}\n"
            )
        context = "\n".join(context_parts)
        
        # Create prompt
        prompt = f"""You are a helpful research assistant. Answer based on these papers.

{context}

Question: {query}

Instructions:
- Answer based only on the provided papers
- Cite which papers you use
- Be concise and accurate

Answer:"""
        
        # Generate
        response_text = call_ollama(prompt)
        
        return jsonify({
            'query': query,
            'response': response_text,
            'sources': results,
            'retrieval_time': 0,
            'generation_time': 0,
            'total_time': 0
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True, port=5000)