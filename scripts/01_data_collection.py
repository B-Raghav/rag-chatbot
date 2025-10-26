import pandas as pd
import json
from datetime import datetime
import os

print("🔄 Loading full ArXiv dataset (this takes 5-10 minutes)...")

# Load all data
data = []
count = 0

with open('data/raw/arxiv-metadata-oai-snapshot.json', 'r') as f:
    for line in f:
        paper = json.loads(line)
        
        # Filter CS papers from 2020-2024 on the fly
        if 'cs.' in paper['categories'].lower():
            update_date = pd.to_datetime(paper['update_date'])
            if update_date >= pd.Timestamp('2020-01-01') and update_date <= pd.Timestamp('2024-12-31'):
                data.append(paper)
        
        count += 1
        if count % 100000 == 0:
            print(f"Processed {count} papers... Found {len(data)} CS papers so far")

print(f"\n✅ Finished processing {count} total papers")
print(f"✅ Found {len(data)} Computer Science papers (2020-2024)")

# Create DataFrame
df = pd.DataFrame(data)

# Basic cleaning
df['update_date'] = pd.to_datetime(df['update_date'])
df['word_count'] = df['abstract'].str.split().str.len()

# Save filtered dataset
os.makedirs('data/processed', exist_ok=True)
df.to_csv('data/processed/cs_papers_2020_2024.csv', index=False)
df.to_pickle('data/processed/cs_papers_2020_2024.pkl')

print(f"\n📊 Dataset Statistics:")
print(f"Total CS papers: {len(df)}")
print(f"Date range: {df['update_date'].min()} to {df['update_date'].max()}")
print(f"Average abstract length: {df['word_count'].mean():.0f} words")
print(f"\nTop CS categories:")
print(df['categories'].value_counts().head(10))

print(f"\n💾 Saved to:")
print(f"  - data/processed/cs_papers_2020_2024.csv")
print(f"  - data/processed/cs_papers_2020_2024.pkl")