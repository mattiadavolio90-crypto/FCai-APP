# 🚨 FIX COMPLETO: RLS PERMESSI + DICITURE

**Data**: 30/12/2025  
**Problemi Risolti**:
1. ❌ Errore RLS: "new row violates row-level security policy"
2. ❌ Diciture categorizzate come "NO FOOD" invece di "📝 NOTE E DICITURE"

---

## ✅ STATO IMPLEMENTAZIONE

### FIX CODICE (COMPLETATO)
- ✅ **FIX 2**: [pages/admin.py](pages/admin.py#L510-L560) - Gestione errori migliorata per correzioni
- ✅ **FIX 3**: [app.py](app.py#L2557-L2567) - Esclusione diciture da grafici (già presente)
- ✅ **FIX 4**: [app.py](app.py#L2557-L2567) - Esclusione diciture da totali (già presente)

### FIX SQL (DA ESEGUIRE SU SUPABASE)
- ⏳ **FIX 1**: [migrations/003_fix_rls_permissions.sql](migrations/003_fix_rls_permissions.sql) - Policy permissiva
- ⏳ **FIX 5**: [migrations/004_fix_diciture_retroattive.sql](migrations/004_fix_diciture_retroattive.sql) - Correzione retroattiva

---

## 📋 ISTRUZIONI PASSO-PASSO

### STEP 1: Esegui SQL su Supabase

1. Vai su **Supabase Dashboard** → [https://supabase.com/dashboard](https://supabase.com/dashboard)
2. Seleziona il tuo progetto
3. Vai su **SQL Editor** (nel menu laterale)
4. Clicca **New Query**

#### A) Esegui FIX 1 - Permessi RLS

Copia e incolla questo SQL:

```sql
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
```

5. Clicca **RUN** (o `Ctrl+Enter`)
6. Verifica output: dovrebbe mostrare "Success"

#### B) Esegui FIX 5 - Correzione Retroattiva

Crea una nuova query e incolla:

```sql
-- Trova e correggi tutte le righe che dovrebbero essere diciture ma hanno categoria sbagliata
UPDATE public.fatture
SET categoria = '📝 NOTE E DICITURE'
WHERE 
    prezzo_unitario = 0 
    AND (
        descrizione ILIKE 'DDT N.%' 
        OR descrizione ILIKE 'DATI N.%'
        OR descrizione ILIKE 'NUMERO BOLL%'
        OR descrizione ILIKE 'BOLL N.%'
        OR descrizione ILIKE '%DOCUMENTO DI TRASPORTO%'
        OR descrizione ILIKE 'NOSTRO RIF%'
        OR descrizione ILIKE 'VOSTRO RIF%'
        OR descrizione ILIKE '%TRASPORTO GRATUITO%'
    )
    AND categoria != '📝 NOTE E DICITURE';
```

7. Clicca **RUN**
8. Output mostrerà quante righe sono state aggiornate (es: "UPDATE 5")

---

### STEP 2: Riavvia l'App

```bash
streamlit run app.py
```

O usa il file `Avvia App.bat`

---

### STEP 3: Testa la Correzione

1. Vai su **ADMIN PANEL** (nel menu laterale)
2. Seleziona **TAB 3: Review Righe Prezzo €0**
3. Seleziona descrizioni da marcare come diciture (es: "DDT N. 2914")
4. Clicca **🔴 Marca come Diciture**

**Risultato Atteso**:
- ✅ Nessun errore RLS
- ✅ Messaggio: "✅ X descrizioni marcate come diciture e aggiornate nel database!"
- ✅ Le righe scompaiono dalla lista (ora sono NOTE E DICITURE)

---

## 🔍 VERIFICA FINALE

### 1. Verifica Database

Esegui su Supabase SQL Editor:

```sql
-- Conta diciture totali
SELECT COUNT(*) AS diciture_totali
FROM public.fatture
WHERE categoria = '📝 NOTE E DICITURE';

-- Mostra esempi
SELECT descrizione, categoria, prezzo_unitario
FROM public.fatture
WHERE descrizione ILIKE 'DDT N.%'
LIMIT 10;
```

**Atteso**: Tutte le descrizioni DDT dovrebbero avere categoria "📝 NOTE E DICITURE"

### 2. Verifica Grafici

1. Torna alla **Dashboard principale**
2. Verifica che i grafici F&B e Spese **NON** includano:
   - DDT N. XXXX
   - Diciture varie
   - Righe con prezzo €0

### 3. Verifica Totali

1. Controlla il box blu in alto:
   ```
   📋 N. Righe Elaborate: XXX | 💰 Totale: € XXX.XX
   ```
2. Verifica che **NON** includa righe diciture (es: DDT dovrebbero essere escluse)

---

## 🎯 BENEFICI POST-FIX

✅ **Correzioni Funzionanti**: Nessun errore RLS durante salvataggio  
✅ **Categorie Corrette**: Diciture hanno categoria "📝 NOTE E DICITURE"  
✅ **Grafici Puliti**: Diciture escluse da analisi F&B e Spese  
✅ **Totali Accurati**: Calcoli escludono automaticamente diciture  
✅ **Auto-Classificazione**: Prossimi caricamenti riconoscono diciture automaticamente  
✅ **Gestione Errori**: Logging dettagliato per debug  

---

## 🐛 TROUBLESHOOTING

### Problema: SQL non si esegue
- Verifica di essere nel progetto corretto su Supabase
- Controlla di avere permessi admin sul database
- Verifica che le tabelle `fatture` e `classificazioni_manuali` esistano

### Problema: Ancora errore RLS dopo SQL
1. Fai logout dall'app
2. Ricarica la pagina
3. Fai login di nuovo
4. Riprova la correzione

### Problema: Diciture ancora visibili nei grafici
1. Forza il refresh cache: `Ctrl+Shift+R` sul browser
2. Oppure nell'app clicca su un filtro per ricaricare i dati
3. Verifica su Supabase che la categoria sia stata aggiornata

---

## 📝 CHANGELOG

**30/12/2025**:
- Creato FIX 1: Policy RLS permissiva
- Creato FIX 2: Gestione errori migliorata in admin.py
- Verificato FIX 3: Esclusione diciture da mostra_statistiche() (già presente)
- Verificato FIX 4: Esclusione diciture da totali (automatico da FIX 3)
- Creato FIX 5: Correzione retroattiva diciture nel database

---

## 🆘 SUPPORTO

Se i problemi persistono dopo aver applicato tutti i fix:

1. Controlla i log: `debug.log.1`
2. Verifica output SQL su Supabase
3. Controlla la console del browser (F12) per errori JavaScript
4. Riavvia completamente l'app

---

**Stato**: ✅ Codice implementato - ⏳ SQL da eseguire manualmente
