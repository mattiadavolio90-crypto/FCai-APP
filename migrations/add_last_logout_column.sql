-- Aggiunge colonna last_logout per tracciare quando l'utente fa logout
-- Questo permette di invalidare sessioni anche se Streamlit Cloud mantiene session_state

ALTER TABLE users 
ADD COLUMN IF NOT EXISTS last_logout TIMESTAMP WITH TIME ZONE;

-- Crea indice per performance
CREATE INDEX IF NOT EXISTS idx_users_last_logout ON users(last_logout);

-- Commento
COMMENT ON COLUMN users.last_logout IS 'Timestamp ultimo logout - usato per invalidare sessioni persistenti';
