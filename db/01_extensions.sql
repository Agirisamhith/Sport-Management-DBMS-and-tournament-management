-- =============================================================================
-- 01_extensions.sql
-- Enable required PostgreSQL extensions
-- =============================================================================

-- pg_trgm: provides trigram-based text search functions for fuzzy search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- btree_gist: provides GiST support for btree operators, required for
--             EXCLUDE constraints on overlapping time ranges
CREATE EXTENSION IF NOT EXISTS btree_gist;
