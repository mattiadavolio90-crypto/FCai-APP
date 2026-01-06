-- ====================================================================
-- FIX 5: CORREZIONE RETROATTIVA DICITURE
-- ====================================================================
-- Problema: Righe già salvate hanno categoria "NO FOOD" invece di "📝 NOTE E DICITURE"
-- Soluzione: Aggiornare tutte le righe esistenti che dovrebbero essere diciture
-- Data: 30/12/2025
-- ====================================================================

-- Trova e correggi tutte le righe che dovrebbero essere diciture ma hanno categoria sbagliata
UPDATE public.fatture
SET categoria = '📝 NOTE E DICITURE'
WHERE 
    prezzo_unitario = 0 
    AND (
        descrizione ILIKE 'DDT N.%' 
        OR descrizione ILIKE 'DATI N.%'
        OR descrizione ILIKE 'NUMERO BOLL%'
        OR descrizione ILIKE 'BOLL N.%'
        OR descrizione ILIKE '%DOCUMENTO DI TRASPORTO%'
        OR descrizione ILIKE 'NOSTRO RIF%'
        OR descrizione ILIKE 'VOSTRO RIF%'
        OR descrizione ILIKE '%TRASPORTO GRATUITO%'
    )
    AND categoria != '📝 NOTE E DICITURE';

-- ====================================================================
-- ESEGUI QUESTO SQL SU SUPABASE DASHBOARD → SQL EDITOR
-- DOPO AVER ESEGUITO 003_fix_rls_permissions.sql
-- ====================================================================
