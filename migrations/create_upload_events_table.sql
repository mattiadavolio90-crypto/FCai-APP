-- ============================================================
-- TABELLA upload_events - Logging caricamenti fatture
-- ============================================================

CREATE TABLE IF NOT EXISTS upload_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id UUID NOT NULL,
    user_email TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_type TEXT NULL,
    status TEXT NOT NULL CHECK (status IN ('SAVED_OK', 'SAVED_PARTIAL', 'FAILED')),
    rows_parsed INT DEFAULT 0,
    rows_saved INT DEFAULT 0,
    rows_excluded INT DEFAULT 0,
    error_stage TEXT NULL,
    error_message TEXT NULL,
    details JSONB NULL,
    ack BOOLEAN DEFAULT FALSE,
    ack_at TIMESTAMPTZ NULL,
    ack_by TEXT NULL
);

-- ============================================================
-- INDICI per performance
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_upload_events_status_ack 
ON upload_events (ack, status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_upload_events_user_email 
ON upload_events (user_email);

CREATE INDEX IF NOT EXISTS idx_upload_events_file_name 
ON upload_events (file_name);

-- ============================================================
-- RLS (Row Level Security) - DISABILITATO
-- ============================================================

-- NOTA: RLS disabilitato per questa tabella
-- Sicurezza gestita lato applicazione:
-- - Solo admin (whitelist ADMIN_EMAILS) può accedere al panel
-- - Service key usato per INSERT/SELECT/UPDATE bypassa RLS

ALTER TABLE upload_events DISABLE ROW LEVEL SECURITY;

-- ============================================================
-- COMMENTI
-- ============================================================

COMMENT ON TABLE upload_events IS 'Log eventi caricamento fatture per supporto tecnico (RLS disabilitato, sicurezza gestita in app)';
COMMENT ON COLUMN upload_events.status IS 'SAVED_OK | SAVED_PARTIAL | FAILED (NO DUPLICATE)';
COMMENT ON COLUMN upload_events.error_stage IS 'PARSING | VISION | SUPABASE_INSERT | POSTCHECK';
COMMENT ON COLUMN upload_events.ack IS 'TRUE = problema verificato da admin';
COMMENT ON COLUMN upload_events.rows_excluded IS 'Righe escluse per diciture (comportamento normale, non errore)';
