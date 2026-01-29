-- ============================================================
-- MIGRAZIONE 009: P.IVA + Password Security
-- ============================================================
-- Data: 2026-01-29
-- Descrizione: Aggiunge campi per validazione P.IVA e tracking password
-- Rollback: migrations/009_rollback.sql
-- ============================================================

BEGIN;

-- 1. Aggiungi campo partita_iva
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS partita_iva VARCHAR(11) NULL;

-- 2. Aggiungi constraint UNIQUE (permette NULL multipli)
ALTER TABLE users 
ADD CONSTRAINT users_partita_iva_unique UNIQUE (partita_iva);

-- 3. Aggiungi campo ragione_sociale
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS ragione_sociale TEXT NULL;

-- 4. Aggiungi campo password_changed_at
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS password_changed_at TIMESTAMPTZ DEFAULT NOW();

-- 5. Aggiungi campo login_attempts
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS login_attempts INTEGER DEFAULT 0;

-- 6. Aggiungi campo reset_token (per email reset password)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS reset_token UUID NULL;

-- 7. Aggiungi campo reset_token_expires_at
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS reset_token_expires_at TIMESTAMPTZ NULL;

-- 8. Indice per performance ricerca P.IVA
CREATE INDEX IF NOT EXISTS idx_users_partita_iva 
ON users(partita_iva) 
WHERE partita_iva IS NOT NULL;

-- 9. Indice per ricerca token reset
CREATE INDEX IF NOT EXISTS idx_users_reset_token 
ON users(reset_token) 
WHERE reset_token IS NOT NULL;

-- 10. Aggiorna password_changed_at per utenti esistenti
UPDATE users 
SET password_changed_at = COALESCE(created_at, NOW()) 
WHERE password_changed_at IS NULL;

-- 11. Reset login_attempts per utenti esistenti
UPDATE users 
SET login_attempts = 0 
WHERE login_attempts IS NULL;

COMMIT;

-- ============================================================
-- VERIFICA POST-MIGRAZIONE
-- ============================================================
-- Esegui questa query per verificare:
-- SELECT column_name, data_type, is_nullable 
-- FROM information_schema.columns 
-- WHERE table_name = 'users' 
-- AND column_name IN ('partita_iva', 'ragione_sociale', 'password_changed_at', 'login_attempts', 'reset_token', 'reset_token_expires_at');
