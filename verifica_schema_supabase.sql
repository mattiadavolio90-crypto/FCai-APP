-- ========================================
-- 🔍 VERIFICA SCHEMA SUPABASE - DEBUG BUG
-- ========================================
-- Esegui queste query su Supabase Dashboard → SQL Editor
-- per diagnosticare i problemi di constraint e hash

-- ========================================
-- 1️⃣ VERIFICA CONSTRAINT SU CAMPO PIANO
-- ========================================
-- Questa query mostra il constraint esatto sul campo piano
SELECT 
    constraint_name, 
    check_clause 
FROM information_schema.check_constraints 
WHERE table_name = 'users' 
AND constraint_name LIKE '%piano%';

-- ========================================
-- 2️⃣ VERIFICA DEFINIZIONE COLONNA PIANO
-- ========================================
-- Mostra tipo di dato, default e nullable
SELECT 
    column_name, 
    data_type, 
    column_default,
    is_nullable,
    character_maximum_length
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name = 'piano';

-- ========================================
-- 3️⃣ TUTTI I CONSTRAINT SULLA TABELLA USERS
-- ========================================
-- Mostra TUTTI i constraint (check, foreign key, etc.)
SELECT 
    tc.constraint_name, 
    tc.constraint_type,
    cc.check_clause,
    tc.table_name
FROM information_schema.table_constraints tc
LEFT JOIN information_schema.check_constraints cc 
    ON tc.constraint_name = cc.constraint_name
WHERE tc.table_name = 'users'
ORDER BY tc.constraint_type, tc.constraint_name;

-- ========================================
-- 4️⃣ VERIFICA TIPO COLONNA PASSWORD_HASH
-- ========================================
-- Importante: deve essere TEXT per contenere hash lunghi
SELECT 
    column_name, 
    data_type, 
    character_maximum_length,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name = 'password_hash';

-- ========================================
-- 5️⃣ VALORI ATTUALI NEL DATABASE
-- ========================================
-- Mostra i primi caratteri degli hash attuali
SELECT 
    id,
    email,
    piano,
    LEFT(password_hash, 50) AS hash_primi_50_char,
    LENGTH(password_hash) AS lunghezza_hash,
    (password_hash LIKE '$argon2%') AS hash_corretto,
    (SELECT COUNT(*) FROM regexp_matches(password_hash, '\$', 'g')) AS conta_dollari
FROM users
ORDER BY created_at DESC
LIMIT 10;

-- ========================================
-- 6️⃣ VALORI DISTINTI CAMPO PIANO
-- ========================================
-- Mostra quali valori di piano esistono nel database
SELECT 
    piano,
    COUNT(*) as conteggio
FROM users
GROUP BY piano
ORDER BY conteggio DESC;

-- ========================================
-- 🛠️ FIX TEMPORANEO - RIMUOVI CONSTRAINT
-- ========================================
-- ⚠️ USA SOLO SE IL CONSTRAINT BLOCCA LA CREAZIONE UTENTI
-- Questo rimuove temporaneamente il constraint sul campo piano

-- ALTER TABLE users DROP CONSTRAINT IF EXISTS users_piano_check;

-- Dopo aver rimosso il constraint, puoi ri-crearlo con valori corretti:
-- ALTER TABLE users ADD CONSTRAINT users_piano_check 
--     CHECK (piano IN ('base', 'premium', 'enterprise'));

-- ========================================
-- 🛠️ FIX COLONNA PASSWORD_HASH SE NECESSARIO
-- ========================================
-- Se la colonna password_hash non è di tipo TEXT, convertila:

-- ALTER TABLE users ALTER COLUMN password_hash TYPE TEXT;

-- ========================================
-- 🧹 PULIZIA - ELIMINA UTENTI DI TEST
-- ========================================
-- ⚠️ USA CON CAUTELA! Elimina utenti creati durante i test

-- DELETE FROM users WHERE email LIKE 'test%@%';
-- DELETE FROM users WHERE email LIKE 'debug%@%';

-- ========================================
-- 📊 RISULTATI ATTESI
-- ========================================
-- Query 1: Dovrebbe mostrare un constraint come "piano IN ('base', 'premium', 'enterprise')"
-- Query 2: data_type = 'text' o 'character varying'
-- Query 3: Almeno un constraint di tipo PRIMARY KEY e CHECK
-- Query 4: data_type = 'text', character_maximum_length = NULL (illimitato)
-- Query 5: hash_corretto = true, conta_dollari = 5
-- Query 6: Solo valori 'base', 'premium', 'enterprise' (lowercase)

-- ========================================
-- 🔴 SINTOMI DI PROBLEMI
-- ========================================
-- ❌ Query 1 mostra constraint con valori UPPERCASE ('BASE', 'PREMIUM')
-- ❌ Query 4 mostra character_maximum_length limitato (es: 100)
-- ❌ Query 5 mostra hash_corretto = false
-- ❌ Query 5 mostra conta_dollari diverso da 5
-- ❌ Query 5 mostra hash che iniziano con "argon2id" invece di "$argon2id$"
