# 🔧 IMPLEMENTAZIONE STRATEGIA IBRIDA - Righe €0 con Review

**Data**: 15 Gennaio 2026  
**Stato**: Analisi + Soluzione Definitiva

---

## 📋 INDICE

1. [Obiettivo](#obiettivo)
2. [Analisi Implementazione Proposta](#analisi-implementazione-proposta)
3. [Problemi Identificati](#problemi-identificati)
4. [Soluzione Definitiva Corretta](#soluzione-definitiva-corretta)
5. [Checklist Esecuzione](#checklist-esecuzione)

---

## OBIETTIVO

**Problema Attuale**: Le righe categorizzate come "📝 NOTE E DICITURE" vengono **scartate al parsing** (`continue`) e **mai salvate nel database**. Questo causa perdita di dati irrecuperabile.

**Soluzione**: Strategia ibrida con flag `needs_review`:
- Salvare TUTTE le righe nel database
- Marcare righe sospette con `needs_review = true`
- Admin Panel per validare/ignorare
- Dashboard utente vede solo righe validate

---

## ANALISI IMPLEMENTAZIONE PROPOSTA

### Valutazione Parti Originali

| Parte | Componente | Valutazione | Note |
|-------|-----------|-------------|------|
| PARTE 1 | Modifica parsing | ⚠️ Migliorabile | Troppo aggressivo con €0 |
| PARTE 2 | Campo needs_review in append | ✅ Corretto | Nessuna modifica necessaria |
| PARTE 3 | Salvataggio DB | ✅ Corretto | Nessuna modifica necessaria |
| PARTE 4 | Filtro app.py | ❌ Errata | Logica invertita |
| PARTE 5 | Query Admin Panel | ⚠️ Inefficiente | 2 query invece di 1 |
| PARTE 6 | Bottoni azione Admin | ❌ Non funziona | Pattern Streamlit errato |
| PARTE 7 | SQL Supabase | ✅ Corretto | Aggiungere campi audit |

---

## PROBLEMI IDENTIFICATI

### ❌ PROBLEMA 1: Filtro App.py - Logica INVERTITA

**Codice Proposto (ERRATO):**
```python
df_completo = df_completo[
    ~((df_completo['Categoria'] == '📝 NOTE E DICITURE') & 
      (df_completo['needs_review'] == False))
].copy()
```

**Problema**: Questo MOSTRA le righe `needs_review=True` nella dashboard utente!
Le righe in review dovrebbero apparire SOLO in Admin Panel, non nella dashboard cliente.

**Comportamento Errato**:
- ❌ Riga NOTE con `needs_review=True` → VISIBILE a utente
- ❌ Riga normale con `needs_review=True` → VISIBILE a utente (prima della validazione)

---

### ❌ PROBLEMA 2: Pattern Streamlit Impossibile

**Codice Proposto (ERRATO):**
```python
if st.button("✅", key=f"validate_{row_id}"):
    categoria_fb = st.selectbox(...)  # ❌ NON FUNZIONA
    if st.button("Conferma"):         # ❌ MAI ESEGUITO
```

**Problema**: In Streamlit, dopo un click su `st.button`, avviene un **rerun** della pagina. 
Il `selectbox` dentro l'`if` non viene mai renderizzato perché al rerun il bottone torna `False`.

---

### ⚠️ PROBLEMA 3: Troppo Aggressivo con €0

**Codice Proposto:**
```python
if prezzo_unitario == 0 or totale_riga == 0:
    needs_review = True  # ❌ TUTTI i €0 vanno in review
```

**Problema**: Anche prodotti omaggio **già categorizzati correttamente** (es. "CAMPIONE OLIO GRATUITO" → "🛢️ OLIO") finiscono in review inutilmente.

**Conseguenza**: Admin sovraccaricato di righe da validare che sono già corrette.

---

### ⚠️ PROBLEMA 4: Query Inefficiente

**Codice Proposto:**
```python
response_zero = query_zero.execute()    # Query 1
response_review = query_review.execute() # Query 2
df = pd.concat([df_zero, df_review]).drop_duplicates(subset=['id'])
```

**Problema**: Due query separate + concat + drop_duplicates è inefficiente.
Supabase supporta `.or_()` per condizioni multiple in una singola query.

---

### ⚠️ PROBLEMA 5: Manca Audit Trail

**Mancanza**: Non c'è tracciabilità di chi ha validato cosa e quando.

**Conseguenza**: Impossibile ricostruire storico decisioni in caso di errori.

---

## SOLUZIONE DEFINITIVA CORRETTA

### PARTE 0: SQL SUPABASE (Eseguire PRIMA di tutto)

```sql
-- ============================================================
-- ESEGUIRE IN SUPABASE SQL EDITOR PRIMA DI MODIFICARE CODICE
-- ============================================================

-- 1. Colonna principale needs_review
ALTER TABLE fatture 
ADD COLUMN IF NOT EXISTS needs_review BOOLEAN DEFAULT FALSE;

-- 2. Campi audit per tracciabilità
ALTER TABLE fatture 
ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS reviewed_by TEXT;

-- 3. Indice per performance query
CREATE INDEX IF NOT EXISTS idx_fatture_needs_review 
ON fatture(needs_review) WHERE needs_review = true;

-- 4. Indice composito per query admin
CREATE INDEX IF NOT EXISTS idx_fatture_review_prezzo 
ON fatture(needs_review, prezzo_unitario);

-- 5. Verifica colonne aggiunte
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'fatture' 
AND column_name IN ('needs_review', 'reviewed_at', 'reviewed_by');
```

---

### PARTE 1: Modifica Parsing (invoice_service.py)

**File**: `services/invoice_service.py`  
**Posizione**: Circa linea 215-217

**TROVA:**
```python
# Escludi diciture
if categoria_finale == "📝 NOTE E DICITURE":
    logger.info(f"⊗ Riga ESCLUSA (dicitura): {descrizione}")
    continue
```

**SOSTITUISCI CON:**
```python
# ============================================================
# STRATEGIA IBRIDA: Salva tutto, marca per review se necessario
# ============================================================
needs_review = False

# CASO 1: Prezzo €0 con categoria DICITURA o DA CLASSIFICARE
if prezzo_unitario == 0 or totale_riga == 0:
    if categoria_finale == "📝 NOTE E DICITURE":
        needs_review = True
        logger.info(f"🔍 Dicitura €0 → review: {descrizione[:50]}")
    elif categoria_finale == "Da Classificare":
        needs_review = True
        logger.info(f"⚠️ €0 non classificato → review: {descrizione[:50]}")
    else:
        # Prodotto omaggio già categorizzato correttamente → OK
        needs_review = False
        logger.info(f"🎁 Omaggio categorizzato: {descrizione[:50]} → {categoria_finale}")

# CASO 2: NOTE E DICITURE con prezzo > 0 (anomalia!)
elif categoria_finale == "📝 NOTE E DICITURE" and prezzo_unitario > 0:
    needs_review = True
    logger.warning(f"⚠️ NOTE con €{prezzo_unitario:.2f} → review obbligatorio: {descrizione[:50]}")

# CASO 3: Tutto il resto → salva normalmente
else:
    needs_review = False

# ❌ RIMOSSO: continue → ora salviamo SEMPRE
```

---

### PARTE 2: Campo needs_review in Append (invoice_service.py)

**File**: `services/invoice_service.py`  
**Posizione**: Circa linea 220-235, blocco `righe_prodotti.append({...})`

**AGGIUNGI** campo `needs_review` nel dizionario:

```python
righe_prodotti.append({
    'Numero_Riga': idx,
    'Codice_Articolo': codice_articolo,
    'Descrizione': descrizione,
    'Quantita': quantita,
    'Unita_Misura': unita_misura,
    'Prezzo_Unitario': round(prezzo_unitario, 2),
    'IVA_Percentuale': aliquota_iva,
    'Totale_Riga': round(totale_riga, 2),
    'Fornitore': fornitore,
    'Categoria': categoria_finale,
    'Data_Documento': data_documento,
    'File_Origine': file_caricato.name,
    'Prezzo_Standard': prezzo_std,
    'needs_review': needs_review  # ← NUOVO CAMPO
})
```

---

### PARTE 3: Salvataggio DB (invoice_service.py)

**File**: `services/invoice_service.py`  
**Posizione**: Funzione `salva_fattura_processata()`, circa linea 620-640

**AGGIUNGI** nel dict `records.append({...})`:

```python
records.append({
    "user_id": user_id,
    "file_origine": nome_file,
    "numero_riga": prod.get("NumeroRiga", prod.get("Numero_Riga", 0)),
    "data_documento": prod.get("DataDocumento", prod.get("Data_Documento", None)),
    "fornitore": prod.get("Fornitore", "Sconosciuto"),
    "descrizione": prod.get("Descrizione", ""),
    "quantita": prod.get("Quantita", 1),
    "unita_misura": prod.get("UnitaMisura", prod.get("Unita_Misura", "")),
    "prezzo_unitario": prod.get("PrezzoUnitario", prod.get("Prezzo_Unitario", 0)),
    "iva_percentuale": prod.get("IVAPercentuale", prod.get("IVA_Percentuale", 0)),
    "totale_riga": prod.get("TotaleRiga", prod.get("Totale_Riga", 0)),
    "categoria": categoria_raw,
    "codice_articolo": prod.get("CodiceArticolo", prod.get("Codice_Articolo", "")),
    "prezzo_standard": float(prezzo_std) if prezzo_std and pd.notna(prezzo_std) else None,
    "needs_review": prod.get("needs_review", False)  # ← NUOVO CAMPO
})
```

---

### PARTE 4: Filtro App.py (CORRETTO)

**File**: `app.py`  
**Posizione**: Circa linea 1353

**TROVA:**
```python
df_completo = df_completo[df_completo['Categoria'].fillna('') != '📝 NOTE E DICITURE'].copy()
```

**SOSTITUISCI CON:**
```python
# ============================================================
# FILTRO DASHBOARD: Escludi NOTE + righe in review
# Le righe needs_review=True vanno SOLO in Admin Panel
# ============================================================
righe_prima = len(df_completo)

# Costruisci maschera esclusione
mask_escludi = pd.Series([False] * len(df_completo), index=df_completo.index)

# 1. Escludi TUTTE le NOTE E DICITURE (validate o meno)
mask_note = df_completo['Categoria'].fillna('') == '📝 NOTE E DICITURE'
mask_escludi = mask_escludi | mask_note

# 2. Escludi righe in review (qualsiasi categoria)
if 'needs_review' in df_completo.columns:
    mask_review = df_completo['needs_review'].fillna(False) == True
    mask_escludi = mask_escludi | mask_review

# Applica filtro (MANTIENI righe NON escluse)
df_completo = df_completo[~mask_escludi].copy()

righe_dopo = len(df_completo)
if righe_prima > righe_dopo:
    logger.info(f"Escluse da dashboard: {righe_prima - righe_dopo} righe (NOTE + review)")
```

---

### PARTE 5: Query Admin Panel (OTTIMIZZATA)

**File**: `pages/admin.py`  
**Posizione**: Funzione `carica_righe_zero_con_filtro()`, circa linea 1437

**SOSTITUISCI INTERA FUNZIONE:**
```python
def carica_righe_zero_con_filtro(cliente_id=None):
    """
    Carica righe da validare: €0 OPPURE needs_review=true.
    Query singola ottimizzata con OR.
    """
    try:
        # Query singola con OR per entrambe le condizioni
        query = supabase.table('fatture')\
            .select('id, descrizione, categoria, fornitore, file_origine, data_documento, user_id, prezzo_unitario, needs_review, reviewed_at, reviewed_by')\
            .or_('prezzo_unitario.eq.0,needs_review.eq.true')
        
        # Applica filtro cliente se specificato
        if cliente_id:
            query = query.eq('user_id', cliente_id)
        
        response = query.execute()
        
        df = pd.DataFrame(response.data) if response.data else pd.DataFrame()
        
        # Log statistiche
        if not df.empty:
            n_zero = len(df[df['prezzo_unitario'] == 0]) if 'prezzo_unitario' in df.columns else 0
            n_review = len(df[df['needs_review'] == True]) if 'needs_review' in df.columns else 0
            logger.info(f"🔍 Righe da validare: {n_zero} €0 | {n_review} needs_review | {len(df)} totali (dedup)")
        
        return df
        
    except Exception as e:
        logger.error(f"Errore caricamento righe review: {e}")
        return pd.DataFrame()
```

---

### PARTE 6: Bottoni Azione Admin (PATTERN CORRETTO)

**File**: `pages/admin.py`  
**Posizione**: Dopo visualizzazione righe €0, circa linea 1650-1700

**SOSTITUISCI blocco azioni con:**
```python
# ============================================================
# AZIONI PER OGNI DESCRIZIONE UNIVOCA
# ============================================================
for idx, (descrizione, group) in enumerate(df_grouped.groupby('descrizione')):
    occorrenze = len(group)
    row_id = group.iloc[0]['id']
    categoria_attuale = group.iloc[0].get('categoria', 'N/A')
    prezzo = group.iloc[0].get('prezzo_unitario', 0)
    needs_review_flag = group.iloc[0].get('needs_review', False)
    
    # Badge review
    review_badge = "🔍" if needs_review_flag else ""
    
    # Layout riga
    col_desc, col_occ, col_cat, col_prezzo, col_azioni = st.columns([4, 1, 2, 1, 2])
    
    with col_desc:
        st.text(f"{review_badge} {descrizione[:50]}...")
    with col_occ:
        st.text(f"x{occorrenze}")
    with col_cat:
        st.text(categoria_attuale[:20] if categoria_attuale else "N/A")
    with col_prezzo:
        st.text(f"€{prezzo:.2f}")
    
    with col_azioni:
        # Pattern corretto: selectbox + bottoni nella stessa riga
        action_cols = st.columns([1, 1])
        
        with action_cols[0]:
            if st.button("❌", key=f"ignore_{idx}", help="Ignora definitivamente"):
                try:
                    from datetime import datetime
                    result = supabase.table('fatture').update({
                        'categoria': '📝 NOTE E DICITURE',
                        'needs_review': False,
                        'reviewed_at': datetime.now().isoformat(),
                        'reviewed_by': 'admin'
                    }).eq('descrizione', descrizione).execute()
                    
                    st.success(f"❌ {len(result.data) if result.data else occorrenze} righe ignorate")
                    st.cache_data.clear()
                    time.sleep(0.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"Errore: {e}")
        
        with action_cols[1]:
            if st.button("✏️", key=f"edit_{idx}", help="Modifica categoria"):
                st.session_state[f"editing_{idx}"] = True
                st.rerun()
    
    # Expander per modifica categoria (appare se cliccato ✏️)
    if st.session_state.get(f"editing_{idx}", False):
        with st.expander(f"🔧 Modifica: {descrizione[:30]}...", expanded=True):
            nuova_categoria = st.selectbox(
                "Nuova categoria:",
                ["🥩 CARNE", "🐟 PESCE", "🥬 VERDURE", "🍝 PASTA RISO", 
                 "🧀 FORMAGGI", "🥛 LATTICINI", "🍞 PANE", "🛢️ OLIO",
                 "🍕 PIZZA", "🍰 PASTICCERIA", "☕ CAFFÈ", "🍺 BIRRE",
                 "🍷 VINI", "🧃 BEVANDE", "💧 ACQUA", "🧊 SURGELATI",
                 "📦 NO FOOD", "📝 NOTE E DICITURE", "❓ Da Classificare"],
                key=f"newcat_{idx}"
            )
            
            col_confirm, col_cancel = st.columns(2)
            
            with col_confirm:
                if st.button("✅ Conferma", key=f"confirm_{idx}"):
                    try:
                        from datetime import datetime
                        result = supabase.table('fatture').update({
                            'categoria': nuova_categoria,
                            'needs_review': False,
                            'reviewed_at': datetime.now().isoformat(),
                            'reviewed_by': 'admin'
                        }).eq('descrizione', descrizione).execute()
                        
                        st.success(f"✅ {len(result.data) if result.data else occorrenze} righe → {nuova_categoria}")
                        del st.session_state[f"editing_{idx}"]
                        st.cache_data.clear()
                        time.sleep(0.5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Errore: {e}")
            
            with col_cancel:
                if st.button("🚫 Annulla", key=f"cancel_{idx}"):
                    del st.session_state[f"editing_{idx}"]
                    st.rerun()
    
    st.markdown("---")
```

---

## CHECKLIST ESECUZIONE

### Ordine di Esecuzione

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: SQL Supabase (PARTE 0)                            │
│  → Esegui SQL in Supabase SQL Editor                       │
│  → Verifica colonne create                                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: invoice_service.py (PARTI 1, 2, 3)                │
│  → Modifica parsing (rimuovi continue)                     │
│  → Aggiungi needs_review in append                         │
│  → Aggiungi needs_review in salvataggio DB                 │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: app.py (PARTE 4)                                  │
│  → Modifica filtro dashboard                               │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: admin.py (PARTI 5, 6)                             │
│  → Sostituisci funzione query                              │
│  → Sostituisci blocco azioni                               │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  STEP 5: Test                                              │
│  → Carica fattura di test                                  │
│  → Verifica riga €0 in Admin Panel                         │
│  → Valida/Ignora e verifica dashboard                      │
└─────────────────────────────────────────────────────────────┘
```

### Checklist Dettagliata

```
□ STEP 1: SQL Supabase
  □ Eseguito ALTER TABLE per needs_review
  □ Eseguito ALTER TABLE per reviewed_at, reviewed_by
  □ Creato indice idx_fatture_needs_review
  □ Creato indice idx_fatture_review_prezzo
  □ Verificato colonne con SELECT

□ STEP 2: invoice_service.py
  □ Trovato blocco "Escludi diciture" (linea ~215)
  □ Sostituito con logica needs_review (PARTE 1)
  □ Trovato blocco righe_prodotti.append (linea ~220)
  □ Aggiunto campo needs_review (PARTE 2)
  □ Trovato blocco records.append in salva_fattura_processata (linea ~620)
  □ Aggiunto campo needs_review (PARTE 3)

□ STEP 3: app.py
  □ Trovato filtro diciture (linea ~1353)
  □ Sostituito con nuovo filtro mask (PARTE 4)

□ STEP 4: admin.py
  □ Trovato funzione carica_righe_zero_con_filtro (linea ~1437)
  □ Sostituito con query ottimizzata (PARTE 5)
  □ Trovato blocco azioni bottoni (linea ~1650)
  □ Sostituito con pattern expander (PARTE 6)

□ STEP 5: Test
  □ Riavviato Streamlit
  □ Caricato fattura con riga €0
  □ Riga appare in Admin → Review Righe €0
  □ Cliccato ❌ Ignora → riga scompare
  □ Caricato altra fattura con riga €0
  □ Cliccato ✏️ → expander aperto
  □ Selezionato categoria → ✅ Conferma
  □ Riga appare in dashboard principale
```

---

## 🧪 TEST FINALE

### Scenario Test

1. **Carica** fattura `IT11716900151_01HI8.xml` (o qualsiasi con riga €0)

2. **Verifica LOG**:
   ```
   🔍 Dicitura €0 → review: [descrizione]
   ```
   oppure
   ```
   🎁 Omaggio categorizzato: [descrizione] → [categoria]
   ```

3. **Verifica DASHBOARD**: Riga €0 **NON** visibile (filtrata)

4. **Vai ADMIN → Review Righe €0**:
   - Riga visibile con badge 🔍
   - Bottoni ❌ e ✏️ funzionanti

5. **Test IGNORA**:
   - Clicca ❌
   - Riga scompare dalla lista
   - Verifica DB: `categoria = '📝 NOTE E DICITURE'`, `needs_review = false`

6. **Test VALIDA**:
   - Clicca ✏️ su altra riga
   - Expander si apre
   - Seleziona categoria (es. "🥩 CARNE")
   - Clicca ✅ Conferma
   - Riga scompare da Admin
   - Riga **APPARE** in dashboard principale con categoria selezionata

---

## 📊 RIEPILOGO MODIFICHE

| File | Linee | Modifica |
|------|-------|----------|
| **Supabase** | - | 3 colonne + 2 indici |
| **invoice_service.py** | ~215 | Rimuovi `continue`, aggiungi logica `needs_review` |
| **invoice_service.py** | ~220 | Campo `needs_review` in append |
| **invoice_service.py** | ~620 | Campo `needs_review` in salvataggio |
| **app.py** | ~1353 | Filtro mask con esclusione review |
| **admin.py** | ~1437 | Query ottimizzata con `.or_()` |
| **admin.py** | ~1650 | Bottoni con pattern expander |

---

## ⚠️ NOTE IMPORTANTI

1. **NON modificare** logiche AI/categorizzazione esistenti
2. **NON toccare** altre funzioni app.py (alert, dettaglio, ecc)
3. **Backup** database prima di eseguire SQL
4. **Testare** su ambiente sviluppo prima di produzione
5. **Eseguire** SQL Supabase **PRIMA** di modificare codice Python

---

**DOCUMENTO COMPLETATO** - 15 Gennaio 2026  
**Pronto per Implementazione**
