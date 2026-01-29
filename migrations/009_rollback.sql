-- ============================================================
-- ROLLBACK MIGRAZIONE 009: P.IVA + Password Security
-- ============================================================
-- Data: 2026-01-29
-- Descrizione: Rimuove campi aggiunti dalla migrazione 009
-- ============================================================

BEGIN;

-- 1. Rimuovi indice
DROP INDEX IF EXISTS idx_users_partita_iva;

-- 2. Rimuovi constraint UNIQUE
ALTER TABLE users 
DROP CONSTRAINT IF EXISTS users_partita_iva_unique;

-- 3. Rimuovi campi
ALTER TABLE users 
DROP COLUMN IF EXISTS partita_iva,
DROP COLUMN IF EXISTS ragione_sociale,
DROP COLUMN IF EXISTS password_changed_at,
DROP COLUMN IF EXISTS login_attempts;

COMMIT;

-- ============================================================
-- VERIFICA ROLLBACK
-- ============================================================
-- Esegui questa query per verificare che i campi siano stati rimossi:
-- SELECT column_name FROM information_schema.columns 
-- WHERE table_name = 'users' 
-- AND column_name IN ('partita_iva', 'ragione_sociale', 'password_changed_at', 'login_attempts');
-- (Deve restituire 0 righe)
