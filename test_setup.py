import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import psycopg2

print("✅ All packages working!")

# Test DB connection
try:
    conn = psycopg2.connect(
        host="localhost",
        database="rag_chatbot_db"
    )
    print("✅ Database connected!")
    conn.close()
except Exception as e:
    print(f"❌ Database error: {e}")
    