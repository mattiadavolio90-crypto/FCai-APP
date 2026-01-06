-- ============================================================
-- CREAZIONE TABELLA prodotti_utente (MEMORIA LOCALE PERSONALIZZAZIONI)
-- ============================================================
-- Questa tabella memorizza le personalizzazioni per singolo cliente
-- Permette override delle categorie a livello utente
-- ============================================================

CREATE TABLE IF NOT EXISTS prodotti_utente (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    descrizione TEXT NOT NULL,
    categoria TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraint unico: un utente può avere una sola categoria per descrizione
    CONSTRAINT uq_user_descrizione UNIQUE (user_id, descrizione)
);

-- Abilita Row Level Security
ALTER TABLE prodotti_utente ENABLE ROW LEVEL SECURITY;

-- Policy: Gli utenti vedono solo le proprie personalizzazioni
CREATE POLICY "Users can view own products"
    ON prodotti_utente
    FOR SELECT
    USING (auth.uid() = user_id);

-- Policy: Gli utenti possono inserire le proprie personalizzazioni
CREATE POLICY "Users can insert own products"
    ON prodotti_utente
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Policy: Gli utenti possono aggiornare le proprie personalizzazioni
CREATE POLICY "Users can update own products"
    ON prodotti_utente
    FOR UPDATE
    USING (auth.uid() = user_id);

-- Policy: Gli utenti possono eliminare le proprie personalizzazioni
CREATE POLICY "Users can delete own products"
    ON prodotti_utente
    FOR DELETE
    USING (auth.uid() = user_id);

-- Indice per performance (lookup veloce per user + descrizione)
CREATE INDEX IF NOT EXISTS idx_prodotti_utente_user_desc 
ON prodotti_utente(user_id, descrizione);

-- Indice per ricerca per categoria
CREATE INDEX IF NOT EXISTS idx_prodotti_utente_categoria 
ON prodotti_utente(categoria);

-- ============================================================
-- VERIFICA CREAZIONE
-- ============================================================
-- SELECT * FROM prodotti_utente LIMIT 10;

-- ============================================================
-- NOTE
-- ============================================================
-- ✅ Tabella con RLS per isolamento multi-tenant
-- ✅ Personalizzazioni utente (override memoria globale)
-- ✅ Constraint unique previene duplicati
-- ✅ Indici per performance query
