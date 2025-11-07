# RAG Chatbot for Computer Science Research Papers

A Retrieval-Augmented Generation system that helps users access and understand computer science research papers from arXiv

## Team Members

- Abishek Udayakrishna Surya Narayanan - System Design, Testing, Deployment
- Varun Mandepudi - Database Design, Data Management, SQL Analytics
- Raghavendra Beri - Machine Learning, RAG Implementation

## Project Overview

This project builds an intelligent chatbot using RAG to answer questions about computer science research. The system combines PostgreSQL for structured metadata with FAISS for vector similarity search, and uses a local LLM (Mistral via Ollama) for response generation.

### Key Features

- 547,896 CS research papers (2020-2024)
- Hybrid database: PostgreSQL and FAISS
- Semantic search using sentence-transformers
- Local LLM inference using Ollama (Mistral model)
- Web interface built with Flask
- Comprehensive SQL analytics for evaluation

## Dataset

Source: arXiv Dataset on Kaggle (https://www.kaggle.com/datasets/Cornell-University/arxiv)

- Computer Science papers only
- 547,896 papers with abstracts and metadata

## Technology Stack

**Programming Language:** Python 3.12

**Databases:**

- PostgreSQL 15 for structured metadata
- FAISS for vector embeddings and similarity search

**Key Libraries:**

- pandas, NumPy - Data processing
- sentence-transformers - Embedding generation (all-MiniLM-L6-v2)
- psycopg2, SQLAlchemy - PostgreSQL integration
- FAISS - Vector similarity search
- Ollama - Local LLM inference (Mistral)
- Flask - Web interface

## Project Structure

```
rag_cb/
├── app.py                      # Flask web application
├── data/
│   ├── raw/                    # Original arXiv dataset
│   └── processed/              # Processed chunks and embeddings
├── scripts/
│   ├── 01_data_collection.py   # Download and filter papers
│   ├── 02_database_setup.py    # Create database schema
│   ├── 03_load_data_to_db.py   # Load papers into PostgreSQL
│   ├── 04_text_preprocessing.py # Clean and chunk text
│   ├── 05_generate_embeddings.py # Generate embeddings
│   ├── 06_build_faiss_index.py  # Build FAISS search index
│   ├── 07_retrieval_system.py   # Retrieval implementation
│   └── 08_rag_pipeline.py       # Complete RAG pipeline
├── sql_queries/
│   └── analytical_queries.sql   # 10 evaluation queries
├── templates/
│   └── index.html               # Web interface
├── requirements.txt
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.12 or higher
- PostgreSQL 15
- Ollama (for local LLM)
- 10GB free disk space

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/B-Raghav/rag-chatbot.git
cd rag-chatbot
```

**2. Create virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**3. Install Python dependencies**

```bash
pip install -r requirements.txt
```

**4. Install and setup PostgreSQL**

```bash
# Install PostgreSQL (if not already installed)
brew install postgresql@15  # On macOS
# For other OS, visit: https://www.postgresql.org/download/

# Start PostgreSQL
brew services start postgresql@15

# Create database
createdb rag_chatbot_db

# Create database schema
python scripts/02_database_setup.py
```

**5. Install and setup Ollama**

```bash
# Download Ollama from https://ollama.ai
# Or on macOS:
brew install ollama

# Pull the Mistral model
ollama pull mistral:latest

# Start Ollama server (in a separate terminal)
ollama serve
```

**6. Download and process data**

```bash
# Download arXiv dataset from Kaggle
# Place arxiv-metadata-oai-snapshot.json in data/raw/

# Run data collection and processing
python scripts/01_data_collection.py      # Filter CS papers (5-10 min)
python scripts/03_load_data_to_db.py      # Load into PostgreSQL (10-15 min)
python scripts/04_text_preprocessing.py   # Clean and chunk text (10-15 min)
python scripts/05_generate_embeddings.py  # Generate embeddings (15-20 min)
python scripts/06_build_faiss_index.py    # Build FAISS index (1 min)
```

## Running the Application

### Option 1: Web Interface

```bash
# Make sure Ollama is running in another terminal
ollama serve

# Start Flask app
python app.py

# Open browser to http://localhost:5000
```

### Option 2: Command Line

```bash
# Test the RAG pipeline directly
python scripts/08_rag_pipeline.py
```

### Option 3: Retrieval Only

```bash
# Test just the retrieval system
python scripts/07_retrieval_system.py
```

## Project Status

### Completed

- Data collection from arXiv (547,896 CS papers)
- PostgreSQL database with 4 interconnected tables
- Text preprocessing and chunking (547,574 chunks)
- Embedding generation (384-dimensional vectors)
- FAISS index for semantic search
- Retrieval system with PostgreSQL integration
- RAG pipeline with Ollama/Mistral
- Web interface with Flask
- 10 SQL analytical queries for evaluation

### System Performance

- Retrieval time: ~600-1300ms for top 3 papers
- Generation time: ~9000-20000ms (depends on query complexity)
- Total system latency: ~10-21 seconds per query
- Database: 547,896 papers fully indexed and searchable

## Database Schema

**documents** - Paper metadata

- document_id, arxiv_id, title, authors, categories
- abstract, publication_date, update_date, word_count

**queries** - User queries and responses

- query_id, user_query_text, query_timestamp
- response_text, response_quality_score
- retrieval_time_ms, generation_time_ms, total_latency_ms

**document_chunks** - Text chunks for retrieval

- chunk_id, document_id, chunk_text
- chunk_index, token_count, embedding_index

**retrieval_logs** - Query-document matching

- log_id, query_id, document_id, chunk_id
- similarity_score, retrieval_rank, was_used_in_response

## SQL Analytical Queries

Located in `sql_queries/analytical_queries.sql`:

1. Document frequency by CS category
2. Query response success rate over time
3. Retrieval latency tracking (median, p95)
4. Source reliability by category
5. Embedding similarity for different quality responses
6. User interaction frequency by topic
7. Knowledge coverage metrics
8. Top queries and common intents
9. Temporal query patterns
10. Retrieval rank effectiveness

## How It Works

1. **User asks a question** via web interface or command line
2. **Query is converted to embedding** using sentence-transformers
3. **FAISS searches** 547,574 chunks for most similar content
4. **Top 3-5 papers retrieved** from PostgreSQL with full metadata
5. **Context built** from retrieved paper chunks
6. **Mistral LLM generates answer** based only on retrieved papers
7. **Response returned with citations** and source attribution
8. **Everything logged** to database for analysis

## Evaluation Approach

We compare baseline LLM (without RAG) vs our RAG system:

**Metrics:**

- Answer accuracy on test questions
- Hallucination rate reduction
- Response relevance scores
- Retrieval precision@k (k=1,3,5)
- Average query latency
- Source attribution accuracy


## Future Improvements

- Add response caching for common queries
- Implement query refinement and follow-up questions
- Add paper recommendation system
- Create evaluation dashboard with real-time metrics
- Support for multiple LLM backends
- Export conversation history

## License

This project uses the arXiv dataset under open access licenses. All code is available for educational purposes.

## Acknowledgments

- arXiv for providing open access to research papers
- Anthropic Claude for development assistance
- Sentence-transformers and FAISS communities
- Ollama team for local LLM infrastructure
