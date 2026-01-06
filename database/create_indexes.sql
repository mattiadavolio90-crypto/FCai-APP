-- ============================================================
-- INDICI DATABASE PER OTTIMIZZAZIONE PERFORMANCE
-- ============================================================
-- Eseguire su Supabase SQL Editor per migliorare performance query
-- Impatto stimato: 80-90% riduzione tempi query
-- Sicuro: NON modifica dati, solo performance
-- ============================================================

-- INDICE 1: Filtro principale per user_id (isolamento multi-tenant)
-- Usato in: TUTTE le query principali
CREATE INDEX IF NOT EXISTS idx_fatture_user_id 
ON fatture(user_id);

-- INDICE 2: Filtro per categoria (review, dashboard, statistiche)
-- Usato in: TAB 3, TAB 4, analisi categorie
CREATE INDEX IF NOT EXISTS idx_fatture_categoria 
ON fatture(categoria);

-- INDICE 3: Ricerca per descrizione (memoria, matching)
-- Usato in: Memoria globale, review raggruppamenti
CREATE INDEX IF NOT EXISTS idx_fatture_descrizione 
ON fatture(descrizione);

-- INDICE 4: Filtro prezzi a zero (review righe €0)
-- Usato in: TAB 3 Review Righe a Zero
CREATE INDEX IF NOT EXISTS idx_fatture_prezzo_zero 
ON fatture(prezzo_unitario) 
WHERE prezzo_unitario = 0;

-- INDICE 5: Ricerca per file origine (gestione fatture)
-- Usato in: Eliminazione fatture, audit
CREATE INDEX IF NOT EXISTS idx_fatture_file_origine 
ON fatture(file_origine);

-- INDICE 6: Memoria globale lookup (categorizzazione AI)
-- Usato in: ottieni_categoria_prodotto(), memoria globale
CREATE INDEX IF NOT EXISTS idx_prodotti_master_descrizione 
ON prodotti_master(descrizione);

-- INDICE 7: Composito user + categoria per filtraggio veloce
-- Usato in: Dashboard analisi per categoria utente
CREATE INDEX IF NOT EXISTS idx_fatture_user_categoria 
ON fatture(user_id, categoria);

-- INDICE 8: Classificazioni manuali admin
-- Usato in: categorizza_con_memoria(), priorità admin
CREATE INDEX IF NOT EXISTS idx_classificazioni_manuali_descrizione 
ON classificazioni_manuali(descrizione);

-- INDICE 9: Memoria locale utente (personalizzazioni)
-- Usato in: categorizza_con_memoria(), ottieni_categoria_prodotto()
CREATE INDEX IF NOT EXISTS idx_prodotti_utente_user_desc 
ON prodotti_utente(user_id, descrizione);

-- INDICE 10: Ricerca per categoria in memoria utente
-- Usato in: Filtraggi e analisi personalizzazioni
CREATE INDEX IF NOT EXISTS idx_prodotti_utente_categoria 
ON prodotti_utente(categoria);

-- ============================================================
-- VERIFICA INDICI CREATI
-- ============================================================
-- Esegui questa query per verificare gli indici:
-- SELECT indexname, tablename FROM pg_indexes WHERE schemaname = 'public' ORDER BY tablename, indexname;

-- ============================================================
-- NOTE IMPORTANTI
-- ============================================================
-- ✅ Gli indici sono IDEMPOTENTI (IF NOT EXISTS)
-- ✅ Sicuri da eseguire anche se già presenti
-- ✅ Migliorano SOLO performance SELECT (read)
-- ✅ Overhead minimo su INSERT/UPDATE (write)
-- ⚠️ Occupano spazio disco (marginale per DB piccoli/medi)
