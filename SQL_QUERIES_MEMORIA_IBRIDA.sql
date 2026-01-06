-- ============================================================
-- SQL QUERIES UTILI - SISTEMA MEMORIA IBRIDA
-- ============================================================
-- Da eseguire su Supabase SQL Editor per verifiche e debug
-- ============================================================

-- ============================================================
-- SEZIONE 1: VERIFICHE STRUTTURA
-- ============================================================

-- 1.1 Verifica tabella prodotti_utente creata
SELECT 
    table_name, 
    table_type
FROM information_schema.tables 
WHERE table_name = 'prodotti_utente';


-- 1.2 Verifica colonne prodotti_utente
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'prodotti_utente'
ORDER BY ordinal_position;


-- 1.3 Verifica indici
SELECT 
    indexname, 
    indexdef
FROM pg_indexes 
WHERE tablename = 'prodotti_utente';


-- 1.4 Verifica constraint UNIQUE
SELECT 
    conname AS constraint_name,
    contype AS constraint_type,
    pg_get_constraintdef(oid) AS definition
FROM pg_constraint
WHERE conrelid = 'prodotti_utente'::regclass;


-- 1.5 Verifica RLS attiva
SELECT 
    schemaname,
    tablename, 
    rowsecurity AS rls_enabled
FROM pg_tables 
WHERE tablename = 'prodotti_utente';


-- 1.6 Verifica policy RLS
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies 
WHERE tablename = 'prodotti_utente';


-- ============================================================
-- SEZIONE 2: STATISTICHE E MONITORING
-- ============================================================

-- 2.1 Conteggio prodotti per tabella
SELECT 
    'prodotti_master (GLOBALE)' AS tabella,
    COUNT(*) AS totale_prodotti
FROM prodotti_master

UNION ALL

SELECT 
    'prodotti_utente (LOCALE)' AS tabella,
    COUNT(*) AS totale_prodotti
FROM prodotti_utente;


-- 2.2 Top 20 prodotti più visti (GLOBALE)
SELECT 
    descrizione,
    categoria,
    volte_visto,
    classificato_da,
    created_at::date AS data_creazione
FROM prodotti_master
ORDER BY volte_visto DESC
LIMIT 20;


-- 2.3 Distribuzione prodotti per categoria (GLOBALE)
SELECT 
    categoria,
    COUNT(*) AS num_prodotti,
    SUM(volte_visto) AS totale_utilizzi,
    ROUND(AVG(volte_visto), 2) AS media_utilizzi
FROM prodotti_master
GROUP BY categoria
ORDER BY totale_utilizzi DESC;


-- 2.4 Prodotti localizzati per utente
SELECT 
    u.email,
    u.nome_ristorante,
    COUNT(pu.id) AS num_personalizzazioni,
    SUM(pu.volte_visto) AS totale_utilizzi
FROM prodotti_utente pu
LEFT JOIN users u ON pu.user_id = u.id
GROUP BY u.email, u.nome_ristorante
ORDER BY num_personalizzazioni DESC;


-- 2.5 Dettaglio personalizzazioni di un utente specifico
-- SOSTITUISCI 'EMAIL_UTENTE' con email reale
SELECT 
    pu.descrizione,
    pu.categoria AS categoria_locale,
    pm.categoria AS categoria_globale,
    pu.volte_visto,
    pu.created_at::date AS data_personalizzazione
FROM prodotti_utente pu
LEFT JOIN users u ON pu.user_id = u.id
LEFT JOIN prodotti_master pm ON pu.descrizione = pm.descrizione
WHERE u.email = 'EMAIL_UTENTE'
ORDER BY pu.volte_visto DESC;


-- 2.6 Prodotti con override locale (diversi da globale)
SELECT 
    u.email,
    pu.descrizione,
    pu.categoria AS locale,
    pm.categoria AS globale,
    pu.volte_visto AS utilizzi_locale
FROM prodotti_utente pu
JOIN users u ON pu.user_id = u.id
LEFT JOIN prodotti_master pm ON pu.descrizione = pm.descrizione
WHERE pu.categoria != pm.categoria
ORDER BY pu.volte_visto DESC
LIMIT 50;


-- ============================================================
-- SEZIONE 3: ANALISI CLASSIFICAZIONI
-- ============================================================

-- 3.1 Prodotti classificati da AI (GLOBALE)
SELECT 
    descrizione,
    categoria,
    volte_visto,
    created_at::date AS data_creazione
FROM prodotti_master
WHERE classificato_da = 'AI'
ORDER BY volte_visto DESC
LIMIT 30;


-- 3.2 Prodotti corretti da Admin (GLOBALE)
SELECT 
    descrizione,
    categoria,
    volte_visto,
    classificato_da,
    updated_at::date AS data_correzione
FROM prodotti_master
WHERE classificato_da LIKE 'Admin%'
ORDER BY updated_at DESC
LIMIT 30;


-- 3.3 Prodotti corretti da utenti (LOCALE)
SELECT 
    u.email,
    pu.descrizione,
    pu.categoria,
    pu.classificato_da,
    pu.created_at::date AS data_correzione
FROM prodotti_utente pu
JOIN users u ON pu.user_id = u.id
WHERE pu.classificato_da LIKE 'User%'
ORDER BY pu.created_at DESC
LIMIT 30;


-- 3.4 Prodotti con discrepanze tra versioni
-- (stesso prodotto, categorie diverse tra globale e locale)
SELECT 
    u.email,
    pu.descrizione,
    pm.categoria AS globale_categoria,
    pu.categoria AS locale_categoria,
    pm.volte_visto AS globale_utilizzi,
    pu.volte_visto AS locale_utilizzi
FROM prodotti_utente pu
JOIN users u ON pu.user_id = u.id
JOIN prodotti_master pm ON pu.descrizione = pm.descrizione
WHERE pu.categoria != pm.categoria
ORDER BY pm.volte_visto DESC;


-- ============================================================
-- SEZIONE 4: RISPARMIO COSTI AI
-- ============================================================

-- 4.1 Calcolo risparmio chiamate AI
SELECT 
    COUNT(*) AS prodotti_unici,
    SUM(volte_visto) AS totale_utilizzi,
    SUM(volte_visto) - COUNT(*) AS chiamate_risparmiate,
    ROUND((SUM(volte_visto) - COUNT(*)) * 0.001, 2) AS risparmio_euro_stimato
FROM prodotti_master;


-- 4.2 Prodotti più riutilizzati (massimo risparmio)
SELECT 
    descrizione,
    categoria,
    volte_visto,
    volte_visto - 1 AS chiamate_risparmiate,
    ROUND((volte_visto - 1) * 0.001, 2) AS risparmio_euro_stimato
FROM prodotti_master
WHERE volte_visto > 1
ORDER BY volte_visto DESC
LIMIT 30;


-- ============================================================
-- SEZIONE 5: MANUTENZIONE E PULIZIA
-- ============================================================

-- 5.1 Trova prodotti duplicati (case-insensitive)
SELECT 
    LOWER(descrizione) AS descrizione_lower,
    COUNT(*) AS num_varianti,
    STRING_AGG(DISTINCT categoria, ', ') AS categorie
FROM prodotti_master
GROUP BY LOWER(descrizione)
HAVING COUNT(*) > 1
ORDER BY num_varianti DESC;


-- 5.2 Trova prodotti mai utilizzati
SELECT 
    descrizione,
    categoria,
    volte_visto,
    created_at::date AS data_creazione,
    AGE(NOW(), created_at) AS giorni_inutilizzato
FROM prodotti_master
WHERE volte_visto = 0
ORDER BY created_at DESC;


-- 5.3 Rimuovi prodotti vecchi mai utilizzati (>90 giorni)
-- ⚠️ ATTENZIONE: Questo comando CANCELLA dati!
-- Decommentare solo se sicuri
/*
DELETE FROM prodotti_master
WHERE volte_visto = 0 
  AND created_at < NOW() - INTERVAL '90 days';
*/


-- ============================================================
-- SEZIONE 6: TROUBLESHOOTING
-- ============================================================

-- 6.1 Test RLS - Simula accesso come utente specifico
-- SOSTITUISCI 'USER_UUID' con UUID reale
/*
SET LOCAL ROLE authenticated;
SET LOCAL request.jwt.claim.sub = 'USER_UUID';

SELECT * FROM prodotti_utente;

RESET ROLE;
*/


-- 6.2 Verifica foreign key su user_id
SELECT 
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY' 
  AND tc.table_name = 'prodotti_utente';


-- 6.3 Trova errori di integrità referenziale
-- (user_id che non esistono più in users)
SELECT 
    pu.user_id,
    COUNT(*) AS num_prodotti_orfani
FROM prodotti_utente pu
LEFT JOIN auth.users u ON pu.user_id = u.id
WHERE u.id IS NULL
GROUP BY pu.user_id;


-- ============================================================
-- SEZIONE 7: BACKUP E EXPORT
-- ============================================================

-- 7.1 Export prodotti_master per backup
COPY (
    SELECT * FROM prodotti_master
    ORDER BY created_at
) TO '/tmp/backup_prodotti_master.csv' 
WITH (FORMAT CSV, HEADER true, ENCODING 'UTF8');


-- 7.2 Export prodotti_utente per backup
COPY (
    SELECT 
        pu.*,
        u.email
    FROM prodotti_utente pu
    LEFT JOIN users u ON pu.user_id = u.id
    ORDER BY pu.created_at
) TO '/tmp/backup_prodotti_utente.csv' 
WITH (FORMAT CSV, HEADER true, ENCODING 'UTF8');


-- ============================================================
-- SEZIONE 8: QUERY AVANZATE
-- ============================================================

-- 8.1 Matrice copertura memoria per utente
SELECT 
    u.email,
    u.nome_ristorante,
    COUNT(DISTINCT f.descrizione) AS prodotti_totali_utente,
    COUNT(DISTINCT pu.descrizione) AS prodotti_personalizzati,
    COUNT(DISTINCT pm.descrizione) AS prodotti_da_memoria_globale,
    ROUND(
        COUNT(DISTINCT pu.descrizione)::NUMERIC / 
        NULLIF(COUNT(DISTINCT f.descrizione), 0) * 100, 
        2
    ) AS percentuale_personalizzazione
FROM users u
LEFT JOIN fatture f ON f.user_id = u.id
LEFT JOIN prodotti_utente pu ON pu.user_id = u.id AND pu.descrizione = f.descrizione
LEFT JOIN prodotti_master pm ON pm.descrizione = f.descrizione AND pu.id IS NULL
GROUP BY u.email, u.nome_ristorante
ORDER BY percentuale_personalizzazione DESC;


-- 8.2 Timeline evoluzione memoria (per mese)
SELECT 
    DATE_TRUNC('month', created_at) AS mese,
    COUNT(*) AS nuovi_prodotti_globali,
    SUM(COUNT(*)) OVER (ORDER BY DATE_TRUNC('month', created_at)) AS totale_cumulativo
FROM prodotti_master
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY mese;


-- 8.3 Analisi qualità classificazioni AI
-- (prodotti AI non corretti vs corretti)
SELECT 
    CASE 
        WHEN classificato_da = 'AI' THEN 'AI (non corretto)'
        WHEN classificato_da LIKE 'Admin%' THEN 'AI corretto da Admin'
        WHEN classificato_da LIKE 'User%' THEN 'AI corretto da User'
        ELSE 'Altro'
    END AS tipo_classificazione,
    COUNT(*) AS num_prodotti,
    ROUND(AVG(volte_visto), 2) AS media_utilizzi
FROM prodotti_master
GROUP BY tipo_classificazione
ORDER BY num_prodotti DESC;


-- ============================================================
-- FINE QUERY UTILI
-- ============================================================
-- Per supporto: mattiadavolio90@gmail.com
-- ============================================================
