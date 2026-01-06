-- ====================================================================
-- TABELLA MEMORIA GLOBALE PRODOTTI (prodotti_master)
-- ====================================================================
-- Problema: Ogni categorizzazione chiama OpenAI API → costi alti, lentezza
-- Soluzione: Memoria globale condivisa tra TUTTI i clienti
-- Data: 30/12/2025
-- ====================================================================

-- Crea tabella memoria globale prodotti
CREATE TABLE IF NOT EXISTS public.prodotti_master (
    id SERIAL PRIMARY KEY,
    descrizione TEXT UNIQUE NOT NULL,
    categoria TEXT NOT NULL,
    confidence TEXT DEFAULT 'media',
    volte_visto INTEGER DEFAULT 1,
    classificato_da TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    ultima_modifica TIMESTAMP DEFAULT NOW()
);

-- Indici per performance
CREATE INDEX IF NOT EXISTS idx_prodotti_master_descrizione ON public.prodotti_master(descrizione);
CREATE INDEX IF NOT EXISTS idx_prodotti_master_categoria ON public.prodotti_master(categoria);
CREATE INDEX IF NOT EXISTS idx_prodotti_master_volte_visto ON public.prodotti_master(volte_visto DESC);

-- Commenti colonne
COMMENT ON COLUMN public.prodotti_master.descrizione IS 'Descrizione prodotto normalizzata (UPPERCASE)';
COMMENT ON COLUMN public.prodotti_master.categoria IS 'Categoria assegnata (CARNE, PESCE, etc)';
COMMENT ON COLUMN public.prodotti_master.confidence IS 'Livello confidenza: alta, media, bassa';
COMMENT ON COLUMN public.prodotti_master.volte_visto IS 'Numero volte che questo prodotto è stato usato';
COMMENT ON COLUMN public.prodotti_master.classificato_da IS 'Origine: AI, keyword, admin';

-- Row Level Security
ALTER TABLE public.prodotti_master ENABLE ROW LEVEL SECURITY;

-- Policy: Tutti gli utenti autenticati possono leggere (condiviso)
CREATE POLICY "Allow read for all authenticated users"
ON public.prodotti_master
FOR SELECT
TO authenticated
USING (true);

-- Policy: Tutti gli utenti autenticati possono inserire/aggiornare
CREATE POLICY "Allow insert for authenticated users"
ON public.prodotti_master
FOR INSERT
TO authenticated
WITH CHECK (true);

CREATE POLICY "Allow update for authenticated users"
ON public.prodotti_master
FOR UPDATE
TO authenticated
USING (true)
WITH CHECK (true);

-- Grant permessi
GRANT SELECT, INSERT, UPDATE ON public.prodotti_master TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE prodotti_master_id_seq TO authenticated;

-- ====================================================================
-- ESEGUI QUESTO SQL SU SUPABASE DASHBOARD → SQL EDITOR
-- DOPO aver eseguito 003_fix_rls_permissions.sql
-- ====================================================================

-- Verifica tabella creata
SELECT 
    COUNT(*) as prodotti_totali,
    SUM(volte_visto) as utilizzi_totali,
    COUNT(DISTINCT categoria) as categorie_uniche
FROM public.prodotti_master;
