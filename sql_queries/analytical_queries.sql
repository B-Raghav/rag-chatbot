-- Query 1: Document frequency by CS category
SELECT 
    categories,
    COUNT(*) as total_papers,
    AVG(word_count) as avg_abstract_length,
    MIN(update_date) as earliest_paper,
    MAX(update_date) as latest_paper
FROM documents
GROUP BY categories
ORDER BY total_papers DESC
LIMIT 20;

-- Query 2: Query response success rate over time
SELECT 
    DATE(query_timestamp) as query_date,
    COUNT(*) as total_queries,
    AVG(response_quality_score) as avg_quality,
    AVG(total_latency_ms) as avg_latency_ms
FROM queries
GROUP BY query_date
ORDER BY query_date DESC;

-- Query 3: Retrieval latency tracking
SELECT 
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY retrieval_time_ms) as median_retrieval_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY retrieval_time_ms) as p95_retrieval_ms,
    AVG(retrieval_time_ms) as avg_retrieval_ms,
    MIN(retrieval_time_ms) as min_retrieval_ms,
    MAX(retrieval_time_ms) as max_retrieval_ms
FROM queries
WHERE retrieval_time_ms IS NOT NULL;

-- Query 4: Source reliability by category
SELECT 
    d.categories,
    COUNT(DISTINCT rl.query_id) as times_retrieved,
    AVG(rl.similarity_score) as avg_similarity,
    COUNT(DISTINCT d.document_id) as unique_papers
FROM documents d
JOIN retrieval_logs rl ON d.document_id = rl.document_id
GROUP BY d.categories
HAVING COUNT(DISTINCT rl.query_id) >= 1
ORDER BY times_retrieved DESC
LIMIT 20;

-- Query 5: Embedding similarity for responses
SELECT 
    CASE 
        WHEN response_quality_score >= 0.7 THEN 'High Quality'
        WHEN response_quality_score >= 0.4 THEN 'Medium Quality'
        ELSE 'Low Quality'
    END as quality_category,
    COUNT(*) as query_count,
    AVG(rl.similarity_score) as avg_similarity,
    MIN(rl.similarity_score) as min_similarity,
    MAX(rl.similarity_score) as max_similarity
FROM queries q
JOIN retrieval_logs rl ON q.query_id = rl.query_id
WHERE rl.retrieval_rank = 1
GROUP BY quality_category;

-- Query 6: User interaction frequency by topic
SELECT 
    d.categories,
    COUNT(DISTINCT rl.query_id) as query_count,
    COUNT(DISTINCT d.document_id) as unique_docs_retrieved,
    AVG(rl.similarity_score) as avg_similarity
FROM documents d
JOIN retrieval_logs rl ON d.document_id = rl.document_id
GROUP BY d.categories
ORDER BY query_count DESC
LIMIT 15;

-- Query 7: Knowledge coverage analysis
WITH indexed_docs AS (
    SELECT categories, COUNT(DISTINCT document_id) as total_indexed
    FROM documents
    GROUP BY categories
),
retrieved_docs AS (
    SELECT d.categories, COUNT(DISTINCT d.document_id) as total_retrieved
    FROM documents d
    JOIN retrieval_logs rl ON d.document_id = rl.document_id
    GROUP BY d.categories
)
SELECT 
    i.categories,
    i.total_indexed,
    COALESCE(r.total_retrieved, 0) as total_retrieved,
    ROUND(100.0 * COALESCE(r.total_retrieved, 0) / i.total_indexed, 2) as coverage_pct
FROM indexed_docs i
LEFT JOIN retrieved_docs r ON i.categories = r.categories
ORDER BY coverage_pct DESC
LIMIT 20;

-- Query 8: Top queries and common intents
SELECT 
    user_query_text,
    COUNT(*) as frequency,
    AVG(total_latency_ms) as avg_latency,
    AVG(retrieval_time_ms) as avg_retrieval_time,
    AVG(generation_time_ms) as avg_generation_time
FROM queries
GROUP BY user_query_text
ORDER BY frequency DESC
LIMIT 20;

-- Query 9: Temporal query patterns
SELECT 
    EXTRACT(HOUR FROM query_timestamp) as hour_of_day,
    COUNT(*) as query_count,
    AVG(total_latency_ms) as avg_latency
FROM queries
GROUP BY hour_of_day
ORDER BY hour_of_day;

-- Query 10: Retrieval rank effectiveness
SELECT 
    rl.retrieval_rank,
    COUNT(*) as times_at_rank,
    AVG(rl.similarity_score) as avg_similarity,
    COUNT(CASE WHEN rl.was_used_in_response THEN 1 END) as used_in_response
FROM retrieval_logs rl
GROUP BY rl.retrieval_rank
ORDER BY rl.retrieval_rank;