-- ============================================================
-- SETUP TABELLA CLASSIFICAZIONI MANUALI
-- ============================================================
-- Da eseguire nel SQL Editor di Supabase
-- Questo script crea la tabella per memorizzare le correzioni
-- dell'admin che diventano regole permanenti
-- ============================================================

-- 1. Crea tabella per memorizzare correzioni admin (regole permanenti)
CREATE TABLE IF NOT EXISTS classificazioni_manuali (
    id SERIAL PRIMARY KEY,
    descrizione TEXT UNIQUE NOT NULL,
    categoria_corretta TEXT NOT NULL,
    is_dicitura BOOLEAN DEFAULT FALSE,
    validato_da TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. Index per performance (query veloci per descrizione)
CREATE INDEX IF NOT EXISTS idx_classif_descrizione 
ON classificazioni_manuali(descrizione);

-- 3. Commenti per documentazione
COMMENT ON TABLE classificazioni_manuali IS 'Memorizza correzioni manuali admin che diventano regole permanenti per classificazione automatica';
COMMENT ON COLUMN classificazioni_manuali.descrizione IS 'Testo esatto della descrizione da classificare';
COMMENT ON COLUMN classificazioni_manuali.categoria_corretta IS 'Categoria finale validata dall admin';
COMMENT ON COLUMN classificazioni_manuali.is_dicitura IS 'True se è una dicitura da escludere completamente';
COMMENT ON COLUMN classificazioni_manuali.validato_da IS 'Email admin che ha validato questa correzione';

-- 4. RLS (Row Level Security) - solo admin possono scrivere
ALTER TABLE classificazioni_manuali ENABLE ROW LEVEL SECURITY;

-- 5. Policy: Admin possono fare tutto
-- IMPORTANTE: Modifica l'email con quella del tuo admin!
CREATE POLICY "Admin can do everything on classificazioni_manuali"
ON classificazioni_manuali
FOR ALL
USING (
    -- Permetti a tutti di leggere (l'app ne ha bisogno)
    auth.role() = 'authenticated'
    OR
    -- Solo admin specifico può modificare
    auth.jwt() ->> 'email' = 'mattiadavolio90@gmail.com'
);

-- 6. Grant permessi
GRANT SELECT ON classificazioni_manuali TO authenticated;
GRANT INSERT, UPDATE, DELETE ON classificazioni_manuali TO authenticated;

-- ============================================================
-- TEST: Verifica che la tabella sia stata creata
-- ============================================================
-- Esegui questa query per testare:
-- SELECT * FROM classificazioni_manuali;
-- 
-- Dovrebbe restituire 0 righe (tabella vuota ma esistente)
-- ============================================================
