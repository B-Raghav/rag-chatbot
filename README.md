# RAG Chatbot for Computer Science Research Papers

A Retrieval-Augmented Generation system that helps users access and understand computer science research papers from arXiv (2020-2024).

## Team Members

- Abishek Udayakrishna Surya Narayanan - System Design, Testing, Deployment
- Varun Mandepudi - Database Design, Data Management, SQL Analytics
- Raghavendra Beri - Machine Learning, RAG Implementation

## Project Overview

This project builds an intelligent chatbot using RAG to answer questions about computer science research. The system combines PostgreSQL for structured metadata with FAISS for vector similarity search.

### Key Features

- 547,896 CS research papers (2020-2024)
- Hybrid database: PostgreSQL and FAISS
- Semantic search using sentence-transformers
- Response generation using GPT-3.5
- SQL analytics for evaluation

## Dataset

Source: arXiv Dataset on Kaggle (https://www.kaggle.com/datasets/Cornell-University/arxiv)

- Computer Science papers only (2020-2024)
- 547,896 papers with abstracts and metadata
- Open access, no copyright restrictions

## Technology Stack

Programming Language: Python 3.12

Databases:

- PostgreSQL 15 for structured metadata
- FAISS for vector embeddings

Key Libraries:

- pandas, NumPy for data processing
- sentence-transformers for embeddings
- psycopg2, SQLAlchemy for database
- OpenAI API for response generation
- matplotlib, seaborn for visualization

## Project Structure

```
rag_cb/
├── data/
│   ├── raw/
│   └── processed/
├── scripts/
│   ├── 01_data_collection.py
│   ├── 02_database_setup.py
│   ├── 03_load_data_to_db.py
│   └── test_setup.py
├── sql_queries/
├── notebooks/
├── docs/
├── requirements.txt
└── README.md
```

## Setup Instructions

Prerequisites:

- Python 3.12 or higher
- PostgreSQL 15
- 10GB free disk space

Installation:

1. Clone the repository

```bash
git clone https://github.com/B-Raghav/rag-chatbot.git
cd rag-chatbot
```

2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL database

```bash
createdb rag_chatbot_db
python scripts/02_database_setup.py
```

5. Run data collection

```bash
python scripts/01_data_collection.py
python scripts/03_load_data_to_db.py
```

## Current Status

Completed:

- Environment setup with Python virtual environment
- Database schema design with 4 tables
- Data collection from arXiv (547,896 papers)
- Sample data loaded into PostgreSQL (50,000 papers)
- GitHub repository configured

In Progress:

- Text preprocessing pipeline
- Document chunking implementation
- Embedding generation

Next Steps:

- Week 3: RAG pipeline and SQL queries
- Week 4: Testing and evaluation
- Week 5: Documentation and presentation

## Timeline

- Week 1 : Data and Database Setup - Complete
- Week 2 : Preprocessing and Embeddings
- Week 3 : SQL Queries and RAG Pipeline
- Week 4 : Testing and Evaluation
- Week 5 : Documentation and Presentation

## Database Schema

documents table:

- Stores paper metadata including title, authors, categories, abstract, dates, and word count

queries table:

- Logs user queries, responses, quality scores, and latency metrics

document_chunks table:

- Contains text chunks with token counts and embedding references

retrieval_logs table:

- Records which documents were retrieved for each query with similarity scores

## Evaluation Plan

We will compare baseline LLM against our RAG system using:

- Answer accuracy on test questions
- Hallucination rate
- Response relevance
- Retrieval precision
- Query latency

## SQL Queries

We will implement 10 analytical queries:

1. Document frequency by category
2. Query success rate over time
3. Retrieval latency tracking
4. Source reliability analysis
5. Embedding similarity analysis
6. User interaction frequency
7. Knowledge coverage metrics
8. Top queries analysis
9. Temporal query patterns
10. Retrieval rank effectiveness

## License

This project uses the arXiv dataset under open access licenses.
