-- Migration 008: Aggiungi campo verified a prodotti_master
-- Data: 27/01/2026
-- Scopo: Tracking prodotti già verificati dall'admin vs nuovi da controllare

-- Aggiungi colonna verified (default FALSE = da verificare)
ALTER TABLE public.prodotti_master 
ADD COLUMN IF NOT EXISTS verified BOOLEAN DEFAULT FALSE;

-- Crea indice per query performanti (filtrare per verified)
CREATE INDEX IF NOT EXISTS idx_prodotti_master_verified 
ON public.prodotti_master(verified);

-- Commenti per documentazione
COMMENT ON COLUMN public.prodotti_master.verified IS 'TRUE = Admin ha verificato la categoria è corretta, FALSE = Da controllare';

-- NOTA: Righe esistenti avranno verified = FALSE (da ricontrollare)
-- Le correzioni manuali future auto-settano verified = TRUE
