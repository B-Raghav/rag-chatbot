import pandas as pd
import psycopg2
from datetime import datetime

print("Loading data into PostgreSQL...")

# Load the processed data
print("Reading processed data...")
df = pd.read_pickle('data/processed/cs_papers_2020_2024.pkl')

# Sample or use all papers
USE_SAMPLE = False  # Set to False to use all 547k papers
if USE_SAMPLE:
    df = df.sample(n=50000, random_state=42)
    print(f"Using sample of {len(df)} papers")
else:
    print(f"Using all {len(df)} papers")

# Connect to database
conn = psycopg2.connect(
    host="localhost",
    database="rag_chatbot_db"
)
cursor = conn.cursor()

# Prepare data for insertion
print("Inserting documents into database...")
inserted = 0
errors = 0

for idx, row in df.iterrows():
    try:
        cursor.execute("""
            INSERT INTO documents (
                document_id, arxiv_id, title, authors, categories,
                abstract, publication_date, update_date, word_count
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (arxiv_id) DO NOTHING;
        """, (
            row['id'],
            row['id'],
            row['title'],
            row['authors'],
            row['categories'],
            row['abstract'],
            None,
            row['update_date'],
            row['word_count']
        ))
        inserted += 1
        
        if inserted % 10000 == 0:
            conn.commit()
            print(f"  Inserted {inserted} documents...")
            
    except Exception as e:
        errors += 1
        if errors < 5:
            print(f"  Error inserting {row['id']}: {e}")

# Final commit
conn.commit()

# Verify insertion
cursor.execute("SELECT COUNT(*) FROM documents;")
count = cursor.fetchone()[0]

cursor.close()
conn.close()

print(f"\nData loading complete!")
print(f"  Successfully inserted: {inserted} documents")
print(f"  Errors: {errors}")
print(f"  Total in database: {count}")