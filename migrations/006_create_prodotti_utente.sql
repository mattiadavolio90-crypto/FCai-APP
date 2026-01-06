-- ========================================
-- MIGRAZIONE 006: TABELLA prodotti_utente (MEMORIA LOCALE)
-- ========================================
-- Descrizione: Crea tabella per memorizzare personalizzazioni prodotti per singolo utente
-- Data: 2026-01-02
-- Sistema: Memoria Ibrida (LOCALE + GLOBALE)
-- Priorità: LOCALE > GLOBALE > "Da Classificare"

-- ========================================
-- TABELLA prodotti_utente (MEMORIA LOCALE)
-- ========================================
CREATE TABLE IF NOT EXISTS prodotti_utente (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    descrizione TEXT NOT NULL,
    categoria TEXT NOT NULL,
    volte_visto INTEGER DEFAULT 1,
    classificato_da TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, descrizione)
);

-- ========================================
-- INDICI PER PERFORMANCE
-- ========================================
CREATE INDEX IF NOT EXISTS idx_prodotti_utente_user ON prodotti_utente(user_id);
CREATE INDEX IF NOT EXISTS idx_prodotti_utente_desc ON prodotti_utente(descrizione);
CREATE INDEX IF NOT EXISTS idx_prodotti_utente_user_desc ON prodotti_utente(user_id, descrizione);

-- ========================================
-- COMMENTI
-- ========================================
COMMENT ON TABLE prodotti_utente IS 'Memoria LOCALE: personalizzazioni categoria prodotto per singolo utente';
COMMENT ON COLUMN prodotti_utente.user_id IS 'ID utente proprietario della personalizzazione';
COMMENT ON COLUMN prodotti_utente.descrizione IS 'Descrizione prodotto normalizzata';
COMMENT ON COLUMN prodotti_utente.categoria IS 'Categoria personalizzata dall''utente';
COMMENT ON COLUMN prodotti_utente.volte_visto IS 'Numero volte visto nelle fatture utente';
COMMENT ON COLUMN prodotti_utente.classificato_da IS 'Chi ha classificato (User, AI, Admin)';

-- ========================================
-- ROW LEVEL SECURITY (RLS)
-- ========================================
ALTER TABLE prodotti_utente ENABLE ROW LEVEL SECURITY;

-- Policy: ogni utente vede solo i suoi prodotti
DROP POLICY IF EXISTS "Users see own products" ON prodotti_utente;
CREATE POLICY "Users see own products" ON prodotti_utente
    FOR ALL TO authenticated
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

-- ========================================
-- VERIFICA CREAZIONE
-- ========================================
-- SELECT * FROM prodotti_utente LIMIT 1;
-- SELECT table_name, column_name, data_type 
-- FROM information_schema.columns 
-- WHERE table_name = 'prodotti_utente';
