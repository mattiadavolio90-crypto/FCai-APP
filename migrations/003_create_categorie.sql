-- ============================================================
-- TABELLA CATEGORIE DINAMICHE
-- ============================================================
-- Gestione categorie prodotti con icone emoji
-- Admin può creare nuove categorie, tutti possono leggerle

CREATE TABLE IF NOT EXISTS categorie (
    id BIGSERIAL PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE,
    icona TEXT DEFAULT '📦',
    ordinamento INTEGER DEFAULT 999,
    attiva BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indici per performance
CREATE INDEX IF NOT EXISTS idx_categorie_attiva ON categorie(attiva);
CREATE INDEX IF NOT EXISTS idx_categorie_ordinamento ON categorie(ordinamento);

-- RLS Policy: Tutti possono leggere, solo admin può scrivere
ALTER TABLE categorie ENABLE ROW LEVEL SECURITY;

-- Policy lettura (tutti)
DROP POLICY IF EXISTS "Lettura categorie per tutti" ON categorie;
CREATE POLICY "Lettura categorie per tutti"
    ON categorie
    FOR SELECT
    USING (attiva = TRUE);

-- Policy scrittura (solo admin - gestita via service_role_key)
DROP POLICY IF EXISTS "Scrittura categorie solo admin" ON categorie;
CREATE POLICY "Scrittura categorie solo admin"
    ON categorie
    FOR ALL
    USING (FALSE);  -- Nessuno tramite RLS, solo via service_role_key

-- ============================================================
-- POPOLAMENTO INIZIALE CON CATEGORIE ESISTENTI
-- ============================================================

INSERT INTO categorie (nome, icona, ordinamento, attiva) VALUES
    -- Food & Beverage (priorità alta)
    ('CARNE', '🍖', 10, TRUE),
    ('PESCE', '🐟', 20, TRUE),
    ('LATTICINI', '🧀', 30, TRUE),
    ('SALUMI', '🥓', 40, TRUE),
    ('UOVA', '🥚', 50, TRUE),
    ('VERDURE', '🥬', 60, TRUE),
    ('FRUTTA', '🍎', 70, TRUE),
    ('PANE', '🍞', 80, TRUE),
    ('SECCO', '🍝', 90, TRUE),
    ('SALSE', '🧂', 100, TRUE),
    ('OLIO', '🫒', 110, TRUE),
    ('SCATOLAME', '🥫', 120, TRUE),
    ('CONSERVE', '🫙', 130, TRUE),
    ('SURGELATI', '🧊', 140, TRUE),
    ('DOLCI', '🍰', 150, TRUE),
    ('GELATI', '🍦', 160, TRUE),
    
    -- Bevande
    ('ACQUA', '💧', 200, TRUE),
    ('BIBITE', '🥤', 210, TRUE),
    ('CAFFÈ', '☕', 220, TRUE),
    ('VINI', '🍷', 230, TRUE),
    ('BIRRE', '🍺', 240, TRUE),
    ('DISTILLATI', '🥃', 250, TRUE),
    ('AMARI', '🍸', 260, TRUE),
    
    -- Non Food
    ('NO FOOD', '📦', 900, TRUE),
    
    -- Spese Generali (priorità bassa)
    ('MANUTENZIONE E ATTREZZATURE', '🔧', 910, TRUE),
    ('SERVIZI E CONSULENZE', '🧾', 920, TRUE),
    ('UTENZE E LOCALI', '🏠', 930, TRUE),
    
    -- Speciali
    ('NOTE E DICITURE', '📝', 990, TRUE),
    ('Da Classificare', '❓', 999, TRUE)
ON CONFLICT (nome) DO NOTHING;

-- ============================================================
-- COMMENTI
-- ============================================================

COMMENT ON TABLE categorie IS 'Categorie prodotti con icone emoji - gestite dinamicamente';
COMMENT ON COLUMN categorie.nome IS 'Nome categoria (MAIUSCOLO, senza emoji)';
COMMENT ON COLUMN categorie.icona IS 'Emoji icona (singolo carattere o sequenza)';
COMMENT ON COLUMN categorie.ordinamento IS 'Ordinamento custom (default alfabetico se = 999)';
COMMENT ON COLUMN categorie.attiva IS 'Soft delete: FALSE nasconde categoria';
