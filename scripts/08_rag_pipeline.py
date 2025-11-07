import requests
import json
import time
import psycopg2
from datetime import datetime
import os
import sys

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Now import
exec(open(os.path.join(current_dir, '07_retrieval_system.py')).read())
class RAGChatbot:
    def __init__(self):
        print("Initializing RAG Chatbot...")
        self.retriever = RetrievalSystem()
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = "mistral:latest"
        
        # Database connection for logging
        self.conn = psycopg2.connect(
            host="localhost",
            database="rag_chatbot_db"
        )
        print("RAG Chatbot ready!")
    
    def generate_response(self, query, top_k=5):
        """Generate response using RAG"""
        start_time = time.time()
        
        # Step 1: Retrieve relevant chunks
        print(f"\nSearching for relevant papers...")
        retrieval_start = time.time()
        results = self.retriever.search(query, top_k=top_k)
        retrieval_time = int((time.time() - retrieval_start) * 1000)
        
        print(f"Found {len(results)} relevant papers in {retrieval_time}ms")
        
        # Step 2: Build context from retrieved chunks
        context = self._build_context(results)
        
        # Step 3: Create prompt
        prompt = self._create_prompt(query, context)
        
        # Step 4: Generate response with Ollama
        print("Generating response with Llama 3.2...")
        generation_start = time.time()
        response_text = self._call_ollama(prompt)
        generation_time = int((time.time() - generation_start) * 1000)
        
        total_time = int((time.time() - start_time) * 1000)
        
        print(f"Response generated in {generation_time}ms")
        print(f"Total time: {total_time}ms")
        
        # Step 5: Log to database
        self._log_query(query, response_text, results, 
                       retrieval_time, generation_time, total_time)
        
        return {
            'query': query,
            'response': response_text,
            'sources': results,
            'retrieval_time_ms': retrieval_time,
            'generation_time_ms': generation_time,
            'total_time_ms': total_time
        }
    
    def _build_context(self, results):
        """Build context from retrieved papers"""
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(
                f"[Paper {i}]\n"
                f"Title: {result['title']}\n"
                f"Categories: {result['categories']}\n"
                f"Content: {result['chunk_text']}\n"
            )
        return "\n".join(context_parts)
    
    def _create_prompt(self, query, context):
        """Create prompt for LLM"""
        return f"""You are a helpful research assistant. Answer the question based on the provided research papers.

Research Papers:
{context}

Question: {query}

Instructions:
- Answer based only on the provided papers
- Cite which papers you use (e.g., "According to Paper 1...")
- If the papers don't contain relevant information, say so
- Be concise and accurate

Answer:"""
    
    def _call_ollama(self, prompt):
        """Call Ollama API"""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload)
            if response.status_code == 200:
                return response.json()['response']
            else:
                return f"Error: Ollama returned status {response.status_code}"
        except Exception as e:
            return f"Error calling Ollama: {str(e)}"
    
    def _log_query(self, query, response, results, ret_time, gen_time, total_time):
        """Log query to database"""
        cursor = self.conn.cursor()
        
        # Insert query
        cursor.execute("""
            INSERT INTO queries (
                user_query_text, response_text, 
                retrieval_time_ms, generation_time_ms, total_latency_ms
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING query_id
        """, (query, response, ret_time, gen_time, total_time))
        
        query_id = cursor.fetchone()[0]
        
        # Log retrieved documents
        for rank, result in enumerate(results, 1):
            cursor.execute("""
                SELECT chunk_id FROM document_chunks 
                WHERE document_id = %s 
                LIMIT 1
            """, (result['document_id'],))
            
            chunk_row = cursor.fetchone()
            if chunk_row:
                chunk_id = chunk_row[0]
                
                cursor.execute("""
                    INSERT INTO retrieval_logs (
                        query_id, document_id, chunk_id,
                        similarity_score, retrieval_rank, was_used_in_response
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """, (query_id, result['document_id'], chunk_id,
                      result['similarity'], rank, True))
        
        self.conn.commit()
        cursor.close()
    
    def close(self):
        """Close connections"""
        self.retriever.close()
        self.conn.close()


# Test the chatbot
if __name__ == "__main__":
    print("\n" + "="*60)
    print("RAG Chatbot Test")
    print("="*60 + "\n")
    
    chatbot = RAGChatbot()
    
    # Test questions
    test_questions = [
        "What are the latest techniques in computer vision?",
        "How do transformers work in NLP?",
        "What are applications of reinforcement learning in robotics?"
    ]
    
    for question in test_questions:
        print("\n" + "="*60)
        print(f"QUESTION: {question}")
        print("="*60)
        
        result = chatbot.generate_response(question, top_k=3)
        
        print(f"\nANSWER:\n{result['response']}")
        print(f"\nSOURCES USED:")
        for source in result['sources']:
            print(f"  - {source['title'][:60]}... ({source['categories']})")
        
        print(f"\nPERFORMANCE:")
        print(f"  Retrieval: {result['retrieval_time_ms']}ms")
        print(f"  Generation: {result['generation_time_ms']}ms")
        print(f"  Total: {result['total_time_ms']}ms")
    
    chatbot.close()
    print("\n" + "="*60)
    print("Test Complete!")
    print("="*60)