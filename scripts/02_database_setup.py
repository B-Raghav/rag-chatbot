import psycopg2
from psycopg2 import sql

print("🗄️ Setting up PostgreSQL database schema...")

# Connect to database
conn = psycopg2.connect(
    host="localhost",
    database="rag_chatbot_db"
)
cursor = conn.cursor()

# Drop existing tables if any (fresh start)
print("Dropping existing tables...")
cursor.execute("DROP TABLE IF EXISTS retrieval_logs CASCADE;")
cursor.execute("DROP TABLE IF EXISTS document_chunks CASCADE;")
cursor.execute("DROP TABLE IF EXISTS queries CASCADE;")
cursor.execute("DROP TABLE IF EXISTS documents CASCADE;")

# Create Documents table
print("Creating Documents table...")
cursor.execute("""
CREATE TABLE documents (
    document_id VARCHAR(50) PRIMARY KEY,
    arxiv_id VARCHAR(50) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    authors TEXT,
    categories VARCHAR(200),
    abstract TEXT,
    publication_date DATE,
    update_date DATE,
    word_count INTEGER,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# Create Queries table
print("Creating Queries table...")
cursor.execute("""
CREATE TABLE queries (
    query_id SERIAL PRIMARY KEY,
    user_query_text TEXT NOT NULL,
    query_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_text TEXT,
    response_quality_score FLOAT,
    retrieval_time_ms INTEGER,
    generation_time_ms INTEGER,
    total_latency_ms INTEGER
);
""")

# Create Document_Chunks table
print("Creating Document_Chunks table...")
cursor.execute("""
CREATE TABLE document_chunks (
    chunk_id SERIAL PRIMARY KEY,
    document_id VARCHAR(50) REFERENCES documents(document_id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    token_count INTEGER,
    embedding_index INTEGER,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# Create Retrieval_Logs table
print("Creating Retrieval_Logs table...")
cursor.execute("""
CREATE TABLE retrieval_logs (
    log_id SERIAL PRIMARY KEY,
    query_id INTEGER REFERENCES queries(query_id) ON DELETE CASCADE,
    document_id VARCHAR(50) REFERENCES documents(document_id) ON DELETE CASCADE,
    chunk_id INTEGER REFERENCES document_chunks(chunk_id) ON DELETE CASCADE,
    similarity_score FLOAT,
    retrieval_rank INTEGER,
    was_used_in_response BOOLEAN DEFAULT FALSE,
    log_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

# Create indexes for faster queries
print("Creating indexes...")
cursor.execute("CREATE INDEX idx_documents_categories ON documents(categories);")
cursor.execute("CREATE INDEX idx_documents_date ON documents(update_date);")
cursor.execute("CREATE INDEX idx_queries_timestamp ON queries(query_timestamp);")
cursor.execute("CREATE INDEX idx_chunks_document ON document_chunks(document_id);")
cursor.execute("CREATE INDEX idx_retrieval_query ON retrieval_logs(query_id);")
cursor.execute("CREATE INDEX idx_retrieval_document ON retrieval_logs(document_id);")

# Commit changes
conn.commit()
cursor.close()
conn.close()

print("\n✅ Database schema created successfully!")
print("\nTables created:")
print("  1. documents - Paper metadata")
print("  2. queries - User queries and responses")
print("  3. document_chunks - Text chunks for RAG")
print("  4. retrieval_logs - Query-document matches")