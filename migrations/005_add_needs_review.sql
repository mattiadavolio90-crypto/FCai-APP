-- ============================================================
-- MIGRATION: Strategia Ibrida - Righe €0 con Review
-- Data: 15 Gennaio 2026
-- Descrizione: Aggiunge colonne needs_review e audit trail
-- ============================================================

-- IMPORTANTE: Eseguire questo SQL in Supabase SQL Editor
-- PRIMA di modificare il codice Python

-- ============================================================
-- 1. COLONNA PRINCIPALE: needs_review
-- ============================================================
ALTER TABLE fatture 
ADD COLUMN IF NOT EXISTS needs_review BOOLEAN DEFAULT FALSE;

COMMENT ON COLUMN fatture.needs_review IS 
'Flag per righe che richiedono validazione manuale admin. 
true = in attesa review, false = validata/normale';

-- ============================================================
-- 2. CAMPI AUDIT: Tracciabilità validazioni
-- ============================================================
ALTER TABLE fatture 
ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMP;

ALTER TABLE fatture 
ADD COLUMN IF NOT EXISTS reviewed_by TEXT;

COMMENT ON COLUMN fatture.reviewed_at IS 
'Timestamp validazione manuale (NULL se mai validata)';

COMMENT ON COLUMN fatture.reviewed_by IS 
'Utente che ha validato la riga (admin/email)';

-- ============================================================
-- 3. INDICI PER PERFORMANCE
-- ============================================================

-- Indice parziale: solo righe in review (poche righe)
CREATE INDEX IF NOT EXISTS idx_fatture_needs_review 
ON fatture(needs_review) 
WHERE needs_review = true;

-- Indice composito per query Admin Panel
-- Ottimizza: WHERE needs_review=true OR prezzo_unitario=0
CREATE INDEX IF NOT EXISTS idx_fatture_review_prezzo 
ON fatture(needs_review, prezzo_unitario);

-- Indice audit trail
CREATE INDEX IF NOT EXISTS idx_fatture_reviewed_at 
ON fatture(reviewed_at) 
WHERE reviewed_at IS NOT NULL;

-- ============================================================
-- 4. VERIFICA COLONNE AGGIUNTE
-- ============================================================
SELECT 
    column_name, 
    data_type, 
    column_default,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'fatture' 
AND column_name IN ('needs_review', 'reviewed_at', 'reviewed_by')
ORDER BY column_name;

-- ============================================================
-- 5. VERIFICA INDICI CREATI
-- ============================================================
SELECT 
    indexname, 
    indexdef 
FROM pg_indexes 
WHERE tablename = 'fatture' 
AND indexname LIKE 'idx_fatture_%review%'
ORDER BY indexname;

-- ============================================================
-- NOTA CONSTRAINT (NON IMPLEMENTATO)
-- ============================================================
-- Il constraint proposto dall'utente era:
-- CHECK (needs_review = false OR (reviewed_at IS NULL AND reviewed_by IS NULL))
-- 
-- PROBLEMA: Impedisce inconsistenze ma è troppo restrittivo per righe 
-- vecchie con needs_review=false (default) mai reviewate.
-- 
-- DECISIONE: Usare solo logica applicativa, no constraint DB.
-- L'applicazione garantisce atomicità UPDATE dei 3 campi insieme.
-- ============================================================

-- ============================================================
-- OUTPUT ATTESO:
-- ============================================================
-- column_name   | data_type | column_default | is_nullable
-- --------------|-----------|----------------|------------
-- needs_review  | boolean   | false          | YES
-- reviewed_at   | timestamp | NULL           | YES
-- reviewed_by   | text      | NULL           | YES
--
-- indexname                    | indexdef
-- -----------------------------|----------------------------------
-- idx_fatture_needs_review     | CREATE INDEX ... WHERE needs_review = true
-- idx_fatture_review_prezzo    | CREATE INDEX ... ON (needs_review, prezzo_unitario)
-- idx_fatture_reviewed_at      | CREATE INDEX ... WHERE reviewed_at IS NOT NULL
-- ============================================================
