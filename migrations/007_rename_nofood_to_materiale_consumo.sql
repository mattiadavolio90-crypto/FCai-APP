-- ============================================================
-- MIGRATION 007: Rinomina "NO FOOD" → "MATERIALE DI CONSUMO"
-- ============================================================
-- Data: 2026-01-26
-- Descrizione: Rinomina la categoria NO FOOD in MATERIALE DI CONSUMO
--              per maggiore chiarezza e evitare confusione con Spese Generali
--
-- NOTA: MATERIALE DI CONSUMO comprende:
--   - Pellicole, alluminio, carta forno
--   - Detersivi, igienizzanti, saponi
--   - Guanti, mascherine
--   - Posate, bicchieri, cannucce monouso
--   - Contenitori d'asporto, tappi
--   - Scottex, carta igienica, tovaglioli
--
-- MATERIALE DI CONSUMO è SEMPRE considerato F&B (parte della produzione)
-- NON è Spese Generali (che sono utenze, consulenze, manutenzione)
-- ============================================================

-- ============================================================
-- 1. AGGIORNA TABELLA FATTURE (principale)
-- ============================================================

-- Aggiorna tutte le righe fattura con la vecchia categoria
UPDATE fatture 
SET categoria = 'MATERIALE DI CONSUMO'
WHERE categoria = 'NO FOOD';

-- ============================================================
-- 2. AGGIORNA TABELLA PRODOTTI_MASTER (se esiste)
-- ============================================================

-- Esegui solo se la tabella esiste
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'prodotti_master') THEN
        UPDATE prodotti_master 
        SET categoria = 'MATERIALE DI CONSUMO'
        WHERE categoria = 'NO FOOD';
    END IF;
END $$;

-- ============================================================
-- 3. AGGIORNA TABELLA PRODOTTI_UTENTE (se esiste)
-- ============================================================

-- Esegui solo se la tabella esiste
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'prodotti_utente') THEN
        UPDATE prodotti_utente 
        SET categoria = 'MATERIALE DI CONSUMO'
        WHERE categoria = 'NO FOOD';
    END IF;
END $$;

-- ============================================================
-- 5. VERIFICA RISULTATI
-- ============================================================

-- Query di verifica (esegui separatamente per controllare)
-- SELECT COUNT(*) as righe_aggiornate FROM fatture WHERE categoria = 'MATERIALE DI CONSUMO';
-- SELECT COUNT(*) as vecchie_righe FROM fatture WHERE categoria = 'NO FOOD';

-- ============================================================
-- ROLLBACK (se necessario)
-- ============================================================
-- UPDATE categorie SET nome = 'NO FOOD' WHERE nome = 'MATERIALE DI CONSUMO';
-- UPDATE fatture SET categoria = 'NO FOOD' WHERE categoria = 'MATERIALE DI CONSUMO';
-- UPDATE prodotti_master SET categoria = 'NO FOOD' WHERE categoria = 'MATERIALE DI CONSUMO';
-- UPDATE prodotti_utente SET categoria = 'NO FOOD' WHERE categoria = 'MATERIALE DI CONSUMO';
