-- Migrazione: aggiunge colonne per reset password
-- Esegui questa query nella console di Supabase (SQL Editor) o tramite migration tool

ALTER TABLE public.users
  ADD COLUMN IF NOT EXISTS reset_code text;

ALTER TABLE public.users
  ADD COLUMN IF NOT EXISTS reset_expires timestamptz;

-- Opzionale: index su reset_code se usato frequentemente
CREATE INDEX IF NOT EXISTS users_reset_code_idx ON public.users (reset_code);
