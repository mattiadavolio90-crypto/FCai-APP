# ✅ SISTEMA CATEGORIE DINAMICHE

## 📋 PANORAMICA

Sistema di gestione categorie prodotti con:
- **Database dinamico** su Supabase
- **Icone emoji** nei dropdown
- **Ordine alfabetico** automatico
- **Creazione categorie** riservata agli admin
- **Cache intelligente** (5 minuti TTL)

---

## 🗄️ STRUTTURA DATABASE

### Tabella `categorie`

```sql
CREATE TABLE categorie (
    id BIGSERIAL PRIMARY KEY,
    nome TEXT NOT NULL UNIQUE,          -- "CARNE" (senza emoji)
    icona TEXT DEFAULT '📦',             -- "🍖" (solo emoji)
    ordinamento INTEGER DEFAULT 999,     -- Sort custom (999 = alfabetico)
    attiva BOOLEAN DEFAULT TRUE,         -- Soft delete
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Policy RLS

- **Lettura**: Tutti possono leggere categorie attive
- **Scrittura**: Solo via service_role_key (admin app)

---

## 🔧 FUNZIONI PRINCIPALI

### 1. `carica_categorie_da_db()`

**File**: `app.py`  
**Cache**: 5 minuti (TTL=300s)  
**Ritorna**: Lista `["🍖 CARNE", "🐟 PESCE", ...]`

```python
@st.cache_data(ttl=300, show_spinner=False)
def carica_categorie_da_db():
    """
    Carica categorie dinamiche da Supabase.
    Fallback a lista hardcoded se DB non disponibile.
    """
    # Query da table 'categorie'
    # Ordina per ordinamento, poi alfabetico
    # Formato: icona + spazio + nome
```

**Uso:**
```python
categorie = carica_categorie_da_db()
# Output: ["🍖 CARNE", "🐟 PESCE", "🥬 VERDURE", ...]
```

---

### 2. `estrai_nome_categoria(categoria_con_icona)`

**File**: `app.py`  
**Scopo**: Rimuove emoji per salvare nel database

```python
def estrai_nome_categoria(categoria_con_icona):
    """
    Estrae solo nome dalla categoria.
    
    Input:  "🍖 CARNE" o "CARNE"
    Output: "CARNE"
    """
```

**Uso:**
```python
nome = estrai_nome_categoria("🍖 CARNE")  # → "CARNE"
nome = estrai_nome_categoria("PESCE")     # → "PESCE"
```

---

### 3. `aggiungi_icona_categoria(nome_categoria)`

**File**: `app.py`  
**Scopo**: Recupera emoji da database e la aggiunge

```python
def aggiungi_icona_categoria(nome_categoria):
    """
    Aggiunge icona emoji al nome.
    
    Input:  "CARNE"
    Output: "🍖 CARNE"
    """
```

**Uso:**
```python
categoria_display = aggiungi_icona_categoria("CARNE")  # → "🍖 CARNE"
```

---

## 📊 INTEGRAZIONE NEI DROPDOWN

### In `app.py` (Editor Fatture Cliente)

**Prima** (statico):
```python
"Categoria": st.column_config.SelectboxColumn(
    options=TUTTE_LE_CATEGORIE  # Lista hardcoded
)
```

**Dopo** (dinamico):
```python
categorie_disponibili = carica_categorie_da_db()

"Categoria": st.column_config.SelectboxColumn(
    options=categorie_disponibili  # Caricato da DB
)
```

---

### In `admin.py` (Gestione Memoria Globale)

**Prima**:
```python
CATEGORIE_DISPONIBILI = [
    "🍖 CARNE",
    "🐟 PESCE",
    # ... lista hardcoded
]
```

**Dopo**:
```python
from app import carica_categorie_da_db

categorie_disponibili = carica_categorie_da_db()
```

---

## 💾 SALVATAGGIO CATEGORIE

### ✅ REGOLA FONDAMENTALE

**Nel database salviamo SOLO il nome senza emoji.**

```python
# ❌ SBAGLIATO
categoria_db = "🍖 CARNE"  # NON salvare emoji nel DB!

# ✅ CORRETTO
categoria_raw = "🍖 CARNE"
categoria_db = estrai_nome_categoria(categoria_raw)  # "CARNE"
```

### Esempio Salvataggio in `app.py`

```python
for index, row in edited_df.iterrows():
    nuova_cat_raw = row['Categoria']  # Potrebbe avere emoji
    
    # ✅ ESTRAI NOME
    nuova_cat = estrai_nome_categoria(nuova_cat_raw)
    
    # Salva nel DB
    supabase.table("fatture").update({
        "categoria": nuova_cat  # Solo "CARNE", non "🍖 CARNE"
    }).execute()
```

---

## 👨‍💼 UI GESTIONE CATEGORIE (SOLO ADMIN)

### Posizione
`pages/admin.py` → TAB 4 "🧠 Memoria Globale AI" → Expander "⚙️ Gestione Categorie"

### Funzionalità

#### 1. Form Creazione Categoria
```python
- Nome Categoria (MAIUSCOLO)
- Emoji Icona (singolo carattere)
- Ordinamento (1-999, default 999 = alfabetico)
- Bottone "✅ Crea Categoria"
```

#### 2. Validazioni
- Nome non vuoto (min 2 caratteri)
- Nome MAIUSCOLO automatico
- Check duplicati (constraint UNIQUE)
- Emoji default '📦' se non specificata

#### 3. Salvataggio
```python
supabase.table('categorie').insert({
    'nome': 'PASTA FRESCA',
    'icona': '🍝',
    'ordinamento': 85,
    'attiva': True
}).execute()

# Invalida cache
st.cache_data.clear()
```

#### 4. Preview Categorie
- Mostra prime 15 categorie esistenti
- Formato: `✅ 🍖 CARNE` (attiva) o `❌ 🍖 CARNE` (disattivata)
- Ordine alfabetico per nome

---

## 🔄 FLUSSO COMPLETO

### 1. ADMIN CREA NUOVA CATEGORIA

```mermaid
ADMIN → Form "Nuova Categoria"
       ↓
   Inserimento DB (table 'categorie')
       ↓
   st.cache_data.clear()
       ↓
   Rerun automatico
```

### 2. CLIENTE USA CATEGORIA

```mermaid
Cliente → Apre editor fatture
        ↓
    carica_categorie_da_db()
        ↓
    Dropdown mostra "🍖 CARNE", "🐟 PESCE", ...
        ↓
    Cliente seleziona "🍖 CARNE"
        ↓
    Salvataggio: estrai_nome_categoria() → "CARNE"
        ↓
    DB fatture: categoria = "CARNE"
```

### 3. VISUALIZZAZIONE CON ICONE

```mermaid
Query DB fatture
    ↓
categoria = "CARNE" (senza emoji)
    ↓
aggiungi_icona_categoria("CARNE")
    ↓
Display: "🍖 CARNE"
```

---

## ⚡ PERFORMANCE & CACHE

### Cache Strategie

1. **Categorie**: Cache 5 minuti
   ```python
   @st.cache_data(ttl=300)
   def carica_categorie_da_db()
   ```

2. **Invalidazione**: Dopo creazione nuova categoria
   ```python
   st.cache_data.clear()
   ```

3. **Fallback**: Lista hardcoded se DB offline

### Query Ottimizzate

```sql
-- Caricamento categorie (veloce)
SELECT nome, icona, ordinamento 
FROM categorie 
WHERE attiva = TRUE 
ORDER BY ordinamento;

-- Icona singola categoria (cached)
SELECT icona 
FROM categorie 
WHERE nome = 'CARNE' 
  AND attiva = TRUE 
LIMIT 1;
```

---

## 🧪 TEST & VALIDAZIONI

### Test 1: Creazione Categoria Admin
1. Login come admin
2. TAB 4 → Expander "Gestione Categorie"
3. Compila form: Nome="SUSHI", Icona="🍣"
4. Click "Crea Categoria"
5. ✅ Verifica: Categoria appare in preview
6. ✅ Verifica: Dropdown clienti mostra "🍣 SUSHI"

### Test 2: Uso Categoria Cliente
1. Login come cliente
2. Editor Fatture → Dropdown categoria
3. ✅ Verifica: Mostra emoji + nome
4. Seleziona "🍖 CARNE"
5. Salva modifiche
6. ✅ Verifica DB: `categoria = "CARNE"` (senza emoji)

### Test 3: Fallback Offline
1. Disattiva connessione Supabase
2. Apri dropdown categorie
3. ✅ Verifica: Mostra lista fallback hardcoded

### Test 4: Cache Invalidation
1. Admin crea categoria "🥟 RAVIOLI"
2. ✅ Verifica: Cache svuotata automaticamente
3. ✅ Verifica: Categoria disponibile immediatamente

---

## 🚨 TROUBLESHOOTING

### Problema: Dropdown non mostra emoji

**Causa**: Encoding UTF-8 non supportato  
**Soluzione**: Verifica browser supporti UTF-8, usa emoji standard

### Problema: Categoria salvata con emoji nel DB

**Causa**: Mancata chiamata `estrai_nome_categoria()`  
**Soluzione**: 
```python
# ❌ SBAGLIATO
categoria = row['Categoria']

# ✅ CORRETTO
categoria = estrai_nome_categoria(row['Categoria'])
```

### Problema: Cache non si invalida

**Causa**: `st.cache_data.clear()` non chiamato  
**Soluzione**: Aggiungi dopo INSERT:
```python
supabase.table('categorie').insert({...}).execute()
st.cache_data.clear()  # ← IMPORTANTE
st.rerun()
```

### Problema: Admin non vede UI gestione

**Causa**: Email non in lista ADMIN_EMAILS  
**Soluzione**: Verifica in `admin.py`:
```python
ADMIN_EMAILS = ['mattiadavolio90@gmail.com']
is_admin = user_email in ADMIN_EMAILS
```

---

## 📦 FILE MODIFICATI

| File | Modifiche |
|------|-----------|
| `migrations/003_create_categorie.sql` | ✅ Creazione tabella + popolamento |
| `app.py` | ✅ Funzioni caricamento/estrazione/aggiunta icone |
| `app.py` | ✅ Dropdown editor usa `carica_categorie_da_db()` |
| `app.py` | ✅ Salvataggio estrae nome con `estrai_nome_categoria()` |
| `pages/admin.py` | ✅ Import funzioni da app.py |
| `pages/admin.py` | ✅ Dropdown usa categorie dinamiche |
| `pages/admin.py` | ✅ UI creazione categorie (expander admin) |
| `pages/admin.py` | ✅ Salvataggio estrae nome categoria |

---

## 🎯 BENEFICI

1. **✅ Flessibilità**: Admin crea categorie senza modificare codice
2. **✅ UX Migliorata**: Emoji visibili nei dropdown
3. **✅ Ordine Pulito**: Alfabetico automatico
4. **✅ Scalabilità**: Nessun limite numero categorie
5. **✅ Multi-Tenant**: Categorie condivise tra tutti i clienti
6. **✅ Performance**: Cache 5 minuti riduce query DB
7. **✅ Fallback**: Funziona anche offline (lista hardcoded)

---

## 📅 DATA IMPLEMENTAZIONE

**2 Gennaio 2026**

---

## 👨‍💻 AUTORE

GitHub Copilot (Claude Sonnet 4.5)

---

✅ **SISTEMA CATEGORIE DINAMICHE COMPLETO E FUNZIONANTE**
