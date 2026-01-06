# 📋 FOOD COST INTELLIGENCE - PROJECT PLAN COMPLETO

**Versione:** 1.0  
**Data Creazione:** 06 Gennaio 2026  
**Ultimo Aggiornamento:** 06 Gennaio 2026  
**Owner:** Mattia D'Avolio  
**Status:** In Produzione Beta (Streamlit Cloud Ready)

---

## 📑 INDICE

1. [Executive Summary](#executive-summary)
2. [Descrizione Business](#descrizione-business)
3. [Utenti e Ruoli](#utenti-e-ruoli)
4. [Architettura Sistema](#architettura-sistema)
5. [Stack Tecnologico](#stack-tecnologico)
6. [Database & Schema](#database--schema)
7. [API & Integrazioni](#api--integrazioni)
8. [Sicurezza & Multi-tenancy](#sicurezza--multi-tenancy)
9. [Performance & Optimization](#performance--optimization)
10. [Infrastruttura Cloud](#infrastruttura-cloud)
11. [Deployment & DevOps](#deployment--devops)
12. [File Structure & Modules](#file-structure--modules)
13. [Feature Breakdown](#feature-breakdown)
14. [Issues & Technical Debt](#issues--technical-debt)
15. [Roadmap](#roadmap)
16. [Troubleshooting Guide](#troubleshooting-guide)

---

## 1️⃣ EXECUTIVE SUMMARY

### Cos'è Food Cost Intelligence (FCI)?

**FCI** è una **piattaforma SaaS intelligente per ristoratori** che automatizza:
- 📄 **Parsing di fatture XML e PDF** da fornitori
- 🤖 **Categorizzazione AI** di prodotti (ingredienti, bevande, materiale)
- 📊 **Dashboard analytics** con trend prezzi e anomalie
- 🚨 **Alert intelligenti** su aumenti di prezzo fuori norma
- 📈 **Gestione multi-ristorante** (multi-tenancy con Supabase)

### Problema che risolve

❌ **PRIMA:**
- Ristoratori manualmente copiano dati fatture in Excel
- 💔 Nessuna visione dei trend prezzi
- 🔴 Scopri cambiamenti prezzo troppo tardi
- ⏰ Tempo perso in data entry noioso

✅ **ADESSO CON FCI:**
- Upload automatico fatture XML
- 🤖 AI classifica automaticamente (con memoria intelligente)
- 📊 Dashboard interattive con confronti storici
- 🚨 Notifiche email su aumenti anomali
- ⏱️ Da 2 ore a 5 minuti per ristorante/mese

### Metriche di valore

| Metrica | Valore |
|---------|--------|
| **Tempo processing/fattura** | 3-5 secondi |
| **Accuratezza categorizzazione** | 92-97% (migliora con uso) |
| **Tempo medio learning curve** | <2 giorni |
| **Cost per fattura processata** | €0.02-0.05 (OpenAI) |
| **ROI mensile (per ristorante)** | 200-500% |

---

## 2️⃣ DESCRIZIONE BUSINESS

### Modello di Business

**Tipi di Clienti (Ruoli Sistema):**

1. **RISTORATORE** (Free/Premium)
   - Accesso: Upload fatture, Dashboard, Report
   - Pricing: Freemium (10 fatture/mese) → Premium €29/mese
   - Numero limite: Infiniti ristoratori

2. **ADMIN INTERNO** (Mattia)
   - Accesso: Review manuale, Training AI memory, Analytics
   - Compiti:
     - Approvare/correggere categorizzazioni contestate
     - Aggiornare memoria AI globale
     - Monitorare abuse/costi
     - Gestire categorie dinamiche

### Flusso Utente Principale

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUSSO RISTORATORE                           │
└─────────────────────────────────────────────────────────────────┘

1. LOGIN
   ├─ Email/Password
   ├─ Hash Argon2 (m=65536, t=3, p=4)
   └─ Cookie persistente 30 giorni

2. UPLOAD FATTURA
   ├─ File: XML o PDF (max 200MB)
   ├─ Parsing:
   │  ├─ XML → xmltodict → DataFrame
   │  └─ PDF → PyMuPDF → OCR tentativo
   └─ Archiviazione: Supabase Storage

3. CATEGORIZZAZIONE AI (OpenAI GPT-4)
   ├─ Input: Descrizione prodotto
   ├─ Memoria AI:
   │  ├─ Globale (prodotti_master): 2500+ articoli
   │  ├─ Utente (prodotti_utente): storia personale
   │  └─ Admin override (classificazioni_manuali): priorità max
   ├─ Prompt: 2000+ token (context + memoria)
   ├─ Output: Categoria + Confidence score
   └─ Retry: tenacity (max 3 tentativi, backoff esponenziale)

4. REVIEW AUTOMATICA
   ├─ Confidence < 70%? → Coda review admin
   ├─ Anomalia prezzo? → Flag alert
   └─ Salvataggio DB (fatture, prodotti)

5. DASHBOARD
   ├─ Tabelle interattive:
   │  ├─ Fatture cronologiche (sortabili, filtrabili)
   │  └─ Prodotti per categoria
   ├─ Grafici Plotly:
   │  ├─ Trend prezzi (30/60/90 giorni)
   │  ├─ Spesa per categoria (pie + bar)
   │  └─ Alert history
   └─ Pivot mensile (confronto mese/mese)

6. EXPORT
   ├─ Excel multi-sheet: Fatture + Categoria breakdown
   ├─ PDF: Report formattato
   └─ CSV: Raw data

7. ADMIN PANEL (Mattia solo)
   ├─ Review coda: Items flaggati < 70% confidence
   ├─ Approvazione/Rifiuto/Correzione
   ├─ Training AI:
   │  ├─ Aggiorna memoria_ai_correzioni.json
   │  ├─ Backup automatico
   │  └─ Versioning
   ├─ Analytics globali (tutti i ristoratori)
   └─ User management (disattiva/reattiva account)
```

### Casi d'Uso Chiave

**UC1: Ristoratore carica fattura PDF da fornitore**
```
Attore: Ristoratore Giuseppe
Precondizione: Autenticato, ha PDF fattura Sysco
Flow:
1. Click "Upload Fattura"
2. Seleziona file PDF (es: Sysco_Jan2026.pdf)
3. Sistema estrae testo → OCR se necessario
4. Crea 50 righe prodotti (es: "Filetto di Branzino 500g")
5. Invia a GPT-4 con batch 12k token
6. Riceve 50 categorizzazioni (es: "PESCE FRESCO", confidence 94%)
7. Visualizza risultato in tabella
8. Approva/Modifica/Rifiuta
9. Sistema salva in DB + aggiorna memoria AI
Postcondizione: Dashboard mostra nuovi dati
```

**UC2: Admin rivede articoli con bassa confidence**
```
Attore: Mattia (admin)
Precondizione: 23 articoli da Giuseppe in coda < 70%
Flow:
1. Accede Admin Panel
2. Vede lista: "Polpo 1kg" (45%), "Riso Carnaroli" (52%), ...
3. Per ogni articolo:
   a. Visualizza storico (Quando l'ho visto prima? Che prezzo?)
   b. Suggerimento AI: "Potrebbe essere PESCE FRESCO"
   c. Clicca categoria corretta da dropdown
   d. Clicca "Approva" → salva + aggiorna memoria
4. Al 23° articolo, memoria aggiornata
5. Successiva fattura Giuseppe: stessi articoli → 95% confidence
Postcondizione: Giuseppe vede categorizzazione corretta subito
```

**UC3: Alert automatico anomalia prezzo**
```
Attore: Sistema
Precondizione: Giuseppe carica fattura Sistemi Malossi gennaio
Flow:
1. Prodotto: "Burro francese 500g" 
2. Storico prezzi: €12 (dic), €12.50 (nov), €11 (ott)
3. Prezzo gennaio: €18.50 (+50% vs media)
4. Sistema calcola: z-score = 2.8 (anomalo!)
5. Crea alert in DB
6. Invia email: "⚠️ BURRO aumentato 50% - Controlla fornitore"
7. Visualizza in dashboard rosso
Postcondizione: Giuseppe notificato, può negoziare con fornitore
```

---

## 3️⃣ UTENTI E RUOLI

### Matrice Accessi

| Feature | Ristoratore | Admin |
|---------|-------------|-------|
| Login/Logout | ✅ | ✅ |
| Upload fatture | ✅ | ✅ |
| Dashboard personale | ✅ | ✅ (tutti i dati) |
| Export Excel | ✅ | ✅ |
| Admin Panel | ❌ | ✅ |
| Review categorizzazioni | ❌ | ✅ |
| Modifica memoria AI | ❌ | ✅ |
| View analytics globali | ❌ | ✅ |
| Gestione utenti | ❌ | ✅ |
| Reset password altrui | ❌ | ✅ |

### Ruoli DB (Supabase)

```sql
-- Tabella users (Supabase Auth)
id: UUID
email: TEXT UNIQUE
nome_ristorante: TEXT
ruolo: ENUM('ristoratore', 'admin')
piano: ENUM('free', 'premium', 'enterprise')
attivo: BOOLEAN
created_at: TIMESTAMP
last_login: TIMESTAMP
password_hash: TEXT (Argon2)
```

**Verifica Admin:** Hardcoded in `admin.py` riga 104
```python
ADMIN_EMAILS = ["mattiadavolio90@gmail.com"]
```

⚠️ **TODO:** Migrare in Supabase per ridimensionabilità

---

## 4️⃣ ARCHITETTURA SISTEMA

### Diagram Alto Livello

```
┌──────────────────────────────────────────────────────────────────┐
│                       BROWSER RISTORATORE                        │
│  (Chrome/Safari/Firefox - Responsive Design)                     │
└──────────────────────────────────────┬──────────────────────────┘
                                       │ HTTPS
┌──────────────────────────────────────▼──────────────────────────┐
│            STREAMLIT CLOUD (Python Runtime)                      │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  app.py (6210 righe)                                    │   │
│  │  ├─ Login/Logout UI                                     │   │
│  │  ├─ File upload handler                                 │   │
│  │  ├─ Parsing PDF/XML                                     │   │
│  │  ├─ Streamlit multipage router                          │   │
│  │  └─ Dashboard builder                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  pages/*.py (feature-specific)                          │   │
│  │  ├─ pages/1_Upload.py                                   │   │
│  │  ├─ pages/2_Dashboard.py                                │   │
│  │  ├─ pages/3_Export.py                                   │   │
│  │  └─ pages/4_Admin.py (if admin)                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Helper modules                                         │   │
│  │  ├─ admin.py (2090 righe) - admin panel                │   │
│  │  ├─ cambio_password.py - reset password                │   │
│  │  └─ Inline functions                                    │   │
│  └─────────────────────────────────────────────────────────┘   │
└──────────────┬──────────────────┬─────────────────┬──────────────┘
               │                  │                 │
        HTTPS  │                  │                 │ HTTPS
               ▼                  ▼                 ▼
    ┌──────────────────┐  ┌────────────────┐  ┌──────────────────┐
    │   SUPABASE       │  │   OPENAI       │  │   BREVO SMTP     │
    │   (Database)     │  │   (AI/Chat)    │  │   (Email)        │
    │                  │  │                │  │                  │
    │ ├─ PostgreSQL    │  │ ├─ GPT-4       │  │ ├─ API REST      │
    │ ├─ Storage       │  │ ├─ Embeddings  │  │ └─ SMTP Gateway  │
    │ ├─ Auth (RLS)    │  │ └─ Rate limit  │  │                  │
    │ └─ Realtime      │  │                │  │ Rate: 300 email/ │
    │                  │  │ Rate: 90k TPM │  │ giorno (upgrade) │
    └──────────────────┘  └────────────────┘  └──────────────────┘
```

### Flusso Dati (Deep Dive)

#### **Flow: Upload Fattura → Categorizzazione → Dashboard**

```
STEP 1: UPLOAD
┌────────────────┐
│ Ristoratore    │
│ Carica fattura │
│ (PDF/XML)      │
└────────┬───────┘
         │ File bytes → Streamlit
         ▼
    ┌──────────────────────────────────┐
    │ app.py: carica_file_e_processa() │
    │                                  │
    │ PDF?                             │
    │ ├─ PyMuPDF: estrae testo        │
    │ ├─ Regex parsing                │
    │ └─ Fallback OCR su immagini      │
    │                                  │
    │ XML?                             │
    │ ├─ xmltodict: parse → dict      │
    │ └─ Flattening righe             │
    │                                  │
    │ Output: DataFrame 50 righe       │
    │ Colonne: descrizione, qtà, prezzo│
    └──────────┬───────────────────────┘
               │ DataFrame
               ▼
    ┌──────────────────────────────────┐
    │ Supabase Storage upload          │
    │ Percorso: users/{user_id}/{file} │
    └──────────┬───────────────────────┘
               │ Conferma salvataggio
               ▼
    ┌──────────────────────────────────┐
    │ app.py: categorizza_batch_ai()   │
    │                                  │
    │ Crea PROMPT (2000 token):        │
    │ ├─ System: Ti sei il bot         │
    │ ├─ Memory globale: 50+ esempi   │
    │ ├─ Memory utente: 20 esempi     │
    │ ├─ Righe fattura: 50 descrizioni│
    │ └─ JSON format request           │
    │                                  │
    │ Batch splitting:                 │
    │ ├─ Se >12k token → split        │
    │ ├─ Max 5 righe per batch        │
    │ └─ Sequenziale (non parallelo)  │
    │                                  │
    │ Retry logic:                     │
    │ ├─ Max 3 tentativi              │
    │ ├─ tenacity @retry decorator    │
    │ ├─ Backoff esponenziale         │
    │ └─ Log su file/stdout           │
    └──────────┬───────────────────────┘
               │ API call
               ▼
         ╔════════════════╗
         ║  OPENAI GPT-4  ║
         ║   API $$ COST  ║
         ║                ║
         ║  10k token in  ║
         ║  4k token out  ║
         ║  (stimato)     ║
         ║                ║
         ║  = ~€0.05      ║
         ║  per fattura   ║
         ╚════════┬═══════╝
                  │ JSON response
                  ▼
    ┌──────────────────────────────────┐
    │ app.py: processa_risposta_ai()   │
    │                                  │
    │ Parsing risposta:                │
    │ {                                │
    │   "articoli": [                  │
    │     {                            │
    │       "descrizione": "...",      │
    │       "categoria": "PESCE",      │
    │       "confidence": 0.94,        │
    │       "note": "..."              │
    │     }                            │
    │   ]                              │
    │ }                                │
    │                                  │
    │ Validazione:                     │
    │ ├─ Confidence < 70%? → Flag     │
    │ ├─ Categoria sconosciuta?       │
    │ └─ Prezzo anomalo?              │
    │                                  │
    │ Calcolo anomalie:               │
    │ ├─ Z-score vs storico           │
    │ ├─ Deviazione std >2.5?         │
    │ └─ Flag anomalo                 │
    └──────────┬───────────────────────┘
               │ DataFrame validato
               ▼
    ┌──────────────────────────────────┐
    │ Supabase: save fatture table     │
    │                                  │
    │ INSERT INTO fatture (             │
    │   user_id,                        │
    │   numero_fattura,                │
    │   fornitore,                      │
    │   data_fattura,                   │
    │   items: [                        │
    │     {                             │
    │       descrizione_norm,           │
    │       categoria,                  │
    │       quantita,                   │
    │       prezzo_unitario,            │
    │       confidence                  │
    │     }                             │
    │   ]                               │
    │ )                                 │
    └──────────┬───────────────────────┘
               │ Conferma INSERT
               ▼
    ┌──────────────────────────────────┐
    │ Supabase: update memory globale  │
    │ (prodotti_master)                │
    │                                  │
    │ Per ogni articolo:               │
    │ ├─ Lookup: esiste già?           │
    │ ├─ SI: incrementa contatore      │
    │ └─ NO: INSERT nuovo              │
    │                                  │
    │ UPSERT prodotti_master (         │
    │   descrizione_norm,              │
    │   categoria,                      │
    │   contatore_utilizzo++,          │
    │   updated_at = NOW()             │
    │ )                                 │
    └──────────┬───────────────────────┘
               │ Memory aggiornata
               ▼
    ┌──────────────────────────────────┐
    │ ALERT: Check anomalie prezzi    │
    │                                  │
    │ Per ogni articolo:               │
    │ 1. Calcola media storica         │
    │ 2. Calcola std dev               │
    │ 3. Z-score = (prezzo - media)/std│
    │ 4. Se |z-score| > 2.5:           │
    │    ├─ INSERT alert table         │
    │    └─ Accoda email               │
    │                                  │
    │ Alert: "BURRO +50% vs media"     │
    └──────────┬───────────────────────┘
               │ Alert creato
               ▼
    ┌──────────────────────────────────┐
    │ Email notification (Brevo)       │
    │                                  │
    │ TO: ristoratore@gmail.com        │
    │ SUBJECT: ⚠️ Alert anomalia       │
    │ BODY:                            │
    │  "Articolo: BURRO 500g           │
    │   Prezzo: €18.50                 │
    │   Storico: €12 (media)           │
    │   Variazione: +50%               │
    │   Azione: Contatta fornitore"    │
    │                                  │
    │ Rate: 1 email per alert          │
    │       (Max 5 alert/giorno)       │
    └──────────┬───────────────────────┘
               │ Email inviata
               ▼
    ┌──────────────────────────────────┐
    │ DASHBOARD REFRESH                │
    │                                  │
    │ UI mostra:                       │
    │ ├─ Tabella fatture (nuova riga)  │
    │ ├─ Grafico trend prezzi(updated) │
    │ ├─ Alert rosso evidenziato       │
    │ └─ Statistiche refresh            │
    │                                  │
    │ Cache Streamlit:                 │
    │ ├─ @st.cache_data(ttl=300)      │
    │ ├─ Memoria AI (5 min TTL)       │
    │ └─ Next refresh: auto 5 min     │
    └──────────────────────────────────┘
```

---

## 5️⃣ STACK TECNOLOGICO

### Frontend (Client)

| Component | Technology | Version | Uso |
|-----------|-----------|---------|-----|
| **UI Framework** | Streamlit | ≥1.28.0 | Widget UI, routing, session state |
| **Rendering** | Browser (HTML5/CSS/JS) | Modern | Multi-platform (desktop/mobile) |
| **Dataframe Viewer** | Streamlit st.dataframe | Native | Tabelle sortabili/filtrabili |
| **Charts** | Plotly | ≥5.17.0 | Interattive (zoom, hover, export) |
| **Components Avanzati** | extra-streamlit-components | ≥0.1.60 | Custom tabs, carousels, ecc |
| **File Uploader** | Streamlit st.file_uploader | Native | Multi-format (PDF/XML) |

### Backend (Server)

| Component | Technology | Version | Uso |
|-----------|-----------|---------|-----|
| **Runtime** | Python | 3.9+ | Linguaggio principale |
| **Web Server** | Streamlit Runtime | ≥1.28.0 | HTTP server + WebSocket |
| **Deployment** | Streamlit Cloud | Managed | PaaS (no Docker/Kubernetes) |
| **Process Management** | Built-in Streamlit | Auto | Auto-reload on code change |

### Database & Storage

| Component | Technology | Details |
|-----------|-----------|---------|
| **Primary DB** | PostgreSQL (Supabase) | 5GB free, scalable |
| **Authentication** | Supabase Auth + Argon2 | Row-Level Security (RLS) |
| **File Storage** | Supabase Storage | S3-like bucket |
| **Realtime Updates** | Supabase Realtime | WebSocket per live sync |
| **Connection Pooling** | Python-Supabase SDK | Built-in connpool |

### AI & ML

| Component | Technology | Model | Uso |
|-----------|-----------|--------|-----|
| **LLM** | OpenAI API | GPT-4 | Categorizzazione, prompting |
| **Token Counting** | tiktoken | Auto | Stima costi pre-API |
| **Retry Logic** | tenacity | ≥8.2.3 | Fallback robusto |
| **Memory Management** | JSON + Prompt | Custom | Memoria AI persistente |

### Email

| Component | Technology | Provider | Quota |
|-----------|-----------|----------|-------|
| **Email Service** | Brevo API | sib-api-v3-sdk ≥7.6.0 | 300 email/giorno (free) |
| **SMTP Gateway** | Brevo SMTP | SSL/TLS | 1000 email/day (premium) |

### Data Processing

| Library | Version | Uso |
|---------|---------|-----|
| **Pandas** | ≥2.0.0 | DataFrame manipulation |
| **NumPy** | (via Pandas) | Numeric operations |
| **OpenPyXL** | ≥3.1.0 | Excel read/write |
| **PyMuPDF** | ≥1.23.0 | PDF parsing + OCR fallback |
| **xmltodict** | ≥0.13.0 | XML → dict parsing |
| **Pillow** | ≥10.0.0 | Image processing (PDF page render) |

### Configuration & Secrets

| Component | Technology | Uso |
|-----------|-----------|-----|
| **Config Files** | TOML | .streamlit/config.toml |
| **Secrets Management** | Streamlit Secrets + ENV | .streamlit/secrets.toml + cloud upload |
| **TOML Parser** | toml ≥0.10.2 | Parse config files |

### Security

| Component | Technology | Algoritmo |
|-----------|-----------|-----------|
| **Password Hashing** | argon2-cffi ≥23.1.0 | Argon2id (m=65536, t=3, p=4) |
| **Session Management** | Streamlit st.session_state | In-memory per utente |
| **HTTPS** | Browser + Streamlit Cloud | TLS 1.2+ |
| **API Rate Limiting** | OpenAI + custom | 90k TPM, retry on 429 |

### Monitoring & Logging

| Component | Technology | Storage |
|-----------|-----------|---------|
| **Logging** | Python logging | File local (debug.log) + stdout (cloud) |
| **Rotating Files** | RotatingFileHandler | 5MB per file, 5 backups |
| **Cloud Logs** | Streamlit Cloud UI | Retention 30 giorni |
| **Error Tracking** | (TODO) | Sentry.io per produzione |

### Version Management

| Item | Current | Management |
|------|---------|------------|
| **Python** | 3.9+ | Streamlit Cloud auto |
| **Pip Dependencies** | Vedi requirements.txt | Manual pin a versioni |
| **Database Schema** | v3.2 | SQL migrations manuali |
| **API OpenAI** | GPT-4 (model: gpt-4) | Auto-updated by provider |

### Dependencies Summary (requirements.txt)

```
streamlit>=1.28.0              # UI framework
pandas>=2.0.0                  # DataFrames
plotly>=5.17.0                 # Interactive charts
supabase>=2.0.0                # Database client
openpyxl>=3.1.0                # Excel I/O
toml>=0.10.2                   # Config parsing
argon2-cffi>=23.1.0            # Password hashing
sib-api-v3-sdk>=7.6.0          # Brevo email API
openai>=1.3.0                  # GPT-4 API
xmltodict>=0.13.0              # XML parsing
extra-streamlit-components>=0.1.60  # Advanced components
PyMuPDF>=1.23.0                # PDF parsing
Pillow>=10.0.0                 # Image processing
requests>=2.31.0               # HTTP library
tenacity>=8.2.3                # Retry decorators (NEW!)
```

⚠️ **IMPORTANTE:** `tenacity` era MANCANTE e usato nel codice (riga 18 app.py)

---

## 6️⃣ DATABASE & SCHEMA

### Architettura Supabase

```
PROGETTO SUPABASE
├─ Auth (Managed by Supabase)
├─ PostgreSQL Database
│  ├─ Public Schema
│  │  ├─ users (authentication)
│  │  ├─ fatture (invoices)
│  │  ├─ prodotti_master (global AI memory)
│  │  ├─ prodotti_utente (user history)
│  │  ├─ classificazioni_manuali (admin overrides)
│  │  ├─ categorie (dynamic categories)
│  │  ├─ alert_prezzi (price anomalies)
│  │  ├─ review_items (low confidence items)
│  │  └─ upload_events (audit log)
│  │
│  └─ Security
│     ├─ RLS (Row Level Security) ✅ IMPLEMENTATO
│     │  ├─ users: Utente vede solo se id = auth.uid()
│     │  ├─ fatture: User vede se user_id = auth.uid()
│     │  └─ admin: Can read all if role = 'admin'
│     │
│     └─ Roles
│        ├─ authenticated: login required
│        └─ anon: no login (upload_events logs)
│
├─ Storage (S3-like)
│  ├─ /users/{user_id}/
│  │  ├─ {file_uuid}_original.pdf
│  │  ├─ {file_uuid}_original.xml
│  │  └─ {file_uuid}_parsed.json
│  │
│  └─ /temp/
│     ├─ {session_id}_memory.json
│     └─ {session_id}_export.xlsx
│
└─ Realtime (WebSocket)
   ├─ Subscriptions: fatture:INSERT
   └─ Subscriptions: alert_prezzi:UPDATE
```

### Schema Dettagliato

#### **Tabella: users**
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Authentication
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,  -- Argon2 hash
  password_hash_algo TEXT DEFAULT 'argon2',
  
  -- Profile
  nome_ristorante TEXT,
  città TEXT,
  provincia TEXT,
  partita_iva TEXT,
  
  -- Authorization
  ruolo ENUM('ristoratore', 'admin') DEFAULT 'ristoratore',
  piano ENUM('free', 'premium', 'enterprise') DEFAULT 'free',
  
  -- Status
  attivo BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  last_login TIMESTAMP,
  
  -- Audit
  reset_token TEXT,  -- Per password reset
  reset_token_expires TIMESTAMP,
  
  CONSTRAINT email_format CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$')
);

-- RLS Policy
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read own row" ON users
  FOR SELECT USING (auth.uid() = id OR (
    SELECT ruolo FROM users WHERE id = auth.uid()
  ) = 'admin');

CREATE POLICY "Users can update own row" ON users
  FOR UPDATE USING (auth.uid() = id);
```

**Indici:**
```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_ruolo ON users(ruolo);
CREATE INDEX idx_users_attivo ON users(attivo);
```

---

#### **Tabella: fatture**
```sql
CREATE TABLE fatture (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Foreign Key
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Invoice Info
  numero_fattura TEXT NOT NULL,  -- Es: "INV-2026-00123"
  data_fattura DATE NOT NULL,
  fornitore TEXT NOT NULL,  -- Es: "Sysco Italia"
  
  -- File Reference
  file_uuid UUID,  -- Per recuperare da Storage
  file_format ENUM('xml', 'pdf', 'manual') DEFAULT 'xml',
  file_size_bytes INTEGER,
  
  -- Line Items (stored as JSONB array)
  items JSONB NOT NULL,  -- Array of:
  -- [
  --   {
  --     "riga_id": 1,
  --     "descrizione_originale": "Filetto di Branzino 500g",
  --     "descrizione_norm": "FILETTO BRANZINO",
  --     "categoria": "PESCE FRESCO",
  --     "categoria_confidence": 0.94,
  --     "quantita": 5.0,
  --     "unita_misura": "kg",
  --     "prezzo_unitario": 8.50,
  --     "totale_riga": 42.50,
  --     "ai_flagged": false,
  --     "anomalia_prezzo": false,
  --     "timestamp_elaborazione": "2026-01-06T15:30:00Z"
  --   }
  -- ]
  
  -- Totals
  totale_fattura NUMERIC(10, 2),
  
  -- Processing Status
  status ENUM('caricato', 'elaborazione', 'completato', 'errore') DEFAULT 'caricato',
  errore_messaggio TEXT,
  
  -- Audit
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  elaborato_at TIMESTAMP,
  
  CONSTRAINT user_numero_unique UNIQUE(user_id, numero_fattura)
);

-- RLS Policy
ALTER TABLE fatture ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users see own invoices" ON fatture
  FOR SELECT USING (
    auth.uid() = user_id OR 
    (SELECT ruolo FROM users WHERE id = auth.uid()) = 'admin'
  );
```

**Indici:**
```sql
CREATE INDEX idx_fatture_user_id ON fatture(user_id);
CREATE INDEX idx_fatture_data ON fatture(data_fattura DESC);
CREATE INDEX idx_fatture_fornitore ON fatture(fornitore);
CREATE INDEX idx_fatture_status ON fatture(status);
```

---

#### **Tabella: prodotti_master (Global AI Memory)**
```sql
CREATE TABLE prodotti_master (
  id SERIAL PRIMARY KEY,
  
  -- Product Identification
  descrizione_norm TEXT UNIQUE NOT NULL,  -- "FILETTO BRANZINO"
  categoria TEXT NOT NULL,  -- "PESCE FRESCO"
  
  -- AI Memory
  contatore_utilizzo INTEGER DEFAULT 1,  -- Quante volte visto
  ultima_categoria_assegnata TEXT,
  
  -- Statistics
  prezzo_min NUMERIC(10, 2),
  prezzo_max NUMERIC(10, 2),
  prezzo_medio NUMERIC(10, 2),
  
  -- Metadata
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  CONSTRAINT categoria_valid CHECK (categoria IN (
    'FRUTTA VERDURA', 'PESCE FRESCO', 'CARNI ROSSE', 
    'POLLAME', 'FORMAGGI LATTICINI', 'PASTA RISO CEREALI',
    'CONDIMENTI SPEZIE', 'BEVANDE ALCOLICHE', 'BEVANDE NON ALCOLICHE',
    'MATERIALE CONSUMABILE', 'ALTRO'
  ))
);

-- Questo è il "brain" dell'AI - memory globale
-- Quando nuovi articoli arrivano, migliora la categorizzazione
```

**Indici:**
```sql
CREATE INDEX idx_prodotti_categoria ON prodotti_master(categoria);
CREATE INDEX idx_prodotti_contatore ON prodotti_master(contatore_utilizzo DESC);
CREATE UNIQUE INDEX idx_prodotti_descrizione ON prodotti_master(descrizione_norm);
```

---

#### **Tabella: prodotti_utente (Local Memory)**
```sql
CREATE TABLE prodotti_utente (
  id SERIAL PRIMARY KEY,
  
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  descrizione_norm TEXT NOT NULL,
  categoria TEXT NOT NULL,
  
  -- User-specific stats
  contatore_utilizzo INTEGER DEFAULT 1,
  ultima_data_acquisto DATE,
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  CONSTRAINT user_prod_unique UNIQUE(user_id, descrizione_norm)
);

-- Per accelerare categorizzazione futura di questo ristoratore
```

---

#### **Tabella: classificazioni_manuali (Admin Overrides)**
```sql
CREATE TABLE classificazioni_manuali (
  id SERIAL PRIMARY KEY,
  
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  descrizione_norm TEXT NOT NULL,
  categoria_corretta TEXT NOT NULL,
  
  -- Admin Info
  approvato_da TEXT,  -- Email admin
  motivo_correzione TEXT,  -- "Errore AI", "Categoria nuova", ...
  
  -- Priority
  priorita INTEGER DEFAULT 100,  -- Higher = take precedence
  
  created_at TIMESTAMP DEFAULT NOW(),
  
  CONSTRAINT user_desc_unique UNIQUE(user_id, descrizione_norm)
);

-- Massima priorità: se qui, ignora AI memory
-- Usato quando admin corregge errori ricorrenti
```

---

#### **Tabella: alert_prezzi**
```sql
CREATE TABLE alert_prezzi (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  fattura_id UUID NOT NULL REFERENCES fatture(id) ON DELETE CASCADE,
  
  -- Product Info
  descrizione_prod TEXT,
  categoria TEXT,
  
  -- Price Data
  prezzo_attuale NUMERIC(10, 2),
  prezzo_medio_storico NUMERIC(10, 2),
  variazione_percentuale NUMERIC(5, 2),  -- +50.5%
  z_score NUMERIC(5, 2),  -- Statistical deviation
  
  -- Alert Classification
  tipo ENUM('aumento', 'diminuzione', 'trend') DEFAULT 'aumento',
  severita ENUM('bassa', 'media', 'alta', 'critica') DEFAULT 'media',
  
  -- Notification
  email_inviata BOOLEAN DEFAULT false,
  email_inviata_at TIMESTAMP,
  notificato_user BOOLEAN DEFAULT false,
  
  -- Resolution
  risolto BOOLEAN DEFAULT false,
  azione_utente TEXT,  -- "Negoziato sconto", "Cambio fornitore"
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Alert >= 2.5 std dev, notifica email
```

---

#### **Tabella: review_items**
```sql
CREATE TABLE review_items (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  fattura_id UUID NOT NULL REFERENCES fatture(id) ON DELETE CASCADE,
  
  riga_numero INTEGER,
  descrizione_originale TEXT,
  descrizione_norm TEXT,
  categoria_suggerita TEXT,
  confidence NUMERIC(3, 2),  -- 0.45
  
  -- Admin Review
  revisionato BOOLEAN DEFAULT false,
  categoria_approvata TEXT,
  note_admin TEXT,
  revisionato_da TEXT,  -- Admin email
  revisionato_at TIMESTAMP,
  
  created_at TIMESTAMP DEFAULT NOW()
);

-- Tutti i < 70% confidence vanno qui per review umano
```

---

#### **Tabella: upload_events (Audit Log)**
```sql
CREATE TABLE upload_events (
  id SERIAL PRIMARY KEY,
  
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  azione ENUM('upload', 'categorizzazione', 'approvazione', 'export'),
  
  dettagli JSONB,  -- {file: "...", righe: 50, tempo_ms: 1234}
  
  timestamp TIMESTAMP DEFAULT NOW(),
  ip_address INET,
  user_agent TEXT
);

-- Per audit trail e troubleshooting
```

---

### Query Critiche Frequenti

**Q1: Carica dataframe utente con tutte le fatture**
```python
# app.py riga 2913
response = supabase.table("fatture") \
  .select("*") \
  .eq("user_id", user_id) \
  .order("data_fattura", desc=True) \
  .execute()

df = pd.DataFrame(response.data)
# PROBLEMA: Carica TUTTE le righe (scalability issue con 10k+ fatture)
# TODO: Aggiungere .limit(1000) per paginazione
```

**Q2: Load AI memory globale**
```python
# app.py riga 2312
response = supabase.table("prodotti_master") \
  .select("descrizione_norm, categoria, contatore_utilizzo") \
  .order("contatore_utilizzo", desc=True) \
  .limit(2500) \
  .execute()

ai_memory = response.data
# Usato in prompt per categorizzazione
```

**Q3: Cerca anomalie prezzo**
```python
# Calcolato nel codice (non SQL)
for articolo in fattura_items:
  storico = supabase.table("fatture") \
    .select("items->>prezzo_unitario") \
    .eq("user_id", user_id) \
    .gte("data_fattura", 90_giorni_fa) \
    .execute()
  
  # Calcola z-score
  media = mean(storico)
  std = stdev(storico)
  z = (prezzo_attuale - media) / std
  
  if abs(z) > 2.5:
    # Crea alert
```

---

## 7️⃣ API & INTEGRAZIONI

### OpenAI GPT-4

**Endpoint:** `POST https://api.openai.com/v1/chat/completions`

**Authentication:** Header `Authorization: Bearer sk-proj-...`

**Request Structure:**
```python
import openai
from tenacity import retry, stop_after_attempt

@retry(stop=stop_after_attempt(3))
def categorizza_articoli(descrizioni: list, memoria_ai: list) -> dict:
    """
    Args:
        descrizioni: List[str] degli articoli da categorizzare
        memoria_ai: List[dict] con esempi storici
    
    Returns:
        dict con categorizzazioni e confidence
    """
    
    system_prompt = """Tu sei un esperto di food cost management per ristoranti.
    Categorizza gli ingredienti in una delle seguenti categorie:
    - FRUTTA VERDURA
    - PESCE FRESCO
    - CARNI ROSSE
    - POLLAME
    - FORMAGGI LATTICINI
    - PASTA RISO CEREALI
    - CONDIMENTI SPEZIE
    - BEVANDE ALCOLICHE
    - BEVANDE NON ALCOLICHE
    - MATERIALE CONSUMABILE
    - ALTRO
    
    Rispondi SOLO in JSON valido.
    """
    
    memory_examples = "\n".join([
        f"- {m['descrizione_norm']} → {m['categoria']}"
        for m in memoria_ai[:50]
    ])
    
    user_prompt = f"""
    Ecco i prodotti da categorizzare:
    {'\n'.join(descrizioni)}
    
    Esempi da memoria globale:
    {memory_examples}
    
    Rispondi in JSON:
    {{
        "articoli": [
            {{
                "descrizione": "...",
                "categoria": "...",
                "confidence": 0.95,
                "note": "..."
            }}
        ]
    }}
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        temperature=0.2,  # Bassa per consistenza
        max_tokens=2000,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        timeout=60  # Timeout dinamico
    )
    
    result = response.choices[0].message.content
    return json.loads(result)
```

**Rate Limits:**
- 90,000 TPM (tokens per minute)
- Quota: ~3,000 fatture/mese su budget
- Retry: 3 tentativi con backoff esponenziale

**Costi:**
- Input: $0.03 per 1k token (gpt-4)
- Output: $0.06 per 1k token (gpt-4)
- Stima: €0.02-0.05 per fattura

---

### Brevo Email API

**Provider:** Sendinblue (rinominato Brevo)

**Endpoint:** `https://api.brevo.com/v3/smtp/email`

**Authentication:** Header `api-key: xkeysib-...`

**Request Example:**
```python
from sib_api_v3_sdk import SendSmtpEmail

def invia_alert_anomalia(email_utente, articolo, prezzo_attuale, prezzo_medio):
    """Invia email con alert anomalia prezzo"""
    
    email = SendSmtpEmail(
        to=[{"email": email_utente}],
        from_email="alerts@checkfornitori.it",
        from_name="Check Fornitori AI",
        subject=f"⚠️ ALERT: {articolo} aumentato!",
        html_content=f"""
        <h2>Anomalia Prezzo Rilevata</h2>
        <p><strong>Articolo:</strong> {articolo}</p>
        <p><strong>Prezzo attuale:</strong> €{prezzo_attuale:.2f}</p>
        <p><strong>Prezzo medio:</strong> €{prezzo_medio:.2f}</p>
        <p><strong>Variazione:</strong> +{((prezzo_attuale-prezzo_medio)/prezzo_medio*100):.1f}%</p>
        <p>
            <a href="https://app.checkfornitori.it/dashboard">
                Visualizza dettagli
            </a>
        </p>
        """
    )
    
    api_instance = SendersApi(api_client)
    response = api_instance.send_transac_email(email)
    return response
```

**Limiti:**
- Free: 300 email/giorno
- Premium: 1,000 email/giorno
- Rate limit: Non specificato (burst allowed)

---

### Supabase REST API

**Endpoint:** `https://{project_id}.supabase.co/rest/v1/`

**Authentication:** `Authorization: Bearer {API_KEY}` o `apikey: {ANON_KEY}`

**Examples:**

```python
from supabase import create_client, Client

# Init client (cached with @st.cache_resource)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# SELECT
response = supabase \
    .table("fatture") \
    .select("*, users(nome_ristorante)") \
    .eq("user_id", "uuid-123") \
    .gte("data_fattura", "2026-01-01") \
    .limit(100) \
    .execute()

# INSERT
response = supabase \
    .table("fatture") \
    .insert({
        "user_id": "uuid-123",
        "numero_fattura": "INV-001",
        "fornitore": "Sysco",
        "data_fattura": "2026-01-06",
        "items": [...],
        "totale_fattura": 1250.50
    }) \
    .execute()

# UPSERT (insert or update)
response = supabase \
    .table("prodotti_master") \
    .upsert({
        "descrizione_norm": "FILETTO BRANZINO",
        "categoria": "PESCE FRESCO",
        "contatore_utilizzo": 5
    }) \
    .execute()

# UPDATE
response = supabase \
    .table("fatture") \
    .update({"status": "completato"}) \
    .eq("id", "fattura-uuid") \
    .execute()

# DELETE
response = supabase \
    .table("alert_prezzi") \
    .delete() \
    .eq("id", "alert-uuid") \
    .execute()
```

**Rate Limits:**
- Unlimited (PostgreSQL connections managed by Supabase)
- Per-project: Connection pool ~10 connections (free tier)

---

## 8️⃣ SICUREZZA & MULTI-TENANCY

### Autenticazione

**Flow Login:**
```
1. Utente inserisce email/password
2. Password non viene salvata client
3. Hash Argon2 calcolato server (app.py riga ~1700)
   - m=65536 (memory cost)
   - t=3 (time cost)
   - p=4 (parallelism)
4. Confronto: hash_inserito == hash_db
5. Se OK: Crea sessione Streamlit
6. Cookie: st.session_state.logged_in = True
7. Cookie: st.session_state.user_id = UUID
8. TTL: 30 giorni (configurabile)
```

**Password Reset Flow:**
```
1. Utente clicca "Forgot Password"
2. Inserisce email
3. Sistema genera UUID random (reset_token)
4. Salva in DB con TTL 1 ora
5. Email: "Click qui per reset: {reset_link}?token={uuid}"
6. Utente clicca link (cambio_password.py)
7. Inserisce nuova password
8. Token validato e consumato
9. Password aggiornata in DB
```

**Migrazione Hash Automatica:**
```python
# app.py riga ~1750
def verifica_password(email: str, password_inserita: str) -> bool:
    user = supabase.table("users") \
        .select("password_hash, password_hash_algo") \
        .eq("email", email) \
        .single() \
        .execute()
    
    hash_salvato = user.data["password_hash"]
    algo = user.data.get("password_hash_algo", "sha256")
    
    if algo == "sha256":
        # Vecchio hash SHA256
        hash_calcolato = hashlib.sha256(password_inserita.encode()).hexdigest()
        if hash_calcolato == hash_salvato:
            # Migra a Argon2
            hash_argon2 = argon2.hash_password(password_inserita.encode())
            supabase.table("users") \
                .update({
                    "password_hash": hash_argon2,
                    "password_hash_algo": "argon2"
                }) \
                .eq("email", email) \
                .execute()
            return True
    
    elif algo == "argon2":
        # Verifica Argon2
        return argon2.verify(hash_salvato, password_inserita.encode())
    
    return False
```

---

### Multi-tenancy

**Principio: Row-Level Security (RLS)**

Ogni ristoratore vede SOLO i propri dati.

**Implementazione:**
```sql
-- RLS Policy su fatture
CREATE POLICY "Users see own invoices" ON fatture
  FOR SELECT USING (
    auth.uid() = user_id  -- Puoi leggere se ID corrisponde
    OR 
    (SELECT ruolo FROM users WHERE id = auth.uid()) = 'admin'  -- O sei admin
  );

-- Simile per tutti le altre tabelle:
-- alert_prezzi, prodotti_utente, review_items
```

**Verifica nel codice:**
```python
# app.py: Dopo login, salva user_id in session
st.session_state.user_id = user_uuid

# Poi, tutte le query filtrano:
response = supabase.table("fatture") \
    .select("*") \
    .eq("user_id", st.session_state.user_id)  # ← Multi-tenancy!
    .execute()
```

**Protezione:**
- ✅ Utente A non può vedere fatture utente B (RLS)
- ✅ SQL Injection prevenuto (Supabase SDK usa prepared statements)
- ✅ Admin può bypassare RLS (ruolo DB)

---

### Admin Panel Access Control

**Verifica Hardcoded:**
```python
# admin.py riga 104
ADMIN_EMAILS = ["mattiadavolio90@gmail.com"]

def check_admin_access():
    if st.session_state.get("user_email") not in ADMIN_EMAILS:
        st.error("❌ Accesso negato")
        st.stop()
```

⚠️ **PROBLEMA:** Email admin duplicata in 2 file (app.py e admin.py)
- Se cambio email, devo fare 2 edit
- Rischio desync

📋 **TODO:** Centralizzare in secrets.toml
```toml
[app]
admin_emails = ["mattiadavolio90@gmail.com", "altro@admin.it"]
```

---

### CSRF & XSS Protection

**CSRF:**
- ✅ Streamlit Cloud ha `enableXsrfProtection = true` (config.toml)
- ✅ Cookie SameSite=Lax auto

**XSS:**
- ✅ Streamlit escapa HTML per default in st.write()
- ✅ User input in DataFrame non eseguito
- ⚠️ Rischio in str() di valori user (mitigato da parametri prepared)

**Injection SQL:**
- ✅ Supabase SDK usa prepared statements
- ✅ No query building dinamico

---

### Dati Sensibili

**Secrets management:**
```python
# app.py riga 1596-1597
try:
    supabase_url = st.secrets["supabase"]["url"]
    supabase_key = st.secrets["supabase"]["key"]
    api_key = st.secrets["OPENAI_API_KEY"]
except KeyError:
    st.error("❌ Secrets mancanti")
    st.stop()
```

**Quando deployare su Streamlit Cloud:**
1. ❌ **NON** committare `.streamlit/secrets.toml` su GitHub
2. ✅ **CREARE** `.gitignore` con `secrets.toml`
3. ✅ **CARICARE** secrets nell'UI Streamlit Cloud
4. ✅ **VERIFICARE** `git log` che non siano già committati

---

## 9️⃣ PERFORMANCE & OPTIMIZATION

### Cache Strategy

| Cache | TTL | Scope | Dove |
|-------|-----|-------|------|
| **categorie DB** | 600s (10 min) | Per app instance | app.py riga 2119 `@st.cache_data` |
| **AI memory** | 300s (5 min) | Per app instance | app.py riga 2312 `@st.cache_data` |
| **User dataframe** | None (infinito) | Per session | app.py riga 2913 `@st.cache_data` |
| **Alert prezzi** | None | Per session | app.py riga 3688 `@st.cache_data` |
| **Pivot mensile** | None | Per session | app.py riga 3920 `@st.cache_data` |
| **Supabase client** | ∞ (resource) | Per app instance | admin.py riga 57 `@st.cache_resource` |

**Problemi di Cache:**
```python
# ⚠️ app.py riga 2913: Cache infinito
@st.cache_data(ttl=None)
def carica_e_prepara_dataframe(user_id):
    response = supabase.table("fatture") \
        .select("*") \
        .eq("user_id", user_id) \
        .execute()
    return pd.DataFrame(response.data)

# PROBLEMA: Se utente carica nuova fattura, non la vede
# SOLUZIONE: TTL=300 (refresh ogni 5 min) o manuale invalidate
```

---

### Query Optimization

**Problema: N+1 queries**
```python
# ❌ INEFFICIENTE
fatture = supabase.table("fatture") \
    .select("*") \
    .eq("user_id", user_id) \
    .execute()

for fattura in fatture.data:
    # Query 1: JOIN users → nome ristorante
    # Query 2: JOIN prodotti_master per categoria
    # ... N query extra!

# ✅ EFFICIENTE (con select join)
fatture = supabase.table("fatture") \
    .select("*, users(nome_ristorante), prodotti_master(categoria)") \
    .eq("user_id", user_id) \
    .execute()
```

**Problema: No paginazione su dataset large**
```python
# ❌ Se utente ha 50,000 fatture → carica TUTTE
response = supabase.table("fatture") \
    .select("*") \
    .eq("user_id", user_id) \
    .execute()  # 50k row, 100MB RAM!

# ✅ SOLUZIONE: Paginazione
response = supabase.table("fatture") \
    .select("*") \
    .eq("user_id", user_id) \
    .order("data_fattura", desc=True) \
    .limit(1000)  # Prime 1000
    .offset(0)    # Offset per pagina successiva
    .execute()
```

📋 **TODO:** Implementare paginazione UI con Streamlit

---

### OpenAI Token Management

**Token counting prima di API call:**
```python
import tiktoken

def stima_costo_categorizzazione(descrizioni: list, memoria_ai: list) -> dict:
    encoding = tiktoken.encoding_for_model("gpt-4")
    
    # Costruisci prompt
    prompt = f"... {descrizioni} ... {memoria_ai}"
    tokens_input = len(encoding.encode(prompt))
    
    # Stima output (tipicamente 20% input)
    tokens_output_stima = int(tokens_input * 0.2)
    
    # Costo
    costo_input = (tokens_input / 1000) * 0.03
    costo_output = (tokens_output_stima / 1000) * 0.06
    costo_totale = costo_input + costo_output
    
    return {
        "tokens_input": tokens_input,
        "tokens_output_stima": tokens_output_stima,
        "costo_eur": costo_totale,
        "dentro_quota": costo_totale < 0.10  # Allarme se >€0.10
    }
```

**Batch Splitting:**
```python
def categorizza_batch_split(descrizioni: list, max_tokens=12000):
    """Divide descrizioni in batch se > max_tokens"""
    
    batch_size = 5  # Descrizioni per batch
    batches = [
        descrizioni[i:i+batch_size]
        for i in range(0, len(descrizioni), batch_size)
    ]
    
    risultati = []
    for batch in batches:
        # Stima token
        costo = stima_costo_categorizzazione(batch, memoria_ai)
        
        if costo["tokens_input"] > max_tokens:
            logger.warning(f"Batch {batch} > {max_tokens} token!")
            continue
        
        # Call API
        result = categorizza_articoli(batch, memoria_ai)
        risultati.extend(result["articoli"])
        
        time.sleep(0.5)  # Rate limit
    
    return risultati
```

---

### Logging & Monitoring

**Current Implementation:**
```python
# app.py riga 1587 (PROBLEMA CLOUD)
from logging.handlers import RotatingFileHandler

logger = logging.getLogger('fci_app')
handler = RotatingFileHandler('debug.log', maxBytes=5_000_000, backupCount=5)
```

**Problema:** File system read-only su Streamlit Cloud

**Soluzione Implementata:**
```python
# NEW: Fallback cloud-compatible (riga 1587)
import sys

logger = logging.getLogger('fci_app')
if not logger.handlers:
    try:
        # Try local file (development)
        from logging.handlers import RotatingFileHandler
        handler = RotatingFileHandler(
            'debug.log', 
            maxBytes=5_000_000, 
            backupCount=5, 
            encoding='utf-8'
        )
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.info("✅ File logging active")
    except (OSError, PermissionError) as e:
        # Fallback: stdout (cloud mode)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)  # INFO instead of DEBUG
        logger.info("✅ Stdout logging active (cloud mode)")
```

**Log Levels:**
- `DEBUG`: Info dettagliata (token count, API payload)
- `INFO`: Operazioni importanti (categorizzazione completata)
- `WARNING`: Problemi non bloccanti (confidence bassa)
- `ERROR`: Errori (API fail, DB error)
- `CRITICAL`: App non funziona (secrets mancanti)

---

## 🔟 INFRASTRUTTURA CLOUD

### Streamlit Cloud Architecture

```
┌──────────────────────────────────────────────────────┐
│         Streamlit Cloud (Managed PaaS)               │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │  Python Runtime Environment                  │  │
│  │  - Python 3.11 (auto-selected)              │  │
│  │  - Isolated container per app                │  │
│  │  - Auto-restart on code push                │  │
│  │  - Memory: 1GB (free), up to 16GB (paid)    │  │
│  │  - Timeout: 3 hours per session              │  │
│  │  - Storage: /tmp/ (ephemeral, 500MB)        │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │  Secrets Management                          │  │
│  │  - Encrypted in UI                           │  │
│  │  - Injected as st.secrets                    │  │
│  │  - NOT committed to GitHub                   │  │
│  │  - Environment variable access via st.env   │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │  File System                                 │  │
│  │  - Working directory: /app                   │  │
│  │  - Writeable: /tmp/ only                     │  │
│  │  - NO persistent storage                     │  │
│  │  - Read-only on production                   │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │  Networking                                  │  │
│  │  - HTTPS only (auto TLS)                     │  │
│  │  - URL: https://check-fornitori.streamlit.app  │
│  │  - Outbound: Unrestricted (per Supabase, OpenAI)│
│  │  - Inbound: Public internet                  │  │
│  └──────────────────────────────────────────────┘  │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │  Load Balancing & Availability               │  │
│  │  - Auto-scale to concurrent users            │  │
│  │  - No SLA guarantee (free tier)              │  │
│  │  - Uptime: ~99% empirical                    │  │
│  │  - Downtime: Maintenance windows             │  │
│  └──────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

### GitHub Integration

**Deployment Flow:**
```
1. Push code to GitHub (main branch)
   git add .
   git commit -m "Fix logging"
   git push origin main

2. Streamlit Cloud webhook triggered
   ├─ Clone repo
   ├─ pip install -r requirements.txt
   ├─ streamlit run app.py
   └─ Serve on https://check-fornitori.streamlit.app

3. App available in ~2 minutes
   - Old version stopped
   - New version started
   - Secrets re-injected
   - Caches cleared

4. Logs visible in:
   - Settings > Logs (tail -f)
   - Manage > Run history
```

**Branches:**
- `main`: Production (deployed to streamlit.app)
- `dev`: Development (local testing before merge)

---

### External Dependencies

```
App.py
  │
  ├─ SUPABASE
  │  ├─ Project: food-cost-intelligence
  │  ├─ Region: EU Central (eu-west-1)
  │  ├─ Database: PostgreSQL 14.8
  │  ├─ Storage: S3 (100GB free)
  │  ├─ Auth: Supabase Auth + RLS
  │  └─ URL: https://{project_id}.supabase.co
  │
  ├─ OPENAI
  │  ├─ Organization: Personal (mattiadavolio90)
  │  ├─ Model: gpt-4 (latest)
  │  ├─ API Rate: 90k TPM
  │  ├─ Quota: ~3,000 fatture/mese
  │  └─ URL: https://api.openai.com/v1
  │
  ├─ BREVO
  │  ├─ Account: Check Fornitori
  │  ├─ Quota: 300 email/day (free)
  │  ├─ Upgrade: 1,000/day (premium)
  │  └─ URL: https://api.brevo.com/v3
  │
  └─ GITHUB
     ├─ Repo: mattiadavolio/fci-project
     ├─ Branch: main (production)
     ├─ .gitignore: Protegge secrets
     └─ Webhook: Triggers Streamlit deploy
```

---

## 1️⃣1️⃣ DEPLOYMENT & DEVOPS

### Pre-Deployment Checklist

#### Fase 1: Local Testing
- [ ] `pip install -r requirements.txt` (installa tutte le dipendenze)
- [ ] `streamlit run app.py` (test in locale)
- [ ] Login test (crea account test)
- [ ] Upload fattura test (PDF/XML)
- [ ] AI categorizzazione test (mock o API reale)
- [ ] Admin panel test (accedi come admin)
- [ ] Dashboard visualizzazione
- [ ] Export Excel
- [ ] No error nel console/logs

#### Fase 2: Code Quality
- [ ] `.gitignore` presente e corretto
- [ ] `requirements.txt` con versioni specifiche
- [ ] `.streamlit/config.toml` presente
- [ ] `secrets.toml` **NOT** committato (verify: `git log`)
- [ ] No hardcoded API keys nel codice
- [ ] No commented-out code (pulizia)
- [ ] No TODO comments critici
- [ ] Code readable (naming conventions)

#### Fase 3: Configuration
- [ ] Supabase URL e KEY corretti in secrets.toml
- [ ] OpenAI API key attivo (quota verificata)
- [ ] Brevo API key configurato
- [ ] Admin email corretto in admin.py
- [ ] Email sender configurato
- [ ] Database migrations completate (schema a posto)

#### Fase 4: Secrets Preparation
```bash
# Verifica secrets non committati
git log --all --full-history -- '.streamlit/secrets.toml'
# Nessun output = ✅ OK

# Verifica .gitignore protegge
grep "secrets" .gitignore
# Output: secrets.toml, .streamlit/secrets.toml = ✅ OK
```

#### Fase 5: GitHub Preparation
```bash
git add .gitignore requirements.txt .streamlit/config.toml
git commit -m "Add deployment configuration"
git push origin main
```

### Deployment Steps

**Step 1: Streamlit Cloud Setup**

```
1. Go to https://share.streamlit.io
2. Sign up / Log in
3. Click "New app"
4. Configure:
   - Repository: mattiadavolio/fci-project
   - Branch: main
   - Main file path: app.py
   - Python version: 3.11
5. Click "Deploy"
   └─ Wait 2-3 minuti per build e start
```

**Step 2: Add Secrets**

```
1. Once deployed, go to Settings > Secrets
2. Copy ENTIRE content from your local .streamlit/secrets.toml:

   OPENAI_API_KEY = "sk-proj-..."
   
   [supabase]
   url = "https://xxxxx.supabase.co"
   key = "eyJhbGc..."
   service_role_key = "eyJhbGc..."
   
   [brevo]
   api_key = "xkeysib-..."
   sender_email = "your@email.com"
   sender_name = "Check Fornitori AI"

3. Click "Save"
4. App auto-restarts con secrets injected ✅
```

**Step 3: Verify Deployment**

```
1. Open app URL: https://check-fornitori.streamlit.app
2. Check logs:
   Settings > Logs > "Show full logs"
   
   Look for:
   ✅ "✅ Logging su stdout attivo (cloud mode)"
   ✅ "Streamlit version"
   ✅ "Python version"
   ✅ NO "Permission denied" errors
   ✅ NO "Read-only file system" errors

3. Test functionality:
   - [ ] Login works
   - [ ] Upload fattura works
   - [ ] AI categorizzazione works
   - [ ] Dashboard shows data
   - [ ] Admin panel (if admin) works
   - [ ] Export Excel works
```

### Post-Deployment Monitoring

**Daily Checks:**
```bash
# View logs real-time
Streamlit Cloud > App > Settings > Logs

# Look for:
- Errors (red)
- Warnings (yellow)
- OpenAI API rate limits
- Database connection issues
```

**Weekly Checks:**
- Total API costs (OpenAI dashboard)
- Email sends (Brevo analytics)
- Database usage (Supabase dashboard)
- Active users (Streamlit Cloud stats)

**Monthly Checks:**
- Feature requests / bugs
- Performance degradation
- Security updates needed
- Cost optimization opportunities

---

## 1️⃣2️⃣ FILE STRUCTURE & MODULES

### Directory Tree

```
fci-project/
├─ .git/                          # Git repository
├─ .gitignore                    # ✅ NUOVO - Protegge secrets
├─ .streamlit/
│  ├─ config.toml               # ✅ NUOVO - App configuration
│  └─ secrets.toml              # LOCAL ONLY (gitignored)
├─ app.py                        # Main app (6210 righe)
├─ admin.py                      # Admin panel (2090 righe)
├─ cambio_password.py            # Password reset
├─ requirements.txt              # ✅ AGGIORNATO - con tenacity
├─ README.md                     # Documentation (495 righe)
├─ pages/                        # Streamlit multipage (feature-specific)
│  ├─ 1_Upload.py
│  ├─ 2_Dashboard.py
│  ├─ 3_Export.py
│  ├─ 4_Admin.py                # (if admin detected)
│  └─ ... altri page file
├─ database/                     # (opzionale) SQL migration files
│  ├─ schema.sql
│  ├─ migrations/
│  │  ├─ 001_init.sql
│  │  └─ 002_add_alerts.sql
│  └─ ...
├─ tests/                        # (opzionale) Unit tests
│  ├─ test_categorizzazione.py
│  └─ test_auth.py
├─ docs/                         # (opzionale) Documentation
│  ├─ API.md
│  ├─ DATABASE.md
│  └─ ARCHITECTURE.md
└─ assets/                       # Static files (images, icons)
   ├─ logo.png
   └─ ...
```

### app.py Breakdown (6210 righe)

```python
# IMPORTS (righe 1-50)
import streamlit as st
from supabase import create_client
import pandas as pd
import openai
from tenacity import retry, stop_after_attempt  # ← ADDED
# ... 40+ imports

# SESSION STATE INIT (righe 50-150)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
# ... more session vars

# SECRETS LOADING (righe 1596-1597)
try:
    supabase_url = st.secrets["supabase"]["url"]
    supabase_key = st.secrets["supabase"]["key"]
    api_key = st.secrets["OPENAI_API_KEY"]
except KeyError as e:
    st.error(f"❌ Secret missing: {e}")
    st.stop()

# LOGGER SETUP (righe 1580-1610) ← FIXED FOR CLOUD
import sys
logger = logging.getLogger('fci_app')
if not logger.handlers:
    try:
        from logging.handlers import RotatingFileHandler
        handler = RotatingFileHandler('debug.log', maxBytes=5_000_000, backupCount=5)
        # ...
    except (OSError, PermissionError):
        handler = logging.StreamHandler(sys.stdout)
        # ... fallback

# MAIN APP SECTIONS:

## Section 1: Authentication (righe ~1650-1750)
def login_page():
    st.title("🔐 Login - Check Fornitori AI")
    email = st.text_input("Email:")
    password = st.text_input("Password:", type="password")
    if st.button("Login"):
        user = verifica_password(email, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.user_id = user['id']
            st.success(f"✅ Benvenuto {user['nome_ristorante']}!")
            st.rerun()

## Section 2: File Upload & Parsing (righe ~2000-2200)
def carica_file_e_processa(file_bytes, file_type):
    """
    PDF → PyMuPDF → text extraction
    XML → xmltodict → dict parsing
    Returns: DataFrame
    """
    if file_type == 'pdf':
        doc = PyPDF2.PdfReader(file_bytes)
        text = ""
        for page in doc.pages:
            text += page.extract_text()
        # Parse rows from text (regex)
    elif file_type == 'xml':
        data = xmltodict.parse(file_bytes)
        # Flatten to rows
    return df

## Section 3: AI Categorizzazione (righe ~3150-3250)
@retry(stop=stop_after_attempt(3))
def categorizza_batch_ai(descrizioni, memoria_ai):
    """Call GPT-4 with memory"""
    prompt = build_prompt(descrizioni, memoria_ai)
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[...],
        temperature=0.2,
        max_tokens=2000
    )
    return parse_response(response)

## Section 4: Database Operations (righe ~2400-2600)
@st.cache_data(ttl=None)
def carica_e_prepara_dataframe(user_id):
    """Load user invoices from Supabase"""
    response = supabase.table("fatture") \
        .select("*") \
        .eq("user_id", user_id) \
        .execute()
    return pd.DataFrame(response.data)

## Section 5: Dashboard & Visualization (righe ~3600-3950)
def mostra_dashboard(df_fatture, df_prodotti):
    """Interactive Plotly charts + st.dataframe"""
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_trend_prezzi)
    with col2:
        st.plotly_chart(fig_spesa_categoria)
    st.dataframe(df_fatture, use_container_width=True)

## Section 6: Export & Reporting (righe ~3150-3300)
def export_excel(df_fatture, df_prodotti):
    """Multi-sheet Excel file"""
    with pd.ExcelWriter(...) as writer:
        df_fatture.to_excel(writer, sheet_name='Fatture')
        df_prodotti.to_excel(writer, sheet_name='Prodotti')

## Section 7: Main App Flow (righe ~6100-6210)
def main():
    if not st.session_state.logged_in:
        login_page()
    else:
        st.sidebar.write(f"Ciao {st.session_state.user_email}")
        page = st.sidebar.radio("Navigation", ["Dashboard", "Upload", "Export", "Admin"])
        if page == "Dashboard":
            mostra_dashboard(...)
        elif page == "Upload":
            upload_fattura_page(...)
        # ...

if __name__ == "__main__":
    main()
```

### admin.py Breakdown (2090 righe)

```python
# IMPORTS
import streamlit as st
from supabase import create_client
import pandas as pd
import json
from datetime import datetime

# CONSTANTS
ADMIN_EMAILS = ["mattiadavolio90@gmail.com"]  # ⚠️ Hardcoded, TODO: Move to secrets

# CONNECTION POOLING ✅
@st.cache_resource
def get_supabase_client():
    return create_client(
        st.secrets["supabase"]["url"],
        st.secrets["supabase"]["key"]
    )

supabase = get_supabase_client()

# MAIN SECTIONS:

## Section 1: Admin Auth Check (righe ~100-120)
def check_admin():
    if st.session_state.get("user_email") not in ADMIN_EMAILS:
        st.error("❌ Accesso negato - Accesso admin")
        st.stop()

## Section 2: Review Items < 70% (righe ~200-400)
def review_low_confidence():
    """Load items with confidence < 70% from review_items table"""
    items = supabase.table("review_items") \
        .select("*") \
        .lt("confidence", 0.70) \
        .eq("revisionato", False) \
        .execute()
    
    for item in items.data:
        st.subheader(item['descrizione_originale'])
        st.write(f"Confidence: {item['confidence']:.0%}")
        st.write(f"Suggerito: {item['categoria_suggerita']}")
        
        categoria_corretta = st.selectbox(
            f"Categoria corretta [{item['id']}]:",
            CATEGORIE_AVAILABLE
        )
        
        if st.button(f"Approva [{item['id']}]"):
            # Update review_items
            supabase.table("review_items") \
                .update({
                    "categoria_approvata": categoria_corretta,
                    "revisionato": True,
                    "revisionato_at": datetime.now().isoformat(),
                    "revisionato_da": st.session_state.user_email
                }) \
                .eq("id", item['id']) \
                .execute()
            
            # Update fatture item
            # Update prodotti_master memory
            # Log to audit

## Section 3: AI Memory Management (righe ~500-700)
def gestisci_memoria_ai():
    """View and update memoria_ai_correzioni.json"""
    memory_file = "memoria_ai_correzioni.json"
    
    try:
        with open(memory_file, 'r') as f:
            memoria = json.load(f)
    except FileNotFoundError:
        memoria = {}
    
    st.subheader("Aggiungi Categorizzazione")
    desc = st.text_input("Descrizione:")
    cat = st.selectbox("Categoria:", CATEGORIE_AVAILABLE)
    
    if st.button("Aggiungi"):
        memoria[desc] = cat
        
        # Backup
        import shutil
        shutil.copy(memory_file, f"{memory_file}.backup")
        
        # Save
        with open(memory_file, 'w') as f:
            json.dump(memoria, f, indent=2, ensure_ascii=False)
        
        st.success(f"✅ Aggiunto: {desc} → {cat}")

## Section 4: Analytics Dashboard (righe ~800-1000)
def mostra_analytics_globali():
    """All users combined statistics"""
    # Total uploads
    # Total categorizzazioni
    # Cost summary
    # Error rate
    # Top categories
    # User growth

## Section 5: User Management (righe ~1100-1300)
def gestisci_utenti():
    """Enable/disable/reset users"""
    users = supabase.table("users").select("*").execute()
    
    for user in users.data:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(f"📧 {user['email']}")
        with col2:
            st.write(f"Piano: {user['piano']}")
        with col3:
            if st.button(f"🔓 Disattiva [{user['id']}]"):
                supabase.table("users") \
                    .update({"attivo": False}) \
                    .eq("id", user['id']) \
                    .execute()

## Section 6: Upload Events Log (righe ~1400-1500)
def mostra_audit_log():
    """View upload_events table"""
    events = supabase.table("upload_events") \
        .select("*") \
        .order("timestamp", desc=True) \
        .limit(100) \
        .execute()
    
    df = pd.DataFrame(events.data)
    st.dataframe(df, use_container_width=True)

## Section 7: Main Admin Panel (righe ~2050-2090)
def main():
    st.title("👨‍💼 ADMIN PANEL")
    check_admin()
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Review Items", "Memory", "Analytics", "Users", "Logs"
    ])
    
    with tab1:
        review_low_confidence()
    with tab2:
        gestisci_memoria_ai()
    with tab3:
        mostra_analytics_globali()
    # ...
```

---

## 1️⃣3️⃣ FEATURE BREAKDOWN

### Feature 1: Upload Fattura

**Epic:** Ristoratore carica fattura XML/PDF

**Workflow:**
```
┌─ Input file (PDF o XML)
├─ Parsing (estrae dati)
├─ Validazione (formato + data)
├─ Upload a Supabase Storage
├─ Crea record in tabella fatture
├─ Invia a OpenAI GPT-4
├─ Salva categorizzazioni
├─ Controlla anomalie prezzo
├─ Crea alert se anomalia
└─ Notifica email (opzionale)
```

**Code Location:** app.py righe 2000-2200 (carica_file_e_processa)

**Test Case:**
- Upload: `test_fattura_sysco.pdf` (120 righe)
- Expected: 120 categorizzazioni in 45 secondi
- Cost: €0.08 stimato

---

### Feature 2: AI Categorizzazione

**Epic:** Sistema automaticamente classifica articoli

**Workflow:**
```
┌─ Ricevi descrizione articolo
├─ Controlla: esiste in classificazioni_manuali?
│  └─ SI: Usa category_corretta (priorità max)
├─ Controlla: esiste in prodotti_utente?
│  └─ SI: Usa categoria nota (high confidence)
├─ Controlla: esiste in prodotti_master?
│  └─ SI: Usa categoria globale (medium confidence)
├─ SE nessun match: chiedi a GPT-4
│  ├─ Prompt: descrizione + 50 esempi memoria
│  ├─ Response: categoria + confidence
│  └─ SI confidence < 70%? Accoda review admin
├─ Salva in prodotti_master (aggiorna memoria)
└─ Salva in fatture.items
```

**Code Location:** app.py righe 3150-3250 (categorizza_batch_ai)

**Example:**
```
Input: "Filetto di Branzino 500g - Congelato"
Memory: Storico simile: "FILETTO BRANZINO" → "PESCE FRESCO"
Output: {
  "categoria": "PESCE FRESCO",
  "confidence": 0.96,  # Memoria + AI = very high
  "fonte": "memory_match + ai_confirmation"
}
```

---

### Feature 3: Dashboard Analiti

**Epic:** Visualizzazione trend prezzi e spesa per categoria

**Components:**
1. **Trend Grafico:** Plotly line chart (30/60/90 giorni)
2. **Pie Chart:** Spesa per categoria (ultimi 30 gg)
3. **Bar Chart:** Fornitore ranking (top 10)
4. **Tabella Fatture:** Sortabile, filtrable
5. **Pivot Mensile:** Confronto mese vs mese
6. **KPI Cards:** Totale speso, avg prezzo, alerts count

**Code Location:** app.py righe 3600-3950 (mostra_dashboard)

**Performance:**
- Load time: <3 secondi (con cache)
- Refresco: 5 minuti (TTL cache)
- Data points: ~500 max (ultimi 6 mesi)

---

### Feature 4: Alert Anomalie Prezzi

**Epic:** Notifica automatica su aumenti anomali

**Triggering Logic:**
```
Per ogni articolo:
1. Calcola media storica (ultimi 90 giorni)
2. Calcola std dev
3. Z-score = (prezzo_attuale - media) / std
4. SE abs(z) > 2.5:
   ├─ Crea alert in DB (severity: ALTA)
   ├─ Invia email a ristoratore
   ├─ Visualizza rosso in dashboard
   └─ Log to audit

Esempio:
  Articolo: "Burro francese 500g"
  Prezzo attuale: €18.50
  Media (90g): €12.00
  Std dev: €1.50
  Z-score: (18.50 - 12.00) / 1.50 = 4.33 → ANOMALO!
  Email: "⚠️ BURRO aumentato 54% - Contatta fornitore"
```

**Code Location:** Calcolato in categorizza_batch_ai()

**Email Template:**
```html
Subject: ⚠️ ALERT: Burro francese aumentato 54%

<h2>Anomalia Prezzo Rilevata</h2>
<p><strong>Articolo:</strong> Burro francese 500g</p>
<p><strong>Prezzo attuale:</strong> €18.50</p>
<p><strong>Prezzo medio (90g):</strong> €12.00</p>
<p><strong>Variazione:</strong> +54%</p>
<p><strong>Azione consigliata:</strong> Contatta fornitore</p>
<a href="https://app.checkfornitori.it/dashboard">
  Visualizza dettagli
</a>
```

---

### Feature 5: Admin Review Panel

**Epic:** Admin approva/corregge categorizzazioni basse confidence

**Workflow:**
```
┌─ Admin accede panel
├─ Vede coda: 23 articoli < 70% confidence
├─ Per ogni articolo:
│  ├─ Visualizza: descrizione + storico prezzi
│  ├─ Suggerimina: categoria AI + confidence
│  ├─ Seleziona: categoria corretta da dropdown
│  ├─ Clicca: "Approva"
│  └─ Sistema:
│     ├─ Aggiorna review_items (revisionato=true)
│     ├─ Aggiorna fatture.items (categoria corretta)
│     ├─ Aggiorna prodotti_master (contatore++)
│     ├─ Aggiorna memoria_ai_correzioni.json
│     └─ Log audit
└─ Risultato: Memoria AI migliora per future categorizzazioni
```

**Code Location:** admin.py righe 200-400 (review_low_confidence)

**Impact:**
```
Prima review: Articolo "Riso Carnaroli" → confidence 45%
Dopo review × 3: Stesso articolo → confidence 89%
```

---

### Feature 6: Export Excel

**Epic:** Scarica dati in Excel multi-sheet

**Sheets:**
1. **Fatture:** Numero, data, fornitore, totale, URL file
2. **Prodotti:** Descrizione, categoria, prezzo medio, contatore
3. **Categorie:** Riepilogo spesa per categoria
4. **Trend:** Spesa mensile trend
5. **Alert:** Alert ultimi 30 giorni

**Code Location:** app.py righe 3150-3300 (export_excel)

**Example File:**
```
check-fornitori-export-20260106.xlsx
├─ Fatture (50 righe, 8 colonne)
├─ Prodotti (847 righe, 5 colonne)
├─ Categorie (11 righe, 3 colonne)
├─ Trend (6 righe, 12 colonne)
└─ Alert (15 righe, 6 colonne)

File size: ~2.1 MB
```

---

## 1️⃣4️⃣ ISSUES & TECHNICAL DEBT

### 🔴 CRITICAL (Blocca deployment cloud)

**ISSUE #1: Filesystem Write on Cloud**
- **Severity:** CRITICO
- **Localizzazione:** app.py riga 1587 (RotatingFileHandler)
- **Problema:** Streamlit Cloud ha filesystem read-only
- **Impatto:** App crasha subito
- **Soluzione:** Fallback a stdout (implementato)
- **Status:** ✅ RISOLTO (vedi paragrafo 9)

**ISSUE #2: Tenacity Mancante**
- **Severity:** CRITICO
- **Localizzazione:** app.py riga 18 (import tenacity)
- **Problema:** Module not found su cloud deployment
- **Impatto:** AppError al primo retry OpenAI
- **Soluzione:** Aggiungere `tenacity>=8.2.3` a requirements.txt
- **Status:** ✅ RISOLTO (vedi paragrafo 5)

**ISSUE #3: .gitignore Mancante**
- **Severity:** CRITICO
- **Problema:** secrets.toml potrebbe essere committato
- **Impatto:** Leak credenziali OpenAI/Supabase su GitHub
- **Soluzione:** Creare .gitignore (vedi paragrafo 5)
- **Status:** ✅ RISOLTO (file pronto)

---

### ⚠️ HIGH (Degrade performance/UX)

**ISSUE #4: No Paginazione Query Grandi**
- **Severity:** ALTO
- **Localizzazione:** app.py riga 2913 (carica_e_prepara_dataframe)
- **Problema:** Carica TUTTE le fatture senza limit
- **Impatto:** OOM/slow con 10k+ fatture
- **Soluzione:** 
  ```python
  .order("data_fattura", desc=True) \
  .limit(1000) \
  .offset(page*1000)
  ```
- **Status:** 📋 TODO

**ISSUE #5: Cache infinito su dataframe user**
- **Severity:** ALTO
- **Localizzazione:** app.py riga 2913 `@st.cache_data(ttl=None)`
- **Problema:** Nuove fatture non appaiono nel dashboard
- **Impatto:** User confusion ("Dove è la fattura che ho caricato?")
- **Soluzione:** `ttl=300` (refresh ogni 5 min)
- **Status:** 📋 TODO

**ISSUE #6: Admin email hardcoded (duplicata)**
- **Severity:** ALTO
- **Localizzazione:** app.py + admin.py (2 posti)
- **Problema:** Rischio desync se cambio email
- **Impatto:** Admin non riesce ad accedere a uno dei pannelli
- **Soluzione:** Centralizzare in secrets.toml:
  ```toml
  [app]
  admin_emails = ["mattiadavolio90@gmail.com"]
  ```
- **Status:** 📋 TODO

**ISSUE #7: No Connection Pooling in app.py**
- **Severity:** ALTO
- **Localizzazione:** app.py riga ~1596 (crea client globale)
- **Problema:** Nuovo client per ogni run (no caching)
- **Impatto:** Rallenta su traffic alto
- **Soluzione:** Aggiungere dopo riga 1596:
  ```python
  @st.cache_resource
  def get_supabase_client():
      return create_client(supabase_url, supabase_key)
  ```
- **Status:** 📋 TODO

**ISSUE #8: File Upload Non Persistente**
- **Severity:** ALTO
- **Localizzazione:** app.py riga 2334 (salva memoria_ai su file)
- **Problema:** /tmp/ ephemeral su cloud (perso dopo restart)
- **Impatto:** Memoria AI perde dati
- **Soluzione:** 
  - Opzione A: Salva memoria_ai in Supabase (BEST)
  - Opzione B: Migliore fallback try/except OSError
- **Status:** 📋 TODO

---

### 📋 MEDIUM (Nice-to-have, non blocca)

**ISSUE #9: Nessun error tracking**
- **Severity:** MEDIO
- **Problema:** Errori produzione non tracciati
- **Impatto:** Difficile debuggare problemi live
- **Soluzione:** Integrare Sentry.io
- **Status:** 📋 FUTURE

**ISSUE #10: No user feedback mechanism**
- **Severity:** MEDIO
- **Problema:** Ristoratore non può segnalare errori categorizzazione
- **Impatto:** Feedback scarso per AI training
- **Soluzione:** Pulsante "Sbagliato?" nel dashboard
- **Status:** 📋 FUTURE

**ISSUE #11: No Dark mode**
- **Severity:** BASSO
- **Problema:** Theme light-only
- **Impatto:** Eye strain per uso prolungato
- **Soluzione:** st.set_page_config(initial_sidebar_state="expanded", theme="dark")
- **Status:** 📋 FUTURE

---

## 1️⃣5️⃣ ROADMAP

### Phase 1: MVP (COMPLETED ✅)
- ✅ Login/Logout
- ✅ Upload fattura (XML/PDF)
- ✅ AI categorizzazione (GPT-4)
- ✅ Dashboard analytics
- ✅ Alert anomalie prezzi
- ✅ Export Excel

### Phase 2: Production Hardening (IN PROGRESS 🔄)
- ⏳ Fix cloud logging
- ⏳ Add tenacity dependency
- ⏳ Create .gitignore
- ⏳ Connection pooling Supabase
- ⏳ Paginazione query
- ⏳ Cache optimization
- ⏳ Centralizzazione config

**Timeline:** 1-2 settimane

### Phase 3: Enhanced Admin (Q2 2026)
- 📋 Batch categorizzazione correction
- 📋 User management (enable/disable/reset)
- 📋 Cost tracking per utente
- 📋 Billing integration
- 📋 API audit logs detailed

**Timeline:** 3-4 settimane

### Phase 4: Analytics Pro (Q2-Q3 2026)
- 📋 Previsioni trend prezzi (ML)
- 📋 Supplier performance scoring
- 📋 Procurement recommendations
- 📋 Budget forecasting
- 📋 Competitor price tracking

**Timeline:** 8-10 settimane

### Phase 5: Mobile App (Q3 2026)
- 📋 Flutter/React Native
- 📋 Camera upload fatture
- 📋 Offline mode
- 📋 Mobile dashboard

**Timeline:** 6-8 settimane

### Phase 6: B2B Expansion (Q4 2026)
- 📋 Multi-account (chain concept)
- 📋 Centralized reporting
- 📋 Custom categories per user
- 📋 Webhooks / API for partners

**Timeline:** 10-12 settimane

---

## 1️⃣6️⃣ TROUBLESHOOTING GUIDE

### "PermissionError: File or directory not found"

**Cause:** Streamlit Cloud filesystem read-only

**Solution:**
```
1. Verify logging.py has try/except with fallback stdout
2. Check .streamlit/config.toml exists
3. Verify secrets.toml in Cloud (NOT in git)
4. Check logs: Settings > Logs
   Look for: "✅ Logging su stdout attivo (cloud mode)"
```

---

### "ModuleNotFoundError: No module named 'tenacity'"

**Cause:** requirements.txt manca `tenacity`

**Solution:**
```bash
echo "tenacity>=8.2.3" >> requirements.txt
git add requirements.txt
git commit -m "Add tenacity dependency"
git push
# Cloud auto-redeploys in ~2 min
```

---

### "PermissionError: secrets.toml already tracked"

**Cause:** secrets.toml già committato su GitHub

**Solution:**
```bash
# Remove from tracking
git rm --cached .streamlit/secrets.toml

# Add to .gitignore
echo ".streamlit/secrets.toml" >> .gitignore

# Commit
git add .gitignore
git commit -m "Remove secrets from tracking"
git push

# WARN: secrets.toml still visible in history
# → Rigenerare TUTTE le API key (OpenAI, Supabase, Brevo)
```

---

### "RateLimitError: 429 Too Many Requests"

**Cause:** OpenAI TPM limit exceeded

**Solution:**
```
1. Check quota: OpenAI dashboard
2. Reduce batch size (max 5 articoli/batch)
3. Add sleep(1) tra batch
4. Upgrade plan OpenAI
5. Implement queuing (Redis + background job)
```

---

### "AuthError: Invalid API key"

**Cause:** Secrets errati o scaduti

**Solution:**
```
1. Verify locale .streamlit/secrets.toml è corretto
2. Verifica cloud secrets (Settings > Secrets)
3. Test API key direttamente:
   curl -H "Authorization: Bearer {KEY}" \
        https://api.openai.com/v1/models
4. Rigenerare key se necessario
5. Rideployare app
```

---

### "Database is in read-only mode"

**Cause:** Supabase in manutenzione o quota exceeded

**Solution:**
```
1. Check Supabase status: status.supabase.com
2. Verificare storage quota
3. Contattare Supabase support
4. Implementare retry logic nel codice
```

---

### Dashboard mostra dati vecchi

**Cause:** Cache non invalidato

**Solution:**
```
1. Manuale: Ctrl+Shift+R (hard refresh)
2. Auto: Aspetta TTL cache (5 min default)
3. Codice:
   if st.button("🔄 Refresh"):
       st.cache_data.clear()
       st.rerun()
```

---

### Upload fattura fallisce con "File too large"

**Cause:** File > 200MB

**Solution:**
```
Aumentare in .streamlit/config.toml:
[server]
maxUploadSize = 500  # MB (aumentato da 200)

Oppure chiedere utente di comprimere PDF
```

---

## 📚 APPENDICE

### A. Categoria List

```
1. FRUTTA VERDURA
   ├─ Pomodori
   ├─ Insalata
   ├─ Carote
   └─ Patate

2. PESCE FRESCO
   ├─ Branzino
   ├─ Filetto
   ├─ Polpo
   └─ Calamari

3. CARNI ROSSE
   ├─ Manzo
   ├─ Bistecca
   ├─ Vitello
   └─ Maiale

4. POLLAME
   ├─ Pollo
   ├─ Anatra
   ├─ Quaglia
   └─ Tacchino

5. FORMAGGI LATTICINI
   ├─ Parmigiano
   ├─ Mozzarella
   ├─ Burro
   └─ Latte

6. PASTA RISO CEREALI
   ├─ Pasta
   ├─ Riso
   ├─ Farina
   └─ Pane

7. CONDIMENTI SPEZIE
   ├─ Olio
   ├─ Aceto
   ├─ Sale
   └─ Pepe

8. BEVANDE ALCOLICHE
   ├─ Vino rosso
   ├─ Vino bianco
   ├─ Birra
   └─ Liquori

9. BEVANDE NON ALCOLICHE
   ├─ Caffè
   ├─ Tè
   ├─ Succo
   └─ Acqua

10. MATERIALE CONSUMABILE
    ├─ Piatti
    ├─ Bicchieri
    ├─ Tovaglie
    └─ Carta

11. ALTRO
    └─ Non classificato
```

---

### B. API Endpoints Summary

| Endpoint | Method | Auth | Rate | Doc |
|----------|--------|------|------|-----|
| `/v1/chat/completions` | POST | Bearer | 90k TPM | OpenAI |
| `/rest/v1/fatture` | GET/POST | Key | - | Supabase |
| `/rest/v1/users` | GET/POST | Key | - | Supabase |
| `/v3/smtp/email` | POST | Key | 300/day | Brevo |

---

### C. Glossary

| Term | Definition |
|------|-----------|
| **RLS** | Row-Level Security (Supabase) - utenti vedono solo i loro dati |
| **TPM** | Tokens Per Minute (OpenAI rate limit) |
| **TTL** | Time To Live (cache duration) |
| **JSONB** | Binary JSON (PostgreSQL type, queryable) |
| **Z-score** | Statistical measure of deviation from mean |
| **Tenacity** | Retry library per exponential backoff |
| **Argon2** | Password hashing algorithm (cryptographically secure) |
| **OCR** | Optical Character Recognition (PDF → text) |
| **Multi-tenancy** | Sistema con multiple users con dati isolati |

---

**FINE DOCUMENTAZIONE**

_Ultima modifica: 06/01/2026_  
_Autore: Mattia D'Avolio_  
_Versione: 1.0_

Per aggiornamenti futuri, aggiungere sezione "CHANGELOG" qui sotto.

