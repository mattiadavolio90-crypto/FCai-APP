-- ====================================================================
-- FIX 1: PERMESSI RLS PER CLASSIFICAZIONI_MANUALI
-- ====================================================================
-- Problema: Policy troppo restrittiva impedisce salvataggio correzioni
-- Soluzione: Policy permissiva che consente tutte le operazioni
-- Data: 30/12/2025
-- ====================================================================

-- Rimuovi policy esistente (troppo restrittiva)
DROP POLICY IF EXISTS "Allow all for authenticated" ON public.classificazioni_manuali;

-- Crea policy PERMISSIVA che funziona davvero
CREATE POLICY "Allow all operations for authenticated users"
ON public.classificazioni_manuali
FOR ALL
TO authenticated
USING (true)
WITH CHECK (true);

-- Grant esplicito per sicurezza
GRANT ALL ON public.classificazioni_manuali TO authenticated;
GRANT USAGE, SELECT ON SEQUENCE classificazioni_manuali_id_seq TO authenticated;

-- Verifica permessi tabella fatture (per UPDATE categoria)
GRANT UPDATE ON public.fatture TO authenticated;

-- ====================================================================
-- ESEGUI QUESTO SQL SU SUPABASE DASHBOARD → SQL EDITOR
-- ====================================================================
