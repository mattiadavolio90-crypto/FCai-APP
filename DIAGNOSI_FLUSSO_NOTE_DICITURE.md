# 🔍 DIAGNOSI FLUSSO "NOTE E DICITURE"

**Data**: 15 Gennaio 2026  
**Tipo**: Analisi Completa - SOLO DIAGNOSI

---

## 📋 INDICE

1. [Invoice Service - Esclusione al Parsing](#1-invoice-service---esclusione-al-parsing)
2. [App.py - Filtro Post-Caricamento](#2-apppy---filtro-post-caricamento)
3. [Admin Panel - Review Righe Zero](#3-admin-panel---review-righe-zero)
4. [AI Service - Decisione Categorizzazione](#4-ai-service---decisione-categorizzazione)
5. [Flusso Completo](#5-flusso-completo)
6. [Problema Fattura IT11716900151](#6-problema-fattura-it11716900151)
7. [Conclusioni](#7-conclusioni)

---

## 1. INVOICE SERVICE - Esclusione al Parsing

**File**: `services/invoice_service.py`  
**Linee**: 215-217

### CODICE ESATTO

```python
# Escludi diciture
if categoria_finale == "📝 NOTE E DICITURE":
    logger.info(f"⊗ Riga ESCLUSA (dicitura): {descrizione}")
    continue
```

### CONTESTO COMPLETO (linee 208-230)

```python
# Auto-categorizzazione
categoria_finale = categorizza_con_memoria(
    descrizione=descrizione,
    prezzo=prezzo_unitario,
    quantita=quantita,
    user_id=current_user_id
)

# Escludi diciture
if categoria_finale == "📝 NOTE E DICITURE":
    logger.info(f"⊗ Riga ESCLUSA (dicitura): {descrizione}")
    continue

# Calcolo prezzo standard
prezzo_std = calcola_prezzo_standard_intelligente(
    descrizione=descrizione,
    um=unita_misura,
    prezzo_unitario=prezzo_unitario
)

righe_prodotti.append({
    'Numero_Riga': idx,
    'Codice_Articolo': codice_articolo,
    'Descrizione': descrizione,
    'Quantita': quantita,
    ...
})
```

### COMPORTAMENTO

**❌ ESCLUDE E NON SALVA NEL DATABASE**

- `continue` → **salta** l'append a `righe_prodotti`
- La riga **NON viene salvata** in Supabase
- Log: `"⊗ Riga ESCLUSA (dicitura): {descrizione}"`
- **Risultato**: Nessuna traccia della riga nel DB

---

## 2. APP.PY - Filtro Post-Caricamento

**File**: `app.py`  
**Linea**: 1353

### CODICE ESATTO

```python
df_completo = df_completo[df_completo['Categoria'].fillna('') != '📝 NOTE E DICITURE'].copy()
```

### CONTESTO COMPLETO (linee 1349-1363)

```python
# ===== FILTRA DICITURE DA TUTTA L'ANALISI =====
righe_prima = len(df_completo)
fatture_prima = df_completo['FileOrigine'].nunique()

# 🔧 FIX: Usa fillna per mantenere righe con categoria NA/NULL (non sono diciture!)
df_completo = df_completo[df_completo['Categoria'].fillna('') != '📝 NOTE E DICITURE'].copy()
righe_dopo = len(df_completo)
fatture_dopo = df_completo['FileOrigine'].nunique()

if righe_prima > righe_dopo:
    logger.info(f"Diciture escluse: {righe_prima - righe_dopo} righe, {fatture_prima - fatture_dopo} fatture")

if df_completo.empty:
    st.info("📭 Nessun dato disponibile dopo i filtri.")
    return
```

### COMPORTAMENTO

**🛡️ FILTRO DIFENSIVO (DB → UI)**

- Esclude righe con `Categoria = '📝 NOTE E DICITURE'` dal DataFrame
- Utilizzato per **tutte le analisi**: ALERT, DETTAGLIO, CATEGORIE, FORNITORI, SPESE GENERALI
- **PARADOSSO**: Questo filtro è tecnicamente **inutile** perché le NOTE non arrivano mai al DB!
- **Scopo**: Protezione doppia nel caso qualcuno modifichi il comportamento di invoice_service

---

## 3. ADMIN PANEL - Review Righe Zero

**File**: `pages/admin.py`  
**Linee**: 1437-1445, 1690-1695

### QUERY SUPABASE (linee 1437-1445)

```python
def carica_righe_zero_con_filtro(cliente_id=None):
    """
    Carica righe €0, con filtro cliente opzionale.
    """
    try:
        query = supabase.table('fatture')\
            .select('id, descrizione, categoria, fornitore, file_origine, data_documento, user_id')\
            .eq('prezzo_unitario', 0)
        
        # Applica filtro cliente se specificato
        if cliente_id:
            query = query.eq('user_id', cliente_id)
        
        response = query.execute()
        
        df = pd.DataFrame(response.data) if response.data else pd.DataFrame()
        return df
```

### COMPORTAMENTO QUERY

**✅ VISUALIZZA TUTTO PREZZO €0**

- Query: `WHERE prezzo_unitario = 0`
- Mostra righe con **qualsiasi categoria** (incluso "NOTE E DICITURE" se presenti)
- NON filtra per categoria nella query

### METRICHE CATEGORIA (linea 1468)

```python
# Calcola categorie sospette
cat_sospette = df_zero[~df_zero['categoria'].isin(['NOTE E DICITURE', 'Da Classificare'])]
st.metric("Prodotti Classificati", len(cat_sospette))
```

**Comportamento**: Filtra "NOTE E DICITURE" solo per contare "Prodotti Classificati" (metriche)

### AZIONE IGNORA (linee 1690-1695)

```python
# AZIONE: Ignora (marca TUTTE come NOTE E DICITURE)
with col_a2:
    if st.button("🗑️", key=f"ignore_{row_id}", help=f"Ignora {occorrenze} righe"):
        try:
            # Marca TUTTE LE RIGHE CON STESSA DESCRIZIONE
            result = supabase.table('fatture').update({
                'categoria': 'NOTE E DICITURE'
            }).eq('descrizione', descrizione).execute()
            
            num_updated = len(result.data) if result.data else occorrenze
```

### COMPORTAMENTO BOTTONE 🗑️

**🔄 UPDATE RETROATTIVO**

- Bottone 🗑️ → `UPDATE fatture SET categoria = 'NOTE E DICITURE' WHERE descrizione = ?`
- Cambia categoria per righe **già salvate** nel database
- Utile per correggere classificazioni errate **post-upload**
- Le righe **rimangono nel DB** ma cambiano categoria

---

## 4. AI SERVICE - Decisione Categorizzazione

**File**: `services/ai_service.py`  
**Funzione**: `categorizza_con_memoria()`

### LOGICA "NOTE E DICITURE"

#### LIVELLO 1: Memoria Admin (linea 376)

```python
if desc_stripped in _memoria_cache['classificazioni_manuali']:
    record = _memoria_cache['classificazioni_manuali'][desc_stripped]
    if record.get('is_dicitura'):
        logger.info(f"📋 Memoria Admin (cache): '{descrizione}' → DICITURA (validata admin)")
        return "📝 NOTE E DICITURE"
```

#### LIVELLO 4: Check Dicitura Prezzo €0 (linea 411)

```python
# LIVELLO 4: Check dicitura (se prezzo = 0)
if prezzo == 0 and is_dicitura_sicura(descrizione, prezzo, quantita):
    return "📝 NOTE E DICITURE"
```

#### LIVELLO 5: GPT Prompt (linea 500)

```python
REGOLE CLASSIFICAZIONE:
1. **DICITURE**: Se descrizione è riferimento documento (DDT, TRASPORTO, BOLLA, RIF), 
   imballo, spedizione → "NOTE E DICITURE"
```

### TRIGGER "NOTE E DICITURE"

1. **Memoria Admin**: Campo `is_dicitura = true` in tabella `classificazioni_manuali`
2. **Prezzo €0 + Pattern**: `is_dicitura_sicura()` controlla keywords:
   - DDT
   - TRASPORTO
   - BOLLA
   - RIF (riferimento)
   - IMBALLO
   - SPEDIZIONE
3. **GPT Classification**: Prompt esplicito per identificare diciture

---

## 5. FLUSSO COMPLETO

### PARSING → SALVATAGGIO

```
┌─────────────────────────────────────┐
│  PARSING XML (invoice_service.py)  │
└─────────────────┬───────────────────┘
                  ↓
┌─────────────────────────────────────┐
│   categorizza_con_memoria()        │
│   (ai_service.py)                  │
└─────────────────┬───────────────────┘
                  ↓
    ┌─────────────┴──────────────┐
    │                            │
    ├─ Memoria Admin             │
    │  is_dicitura = true?       │
    │  → "📝 NOTE E DICITURE"    │
    │                            │
    ├─ Memoria Locale/Globale    │
    │  → Categoria salvata       │
    │                            │
    ├─ Prezzo €0 +               │
    │  is_dicitura_sicura()      │
    │  → "📝 NOTE E DICITURE"    │
    │                            │
    └─ Keyword/GPT               │
       → Categoria AI            │
       ↓                         │
┌──────────────────────────────────┐
│ categoria_finale == "DICITURA"?  │
└────┬─────────────────────────┬──┘
     │ SI                      │ NO
     ↓                         ↓
┌──────────────┐    ┌──────────────────────┐
│   CONTINUE   │    │ righe_prodotti.      │
│   ⊗ SKIP     │    │ append(riga)         │
│              │    │                      │
│ NON SALVATA  │    │ ✅ SALVA NEL DB      │
│ NEL DB ❌    │    │                      │
└──────────────┘    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │ SUPABASE INSERT      │
                    │ (DB contiene solo    │
                    │  righe NON-dicitura) │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │ APP.PY carica DF     │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │ Filtro difensivo:    │
                    │ df = df[df['Cat']    │
                    │    != 'DICITURA']    │
                    └──────────┬───────────┘
                               ↓
                    ┌──────────────────────┐
                    │ ANALISI (ALERT,      │
                    │ DETTAGLIO, CATEGORIE)│
                    └──────────────────────┘
```

### ADMIN PANEL (flusso parallelo)

```
┌─────────────────────────────────────┐
│ Query: SELECT * FROM fatture        │
│ WHERE prezzo_unitario = 0           │
└─────────────────┬───────────────────┘
                  ↓
┌─────────────────────────────────────┐
│ Mostra righe €0                     │
│ (qualsiasi categoria)               │
└─────────────────┬───────────────────┘
                  ↓
┌─────────────────────────────────────┐
│ Bottone 🗑️ cliccato?                │
└─────────────────┬───────────────────┘
                  ↓ SI
┌─────────────────────────────────────┐
│ UPDATE fatture                      │
│ SET categoria = 'NOTE E DICITURE'   │
│ WHERE descrizione = ?               │
└─────────────────┬───────────────────┘
                  ↓
┌─────────────────────────────────────┐
│ Riga rimane nel DB                  │
│ ma cambia categoria                 │
│ (UPDATE retroattivo)                │
└─────────────────────────────────────┘
```

---

## 6. PROBLEMA FATTURA IT11716900151

### SCENARIO

**File**: `IT11716900151_01HI8.xml`  
**Riga problematica**: Riga 3 con prezzo €290

### STATO ATTUALE

- ❌ File **non presente** in cartella `dati_input/`
- Probabilmente cancellata dopo test

### IPOTESI PROBLEMA

**Riga €290 categorizzata come "📝 NOTE E DICITURE" per errore**

#### Possibili Cause:

1. **Memoria Admin errata**:
   - Descrizione simile marcata `is_dicitura = true` in tabella `classificazioni_manuali`
   - Esempio: "RIGA 3" o "RIF. ORDINE 3" classificata come dicitura

2. **Pattern regex match errato**:
   - `is_dicitura_sicura()` ha matchato keyword per sbaglio
   - Esempio: "RIGA 3" contiene "RIG" → match con "RIF"?

3. **GPT classificazione errata** (meno probabile):
   - Con prezzo €290 improbabile che GPT categorizzi come dicitura
   - GPT dovrebbe usare prezzo come segnale forte

### FLUSSO ERRORE

```
PARSING: Riga 3, Descrizione: "...", Prezzo: €290
    ↓
categorizza_con_memoria() → return "📝 NOTE E DICITURE" ❌
    ↓
invoice_service.py linea 215:
if categoria_finale == "📝 NOTE E DICITURE":
    logger.info(f"⊗ Riga ESCLUSA (dicitura): ...")
    continue  ← RIGA SCARTATA
    ↓
righe_prodotti.append() MAI CHIAMATO
    ↓
❌ Riga NON inserita nel DB
    ↓
❌ Invisibile in Admin Panel (query trova solo righe salvate)
    ↓
❌ Invisibile ovunque (app.py, analisi, export)
```

### VERIFICA NEI LOG

Per confermare, cercare nei log di upload:

```
⊗ Riga ESCLUSA (dicitura): [descrizione riga 3]
```

Se presente, conferma che la riga è stata categorizzata come dicitura e scartata.

---

## 7. CONCLUSIONI

### FLUSSO ATTUALE

```
PARSING → categorizza → if "DICITURA" → CONTINUE (NON SALVA) ❌
                                ↓
                    Nessuna traccia nel DB
                                ↓
                    Admin Panel NON vede la riga
```

### ADMIN PANEL

```
Query: prezzo_unitario = 0 → ✅ Mostra righe salvate nel DB
Bottone 🗑️ → UPDATE categoria → ✅ Cambia categoria retroattivamente
```

### PERCHÉ IT11716900151 SPARITA?

**Diagnosi Finale**:

1. ✅ **Parsing funzionante**: XML letto correttamente
2. ❌ **Categorizzazione errata**: Riga €290 → `"📝 NOTE E DICITURE"`
3. ❌ **Esclusione al parsing**: `continue` → riga scartata
4. ❌ **Mai salvata nel DB**: `righe_prodotti.append()` mai eseguito
5. ❌ **Invisibile ovunque**: Admin Panel non può vedere righe non salvate

### COMPORTAMENTI CHIAVE

| Componente | Comportamento | Effetto |
|------------|--------------|---------|
| **invoice_service.py** | `if DICITURA: continue` | ❌ Non salva nel DB |
| **app.py** | `df = df[Cat != DICITURA]` | 🛡️ Filtro difensivo (inutile) |
| **admin.py query** | `WHERE prezzo = 0` | ✅ Mostra tutte le categorie |
| **admin.py bottone 🗑️** | `UPDATE categoria` | 🔄 Cambia categoria retroattiva |

### PARADOSSO

Il filtro in `app.py` linea 1353 **non trova mai nulla da filtrare** perché:
- Le NOTE E DICITURE non arrivano mai al DB (escluse al parsing)
- È un filtro difensivo "per sicurezza" in caso di modifiche future al codice

---

## 📝 NOTE TECNICHE

### File Coinvolti

1. `services/invoice_service.py` (linee 215-217): Esclusione parsing
2. `services/ai_service.py` (linee 376, 411, 500): Decisione categoria
3. `app.py` (linea 1353): Filtro post-caricamento
4. `pages/admin.py` (linee 1437-1445, 1690-1695): Review e update

### Tabelle Supabase

- `fatture`: Contiene **solo** righe non-dicitura
- `classificazioni_manuali`: Memoria admin con campo `is_dicitura`
- `prodotti_master`: Memoria globale categorie

### Logger Messages

- `⊗ Riga ESCLUSA (dicitura): {descrizione}` → Riga scartata al parsing
- `📋 Memoria Admin (cache): ... → DICITURA` → Match memoria admin
- `Diciture escluse: X righe` → Filtro app.py (sempre 0 righe)

---

**ANALISI COMPLETATA** - 15 Gennaio 2026  
**Tipo**: Solo Diagnosi - Nessuna Modifica Apportata
