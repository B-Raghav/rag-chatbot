import pandas as pd
import re
import psycopg2
from psycopg2.extras import execute_batch

print("Starting text preprocessing...")

# Load data
df = pd.read_pickle('data/processed/cs_papers_2020_2024.pkl')
print(f"Loaded {len(df)} papers")

def clean_text(text):
    """Clean abstract text"""
    if pd.isna(text):
        return ""
    
    # Remove LaTeX commands
    text = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^a-zA-Z0-9\s\.,!?;:\-]', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def chunk_text(text, chunk_size=512, overlap=50):
    """Split text into overlapping chunks"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i:i + chunk_size])
        if len(chunk.split()) > 20:  # Only keep chunks with at least 20 words
            chunks.append(chunk)
    
    return chunks

# Process papers
print("Cleaning abstracts...")
df['clean_abstract'] = df['abstract'].apply(clean_text)

# Create chunks
print("Creating chunks...")
all_chunks = []

for idx, row in df.iterrows():
    if idx % 10000 == 0:
        print(f"Processed {idx} papers...")
    
    text_chunks = chunk_text(row['clean_abstract'])  # Changed variable name
    
    for chunk_idx, chunk_content in enumerate(text_chunks):  # Changed variable name
        all_chunks.append({
            'document_id': row['id'],
            'chunk_text': chunk_content,
            'chunk_index': chunk_idx,
            'token_count': len(chunk_content.split())
        })
print(f"\nTotal chunks created: {len(all_chunks)}")

# Save to database
print("Inserting chunks into database...")
conn = psycopg2.connect(
    host="localhost",
    database="rag_chatbot_db"
)
cursor = conn.cursor()

# Batch insert
insert_query = """
    INSERT INTO document_chunks (document_id, chunk_text, chunk_index, token_count)
    VALUES (%s, %s, %s, %s)
"""

batch_data = [(c['document_id'], c['chunk_text'], c['chunk_index'], c['token_count']) 
              for c in all_chunks]

execute_batch(cursor, insert_query, batch_data, page_size=1000)

conn.commit()

# Verify
cursor.execute("SELECT COUNT(*) FROM document_chunks;")
count = cursor.fetchone()[0]

cursor.close()
conn.close()

print(f"\nPreprocessing complete!")
print(f"Total chunks in database: {count}")

# Save chunks info for later use
chunks_df = pd.DataFrame(all_chunks)
chunks_df.to_pickle('data/processed/chunks_info.pkl')
print("Chunks info saved to data/processed/chunks_info.pkl")