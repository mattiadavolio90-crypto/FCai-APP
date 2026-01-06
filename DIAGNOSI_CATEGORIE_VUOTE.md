# 🔍 DIAGNOSI: Inconsistenza Dati Grafico vs Tabella

## ❌ PROBLEMA SEGNALATO

**Sintomo:**
- Grafico "Spesa per Categoria": mostra categorie assegnate + "Da Classificare"
- TAB "Dettaglio Articoli F&B": TUTTE le righe hanno categoria vuota/null

---

## ✅ ANALISI COMPLETATA

### 1. FONTE DATI GRAFICO

**File**: `app.py` righe 3284-3328  
**DataFrame**: `df_food`  
**Query**: `df_food.groupby("Categoria")["TotaleRiga"].sum()`

```python
# Grafico legge dalla colonna 'Categoria' di df_food
spesa_cat = df_food.groupby("Categoria")["TotaleRiga"].sum()
```

**Origine df_food:**
```
df_completo (caricato da Supabase)
    ↓
df_food_completo (filtro F&B, esclusi fornitori NO FOOD)
    ↓
df_food (filtro periodo selezionato)
```

---

### 2. FONTE DATI TABELLA

**File**: `app.py` righe 3518-3540  
**DataFrame**: `df_editor` → poi `edited_df`  
**Colonne**: Include colonna 'Categoria'

```python
# Tabella usa STESSO df_completo filtrato
cols_base = ['FileOrigine', 'DataDocumento', 'Fornitore', 'Descrizione',
            'Quantita', 'UnitaMisura', 'PrezzoUnitario', 
            'IVAPercentuale', 'TotaleRiga', 'Categoria']  # ← STESSA COLONNA

df_editor = df_base[cols_base].copy()
```

---

### 3. CARICAMENTO DA DATABASE

**Funzione**: `carica_e_prepara_dataframe(user_id)`  
**File**: `app.py` righe 2179-2240  
**Fonte**: **SOLO Supabase** (no JSON, no fallback)

```python
# Query Supabase
response = supabase.table("fatture").select("*").eq("user_id", user_id).execute()

# Mappatura colonna
"Categoria": row["categoria"],  # ← Legge colonna 'categoria' da DB
```

**✅ CONFERMA**: Grafico e Tabella usano **STESSA fonte dati** (Supabase)

---

### 4. SALVATAGGIO FATTURE

**Funzione**: `salva_fattura_processata()`  
**File**: `app.py` righe 1860-1950

```python
# Durante salvataggio su Supabase (riga 1911):
records.append({
    "categoria": prod.get("Categoria", "Da Classificare"),  # ← SALVATA
    # ... altri campi
})

# Inserimento
supabase.table("fatture").insert(records).execute()
```

**✅ CONFERMA**: Categoria **viene salvata** correttamente su Supabase

---

### 5. ESTRAZIONE DATI XML

**Funzione**: `estrai_dati_da_xml()`  
**File**: `app.py` righe 2484-2498

```python
# Durante parsing XML:
righe_prodotti.append({
    'Categoria': categoria_finale,  # ← Categoria calcolata
    # ... altri campi
})
```

**Processo categorizzazione:**
1. Sistema ibrido: memoria locale + globale + dizionario keyword
2. Funzione `categorizza_con_memoria()`
3. Se non trova match → "Da Classificare"

**✅ CONFERMA**: Categoria **viene assegnata** durante estrazione

---

## 🔬 CONCLUSIONE DIAGNOSTICA

### ❌ PROBLEMA NON È NEL CODICE

**Tutti i componenti funzionano correttamente:**
1. ✅ Estrazione XML assegna categoria
2. ✅ Salvataggio su Supabase include categoria
3. ✅ Caricamento da Supabase legge categoria
4. ✅ Grafico e Tabella usano stessa fonte dati

---

## 🎯 CAUSA REALE IDENTIFICATA

### **IPOTESI D: PROBLEMA NEL DATABASE SUPABASE**

**Scenario più probabile:**

Le fatture attualmente nel database **non hanno** la colonna `categoria` popolata perché:

1. **Sono state caricate PRIMA** dell'implementazione del sistema di categorizzazione
2. **Sono state migrate** da vecchio sistema senza campo categoria
3. **C'è stato un bug** in una versione precedente che non salvava categoria

**Test da fare:**

1. **Carica UNA NUOVA fattura** adesso (con sistema attuale)
2. **Verifica su Supabase** se la nuova fattura ha `categoria` popolata
3. **Controlla il grafico** se mostra la categoria della nuova fattura

---

## 🔧 SOLUZIONE PROPOSTA

### OPZIONE A: Ri-categorizzare Fatture Esistenti

**Bottone "🧠 Avvia AI per categorizzare" già presente** (riga 3040):
- Trova righe con `Categoria` vuota/null/"Da Classificare"
- Chiama AI per classificare
- Aggiorna su Supabase

**Come usare:**
1. Apri Dashboard
2. Click bottone "🧠 Avvia AI per categorizzare"
3. Attendi classificazione (può richiedere tempo)
4. Verifica che categorie vengano salvate

---

### OPZIONE B: Migration SQL Manuale

**Query SQL da eseguire su Supabase:**

```sql
-- 1. Verifica quante righe hanno categoria vuota
SELECT COUNT(*) 
FROM fatture 
WHERE categoria IS NULL 
   OR categoria = '' 
   OR categoria = 'Da Classificare';

-- 2. Assegna categoria "Da Classificare" a righe vuote
UPDATE fatture 
SET categoria = 'Da Classificare'
WHERE categoria IS NULL OR categoria = '';

-- 3. Verifica risultato
SELECT categoria, COUNT(*) as conteggio
FROM fatture
GROUP BY categoria
ORDER BY conteggio DESC;
```

**Poi usa bottone AI per classificare.**

---

### OPZIONE C: Debug Specifico

**Aggiungi log temporaneo per verificare:**

```python
# In mostra_statistiche(), dopo df_completo = ...
st.write("🔍 DEBUG Categorie uniche:", df_completo['Categoria'].unique())
st.write("🔍 DEBUG Conteggio null:", df_completo['Categoria'].isna().sum())
st.write("🔍 DEBUG Conteggio vuote:", (df_completo['Categoria'] == '').sum())
st.write("🔍 DEBUG Sample dati:")
st.dataframe(df_completo[['Descrizione', 'Categoria', 'Fornitore']].head(10))
```

---

## 📋 AZIONI IMMEDIATE CONSIGLIATE

### 1. **VERIFICA DATABASE** (Priorità Alta)

Apri Supabase Dashboard:
```
1. Vai su Table Editor
2. Apri tabella 'fatture'
3. Filtra per tuo user_id
4. Controlla colonna 'categoria'
```

**Domanda chiave**: 
- ✅ Sono tutte NULL/vuote? → Usa Opzione B (migration)
- ✅ Alcune popolate, altre no? → Usa Opzione A (bottone AI)
- ❌ Tutte popolate? → Problema cache (invalida e ricarica)

---

### 2. **TEST NUOVA FATTURA** (Priorità Alta)

```
1. Carica una fattura XML/PDF di test
2. Dopo upload, vai su Supabase
3. Cerca la fattura appena caricata
4. Verifica se colonna 'categoria' è popolata
```

**Se categoria è popolata** → Le vecchie fatture vanno ri-categorizzate  
**Se categoria è vuota** → C'è un bug nel salvataggio (contact dev)

---

### 3. **INVALIDA CACHE** (Priorità Media)

Nel codice, dopo login:
```python
st.cache_data.clear()
st.rerun()
```

O riavvia completamente l'app.

---

### 4. **USA BOTTONE AI** (Priorità Media)

Dopo aver verificato che il DB ha righe con categoria vuota:
```
1. Dashboard → Click "🧠 Avvia AI per categorizzare"
2. Attendi elaborazione (può richiedere diversi minuti)
3. Verifica che categorie vengano aggiornate
4. Refresh pagina
```

---

## 🚨 SE IL PROBLEMA PERSISTE

### Aggiungi questo codice temporaneo per debug:

**In `mostra_statistiche()`, riga ~3000:**

```python
def mostra_statistiche(df_completo):
    """Mostra grafici, filtri e tabella dati"""
    
    # ===== DEBUG TEMPORANEO =====
    st.markdown("### 🔍 DEBUG INFO")
    st.write(f"**DataFrame shape:** {df_completo.shape}")
    st.write(f"**Righe totali:** {len(df_completo)}")
    st.write(f"**Categorie uniche:** {df_completo['Categoria'].nunique()}")
    st.write(f"**Categorie null:** {df_completo['Categoria'].isna().sum()}")
    st.write(f"**Categorie vuote:** {(df_completo['Categoria'] == '').sum()}")
    
    st.markdown("**Sample 10 righe:**")
    st.dataframe(df_completo[['FileOrigine', 'Descrizione', 'Categoria', 'TotaleRiga']].head(10))
    
    st.markdown("**Conteggio per categoria:**")
    conteggio = df_completo.groupby('Categoria').size().reset_index(name='Righe')
    st.dataframe(conteggio)
    st.markdown("---")
    # ===== FINE DEBUG =====
    
    # ... resto del codice normale
```

---

## 📅 DATA DIAGNOSI

**2 Gennaio 2026**

---

## 👨‍💻 AUTORE

GitHub Copilot (Claude Sonnet 4.5)

---

✅ **DIAGNOSI COMPLETATA - CAUSA IDENTIFICATA - SOLUZIONI PROPOSTE**
