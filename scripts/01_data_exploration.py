import pandas as pd
import json
from datetime import datetime

print("Loading ArXiv dataset...")

# Load the data (first 100k rows to explore)
data = []
with open('data/raw/arxiv-metadata-oai-snapshot.json', 'r') as f:
    for i, line in enumerate(f):
        if i >= 100000:  # Just load first 100k for exploration
            break
        data.append(json.loads(line))

df = pd.DataFrame(data)

print(f"\n📊 Dataset Overview:")
print(f"Total papers loaded: {len(df)}")
print(f"\nColumns: {df.columns.tolist()}")
print(f"\nFirst paper example:")
print(df.iloc[0])

# Check date range
df['update_date'] = pd.to_datetime(df['update_date'])
print(f"\nDate range: {df['update_date'].min()} to {df['update_date'].max()}")

# Check categories
print(f"\nSample categories: {df['categories'].head()}")
# Filter Computer Science papers from 2020-2024
cs_papers = df[
    (df['categories'].str.contains('cs.', case=False, na=False)) &
    (df['update_date'] >= '2020-01-01') &
    (df['update_date'] <= '2024-12-31')
]

print(f"\n🎯 Computer Science Papers (2020-2024): {len(cs_papers)}")
print(f"\nSample CS paper:")
print(cs_papers.iloc[0][['title', 'categories', 'update_date']])