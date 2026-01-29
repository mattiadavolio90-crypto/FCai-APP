-- ============================================================
-- VERIFICA MIGRAZIONE 009: P.IVA + Password Security
-- ============================================================
-- Esegui questa query per verificare che la migrazione sia stata eseguita correttamente
-- ============================================================

-- 1. Verifica presenza colonne
SELECT 
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name IN ('partita_iva', 'ragione_sociale', 'password_changed_at', 'login_attempts')
ORDER BY column_name;

-- Expected output: 4 righe con questi valori:
-- | column_name          | data_type                   | is_nullable | column_default |
-- |----------------------|-----------------------------|-------------|----------------|
-- | login_attempts       | integer                     | YES         | 0              |
-- | partita_iva          | character varying           | YES         | NULL           |
-- | password_changed_at  | timestamp with time zone    | YES         | now()          |
-- | ragione_sociale      | text                        | YES         | NULL           |

-- 2. Verifica constraint UNIQUE su partita_iva
SELECT constraint_name, constraint_type 
FROM information_schema.table_constraints 
WHERE table_name = 'users' 
AND constraint_name = 'users_partita_iva_unique';

-- Expected output: 1 riga con constraint_type = 'UNIQUE'

-- 3. Verifica indice
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'users' 
AND indexname = 'idx_users_partita_iva';

-- Expected output: 1 riga con l'indice creato

-- 4. Conta utenti senza P.IVA (per monitoraggio grace period)
SELECT 
    COUNT(*) AS totale_utenti,
    COUNT(partita_iva) AS con_piva,
    COUNT(*) - COUNT(partita_iva) AS senza_piva
FROM users 
WHERE attivo = true;
