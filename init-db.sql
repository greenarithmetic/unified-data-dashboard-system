-- Create database for Superset
CREATE DATABASE superset;
CREATE USER superset WITH PASSWORD '${SUPERSET_DATABASE_PASSWORD:-your_secure_password_here_change_in_production}';
GRANT ALL PRIVILEGES ON DATABASE superset TO superset;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create schema for UDDS
\c udds

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_records_dataset_id ON records(dataset_id);
CREATE INDEX IF NOT EXISTS idx_records_created_at ON records(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_records_is_spam ON records(is_spam) WHERE is_spam = false;
CREATE INDEX IF NOT EXISTS idx_records_data_gin ON records USING gin(data);
CREATE INDEX IF NOT EXISTS idx_records_source_id ON records(source_id) WHERE source_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_records_record_hash ON records(record_hash) WHERE record_hash IS NOT NULL;

-- Create composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_records_dataset_date ON records(dataset_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_records_dataset_spam ON records(dataset_id, is_spam, created_at DESC);

-- Create text search index
CREATE INDEX IF NOT EXISTS idx_records_text_search ON records USING gin(to_tsvector('russian', data->>'текст'));

-- Create function for full-text search
CREATE OR REPLACE FUNCTION search_records(
    p_dataset_id TEXT,
    p_query TEXT DEFAULT NULL,
    p_exclude_spam BOOLEAN DEFAULT TRUE,
    p_limit INTEGER DEFAULT 50,
    p_offset INTEGER DEFAULT 0
) RETURNS TABLE(
    id UUID,
    dataset_id TEXT,
    source TEXT,
    data JSONB,
    is_spam BOOLEAN,
    created_at TIMESTAMP,
    rank FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        r.id,
        r.dataset_id,
        r.source,
        r.data,
        r.is_spam,
        r.created_at,
        ts_rank(to_tsvector('russian', r.data->>'текст'), plainto_tsquery('russian', p_query)) as rank
    FROM records r
    WHERE r.dataset_id = p_dataset_id
        AND (NOT p_exclude_spam OR NOT r.is_spam)
        AND (p_query IS NULL OR to_tsvector('russian', r.data->>'текст') @@ plainto_tsquery('russian', p_query))
    ORDER BY 
        CASE WHEN p_query IS NOT NULL THEN rank ELSE 0 END DESC,
        r.created_at DESC
    LIMIT p_limit
    OFFSET p_offset;
END;
$$ LANGUAGE plpgsql;

-- Create function for statistics
CREATE OR REPLACE FUNCTION get_dataset_stats(
    p_dataset_id TEXT,
    p_exclude_spam BOOLEAN DEFAULT TRUE
) RETURNS TABLE(
    total_records BIGINT,
    total_spam BIGINT,
    by_theme JSONB,
    by_location JSONB,
    response_rate FLOAT,
    last_sync TIMESTAMP
) AS $$
DECLARE
    v_total BIGINT;
    v_spam BIGINT;
    v_themes JSONB;
    v_locations JSONB;
    v_response_rate FLOAT;
    v_last_sync TIMESTAMP;
BEGIN
    -- Total records
    SELECT COUNT(*) INTO v_total
    FROM records r
    WHERE r.dataset_id = p_dataset_id
        AND (NOT p_exclude_spam OR NOT r.is_spam);
    
    -- Spam count
    SELECT COUNT(*) INTO v_spam
    FROM records r
    WHERE r.dataset_id = p_dataset_id
        AND r.is_spam = true;
    
    -- Group by theme
    SELECT jsonb_object_agg(theme, count) INTO v_themes
    FROM (
        SELECT data->>'тема' as theme, COUNT(*) as count
        FROM records r
        WHERE r.dataset_id = p_dataset_id
            AND (NOT p_exclude_spam OR NOT r.is_spam)
            AND data->>'тема' IS NOT NULL
        GROUP BY data->>'тема'
        ORDER BY count DESC
        LIMIT 20
    ) themes;
    
    -- Group by location
    SELECT jsonb_object_agg(location, count) INTO v_locations
    FROM (
        SELECT data->>'адрес' as location, COUNT(*) as count
        FROM records r
        WHERE r.dataset_id = p_dataset_id
            AND (NOT p_exclude_spam OR NOT r.is_spam)
            AND data->>'адрес' IS NOT NULL
        GROUP BY data->>'адрес'
        ORDER BY count DESC
        LIMIT 20
    ) locations;
    
    -- Response rate
    SELECT 
        CASE 
            WHEN COUNT(*) > 0 THEN 
                COUNT(CASE WHEN (data->>'ответ')::BOOLEAN = true THEN 1 END)::FLOAT / COUNT(*)::FLOAT
            ELSE 0 
        END INTO v_response_rate
    FROM records r
    WHERE r.dataset_id = p_dataset_id
        AND (NOT p_exclude_spam OR NOT r.is_spam);
    
    -- Last sync
    SELECT MAX(created_at) INTO v_last_sync
    FROM records r
    WHERE r.dataset_id = p_dataset_id;
    
    RETURN QUERY SELECT 
        v_total,
        v_spam,
        COALESCE(v_themes, '{}'::jsonb),
        COALESCE(v_locations, '{}'::jsonb),
        v_response_rate,
        v_last_sync;
END;
$$ LANGUAGE plpgsql;

-- Create view for reporting
CREATE OR REPLACE VIEW vw_dataset_summary AS
SELECT 
    dataset_id,
    COUNT(*) as total_records,
    COUNT(CASE WHEN is_spam THEN 1 END) as spam_count,
    COUNT(CASE WHEN NOT is_spam THEN 1 END) as clean_count,
    MIN(created_at) as first_record,
    MAX(created_at) as last_record,
    COUNT(DISTINCT source) as sources_count
FROM records
GROUP BY dataset_id;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO udds;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO udds;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO udds;