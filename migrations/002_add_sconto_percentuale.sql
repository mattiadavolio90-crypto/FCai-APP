-- ============================================================
-- MIGRATION 002: Aggiungi colonna Sconto Percentuale
-- ============================================================
-- Descrizione: Aggiunge la colonna "sconto_percentuale" per tracciare
--              gli sconti applicati sui prodotti (calcolato da PrezzoBase - PrezzoEffettivo)
-- Data: 2025-12-23
-- ============================================================

-- Aggiungi colonna Sconto%
ALTER TABLE fatture 
ADD COLUMN IF NOT EXISTS sconto_percentuale FLOAT DEFAULT 0;

-- Commento colonna
COMMENT ON COLUMN fatture.sconto_percentuale IS 'Sconto percentuale applicato: ((PrezzoBase - PrezzoEffettivo) / PrezzoBase) * 100';

-- Verifica colonna creata
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'fatture' 
AND column_name = 'sconto_percentuale';
