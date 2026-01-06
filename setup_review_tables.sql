-- ============================================================
-- SETUP TABELLE PER REVIEW RIGHE €0 - SISTEMA CONFERMA
-- ============================================================
-- 
-- ISTRUZIONI:
-- 1. Vai su Supabase Dashboard → SQL Editor
-- 2. Copia-incolla questo SQL
-- 3. Clicca RUN
-- 4. Riavvia l'app Streamlit
--
-- ============================================================

-- Tabella per tracciare conferme admin
CREATE TABLE IF NOT EXISTS review_confirmed (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    descrizione TEXT NOT NULL,
    categoria_finale TEXT,
    is_correct BOOLEAN DEFAULT true,
    confirmed_by TEXT,
    confirmed_at TIMESTAMP DEFAULT NOW(),
    note TEXT
);

-- Indice per ricerca veloce
CREATE INDEX IF NOT EXISTS idx_review_confirmed_descrizione 
ON review_confirmed(descrizione);

-- Tabella per ignorati temporanei (opzionale)
CREATE TABLE IF NOT EXISTS review_ignored (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    row_id UUID NOT NULL,
    descrizione TEXT,
    ignored_by TEXT,
    ignored_at TIMESTAMP DEFAULT NOW(),
    ignored_until TIMESTAMP DEFAULT (NOW() + INTERVAL '30 days')
);

CREATE INDEX IF NOT EXISTS idx_review_ignored_row 
ON review_ignored(row_id);

-- ============================================================
-- RLS POLICIES (Row Level Security)
-- ============================================================

-- Abilita RLS
ALTER TABLE review_confirmed ENABLE ROW LEVEL SECURITY;
ALTER TABLE review_ignored ENABLE ROW LEVEL SECURITY;

-- Policy: permetti tutto agli utenti autenticati
CREATE POLICY "Allow all for authenticated users on review_confirmed"
ON review_confirmed
FOR ALL TO authenticated
USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for authenticated users on review_ignored"
ON review_ignored
FOR ALL TO authenticated
USING (true) WITH CHECK (true);

-- ============================================================
-- VERIFICA CREAZIONE
-- ============================================================

-- Query di test (esegui dopo per verificare)
-- SELECT * FROM review_confirmed LIMIT 5;
-- SELECT * FROM review_ignored LIMIT 5;
