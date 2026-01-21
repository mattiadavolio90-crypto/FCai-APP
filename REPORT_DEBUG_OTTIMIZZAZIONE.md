# 🔍 REPORT DEBUG & OTTIMIZZAZIONE - FCI_PROJECT

**Data Analisi:** 21 Gennaio 2026  
**Analizzati:** 15 file Python + struttura progetto  
**Obiettivo:** Identificare codice inutilizzato, duplicato, obsoleto per ottimizzazione

---

## 📊 RIEPILOGO ESECUTIVO

| Categoria | Conteggio | Righe Recuperabili |
|-----------|-----------|-------------------|
| **Import inutilizzati** | 50+ | ~50 righe |
| **Funzioni mai chiamate** | 15+ | ~400 righe |
| **Codice duplicato** | 12 pattern | ~250 righe |
| **Codice commentato obsoleto** | 8 blocchi | ~80 righe |
| **Bug/Inconsistenze** | 3 critici | - |
| **TOTALE STIMATO** | | **~780 righe** |

---

## 🔴 PRIORITÀ CRITICA (BUG DA FIXARE)

### 1. BUG: Codice Python dentro JavaScript (app.py)
**Righe 284-288**
```python
# DENTRO BLOCCO <script> JavaScript:
        document.querySelectorAll('[data-testid="stFooter"]').forEach(el => el.remove());
            st.session_state.force_empty_until_upload = False   # ← PYTHON!
            st.session_state.files_processati_sessione = set()   # ← PYTHON!
            st.cache_data.clear()                                # ← PYTHON!
```
**Problema:** Codice Python inserito erroneamente in blocco JavaScript. Non eseguito mai.
**Azione:** Rimuovere righe 284-288

---

### 2. BUG: Variabile `df_editor` non definita (admin.py)
**Riga 1639**
```python
df_editor = filtered_df.copy()  # ← filtered_df non è definito!
```
**Problema:** `NameError` quando eseguito
**Azione:** Correggere riferimento variabile

---

### 3. BUG: Chiavi duplicate nel dizionario CORREZIONI_CATEGORIA (constants.py)

| Chiave | Riga 1 | Valore 1 | Riga 2 | Valore 2 |
|--------|--------|----------|--------|----------|
| `"PASSATA POMOD"` | L819 | "SALSE E CREME" | L869 | "CONSERVE" |
| `"PASSATA POMODORO"` | L820 | "SALSE E CREME" | L870 | "CONSERVE" |
| `"ARAGOSTINE"` | L826 | "PASTICCERIA" | L840 | "PASTICCERIA" |
| `"COPPA GELATO"` | L547 | "GELATI" | L599 | "GELATI" |

**Problema:** Python sovrascrive silenziosamente, comportamento inconsistente
**Azione:** Rimuovere duplicati (decidere quale valore mantenere per PASSATA)

---

## 🟠 PRIORITÀ ALTA (Import Inutilizzati)

### app.py - Import da rimuovere (~30)

| Riga | Import | Motivo |
|------|--------|--------|
| 3 | `base64` | Mai usato |
| 4 | `tempfile` | Mai usato |
| 12 | `plotly.graph_objects as go` | Mai usato (solo px) |
| 16 | `PyPDF2` | Mai usato |
| 17 | `fitz` | Mai usato |
| 18 | `pdf2image` | Mai usato |
| 19-20 | `tenacity` (retry, stop, wait) | Mai usato in app.py |
| 25-43 | Tutte `REGEX_*` | Usate solo in utils, non app.py |
| 47-51 | `CATEGORIE_FOOD`, `TUTTE_LE_CATEGORIE`, ecc. | Mai usate |
| 56 | `PROMPT_AI_POTENZIATO` | Mai usato direttamente |
| 61-62 | `pulisci_descrizione`, `normalizza_prezzo` | Mai chiamate |
| 65-66 | `valida_prezzo`, `rileva_unita_misura` | Mai chiamate |
| 76-77 | `calcola_statistiche_fatture`, `calcola_trend_mensile` | Mai chiamate |
| 96-97 | `carica_memoria_ai`, `salva_memoria_ai` (Legacy) | Mai chiamate |

### services/ai_service.py - Import da rimuovere

| Riga | Import |
|------|--------|
| 14 | `datetime` (solo timedelta usato) |
| 27 | `re` (già importato implicitamente) |

### services/auth_service.py - Import da rimuovere

| Riga | Import |
|------|--------|
| 23 | `logging` (usa logger invece) |

### services/db_service.py - Import da rimuovere

| Riga | Import |
|------|--------|
| 17 | `logging` |

### services/invoice_service.py - Import da rimuovere

| Riga | Import |
|------|--------|
| 17 | `logging` |
| 62 | `carica_memoria_ai` (non usato) |

### utils/formatters.py - Import da rimuovere

| Riga | Import |
|------|--------|
| 15 | `re` (mai usato) |

### utils/text_utils.py - Import da rimuovere

| Riga | Import |
|------|--------|
| 14 | `Tuple` da typing (solo Optional usato) |

### utils/validation.py - Import da rimuovere

| Riga | Import |
|------|--------|
| 10 | `re` (regex importate da constants) |

### pages/admin.py - Import da rimuovere

| Riga | Import |
|------|--------|
| 14 | `plotly.express as px` (mai usato) |
| 18-20 | `sys.path.insert` (non necessario) |

---

## 🟡 PRIORITÀ MEDIA (Funzioni Mai Chiamate)

### app.py

| Righe | Funzione | Note |
|-------|----------|------|
| 1123-1172 | `audit_supabase_data()` | Debug/audit mai usato |
| 1324-1333 | `valida_file_fattura()` | Mai chiamata |

### admin.py (MASSICCIO - ~500 righe morte)

| Righe | Funzione | Note |
|-------|----------|------|
| 119-161 | `conferma_modifica()` | Mai chiamata |
| 163-207 | `ignora_modifica()` | Mai chiamata |
| 221-243 | `conferma_modifica_fornitore()` | Mai chiamata |
| 286-380 | `analizza_integrita_database()` | Mai chiamata |
| 387-437 | `trova_fornitori_duplicati()` | Mai chiamata |
| 439-497 | `statistiche_salute_sistema()` | Mai chiamata |
| 558-599 | `clienti_con_piu_errori()` | Mai chiamata |
| 697-719 | Helper funzione 1 | Mai chiamata |
| 721-745 | Helper funzione 2 | Mai chiamata |
| 747-772 | Helper funzione 3 | Mai chiamata |
| 774-783 | Helper funzione 4 | Mai chiamata |
| 785-797 | Helper funzione 5 | Mai chiamata |
| 799-848 | Helper funzione 6 | Mai chiamata |

### services/ai_service.py

| Righe | Funzione | Note |
|-------|----------|------|
| 716-759 | `carica_memoria_ai()`, `salva_memoria_ai()`, `aggiorna_memoria_ai()` | Legacy deprecate |

### utils/formatters.py

| Righe | Funzione | Note |
|-------|----------|------|
| 443-508 | `_suggerisci_categoria_da_descrizione()` | Funzione privata mai chiamata |

### utils/text_utils.py

| Righe | Funzione | Note |
|-------|----------|------|
| 140-171 | `main()` | Funzione test, mai eseguita |

---

## 🔵 PRIORITÀ MEDIA (Codice Duplicato)

### Pattern CSS Bottone Download (6 occorrenze in app.py)

| Righe | Sezione |
|-------|---------|
| 2672-2690 | Dettaglio |
| 3105-3123 | Alert |
| 3420-3438 | Categorie |
| 3540-3558 | Fornitori |
| 3698-3716 | Spese (Categorie) |
| 3780-3798 | Spese (Fornitori) |

**Soluzione:** Estrarre in `inject_download_button_css()` - risparmio ~100 righe

---

### Pattern Box Statistiche Blu (5 occorrenze in app.py)

| Righe | 
|-------|
| 2720-2730 |
| 3408-3418 |
| 3528-3538 |
| 3686-3696 |
| 3768-3778 |

**Soluzione:** Estrarre in `mostra_box_statistiche(n_righe, totale)` - risparmio ~40 righe

---

### Pattern Configurazione Grafici Plotly (4 occorrenze)

| Righe |
|-------|
| 3465-3497 |
| 3585-3617 |
| 3828-3860 |
| 3869-3901 |

**Soluzione:** Estrarre in `configura_grafico_barre(fig, titolo)` - risparmio ~60 righe

---

### Pattern Export Excel (6 occorrenze)

| Righe | Buffer |
|-------|--------|
| 2791 | excel_buffer |
| 3126 | excel_buffer |
| 3439 | excel_buffer |
| 3559 | excel_buffer |
| 3717 | excel_buffer |
| 3799 | excel_buffer |

**Soluzione:** Estrarre in `crea_excel_download(df, sheet_name)` - risparmio ~30 righe

---

### Hasher Password Duplicato (auth_service.py)

| Riga | Codice |
|------|--------|
| 28 | `ph = PasswordHasher()` (globale) |
| 261 | `ph = PasswordHasher()` (dentro `hash_password()`) |

**Soluzione:** Usare hasher globale nella funzione

---

### Filtro F&B Duplicato (db_service.py)

| Righe | Pattern |
|-------|---------|
| 276-282 | Commento + filtro CATEGORIE_SPESE_GENERALI |
| 438-444 | Stesso commento + filtro identico |

**Soluzione:** Estrarre in `_filtra_solo_fb(df)` helper

---

## 🟢 PRIORITÀ BASSA (Codice Commentato/Obsoleto)

### app.py

| Righe | Descrizione |
|-------|-------------|
| 1 | Commento fix deployment obsoleto |
| 144-156 | Changelog V3.2 obsoleto |
| 938-965 | Commenti placeholder funzioni spostate |
| 2360-2382 | Blocco icone AI 🧠 disabilitato (23 righe) |

### admin.py

| Righe | Descrizione |
|-------|-------------|
| 660-671 | Blocco "funzioni rimosse" |

### constants.py

| Righe | Descrizione |
|-------|-------------|
| 264-265 | Commento duplica codice sotto |

---

## ⚡ OTTIMIZZAZIONI PERFORMANCE

### 1. Consolidare Regex (constants.py)

**Prima:** 29 regex separate in `REGEX_UNITA_MISURA`
```python
REGEX_UNITA_MISURA = [re.compile(r'\bKG\b'), re.compile(r'\bG\b'), ...]
```

**Dopo:** 1 regex con alternation
```python
REGEX_UNITA_MISURA = re.compile(r'\b(KG|G|GR|GRAMMI|L|LT|...)\b', re.IGNORECASE)
```

**Beneficio:** Compilazione più veloce, matching più efficiente

---

### 2. Chiamate `st.cache_data.clear()` Multiple (app.py)

| Righe | Contesto |
|-------|----------|
| 4131 | Prima chiamata |
| 4152 | Seconda (ridondante) |
| 4167 | Terza (ridondante) |

**Azione:** Mantenere solo 1 chiamata

---

### 3. `time.sleep()` Eccessivi (app.py)

| Riga | Durata | Necessità |
|------|--------|-----------|
| 4171 | 0.3s | ❌ Rimuovere |
| 4244 | 1s | ⚠️ Valutare |
| 4660 | 2s | ✅ Necessario (batch) |
| 4770 | 0.5s | ❌ Rimuovere |

---

### 4. Import Dentro Funzioni (vari file)

| File | Riga | Import |
|------|------|--------|
| ai_service.py | 234 | `from datetime import datetime` |
| ai_service.py | 282, 296 | `import streamlit as st` |
| invoice_service.py | 45, 203, 398 | `import streamlit as st` |
| text_utils.py | 207 | `import re` (già globale) |

**Azione:** Spostare tutti gli import a livello modulo

---

### 5. Paginazione Client-Side Costosa (app.py 4380-4410)

```python
while True:
    response = supabase.table("fattures").select(...).range(offset, ...)
```

**Problema:** Carica dati a blocchi invece di usare RPC ottimizzata
**Azione:** Verificare/correggere RPC `get_distinct_files` che fallisce silenziosamente

---

## 📁 FILE POTENZIALMENTE ELIMINABILI

### Documentazione Obsoleta

| File | Note |
|------|------|
| `✅ IMPLEMENTAZIONE_COMPLETATA.txt` | Marker completamento, può essere archiviato |
| `RIASSUNTO_PROBLEMA_CATEGORIZZAZIONE_AI.txt` | Problema risolto |
| `PAGINAZIONE_IMPLEMENTATA.md` | Feature completata |

### File Markdown da Consolidare

I seguenti file potrebbero essere unificati in un unico `DOCUMENTAZIONE.md`:
- `ADMIN_PANEL_README.md`
- `COMANDI_UTILI.md`
- `GUIDA_RAPIDA_ADMIN.md`
- `LEARNING_CORREZIONI_UTENTE.md`
- `MEMORIA_GLOBALE_AI.md`
- `NORMALIZZAZIONE_DESCRIZIONI.md`
- `OPZIONI_URL_EMAIL.md`

---

## 🎯 PIANO D'AZIONE CONSIGLIATO

### Fase 1: Fix Bug Critici (30 min)
1. ✅ Rimuovere codice Python da JavaScript (app.py 284-288)
2. ✅ Fixare `filtered_df` → variabile corretta (admin.py 1639)
3. ✅ Rimuovere chiavi duplicate dizionario (constants.py)

### Fase 2: Pulizia Import (1 ora)
1. Rimuovere ~50 import inutilizzati da tutti i file
2. Testare che app funzioni ancora

### Fase 3: Rimuovere Codice Morto (2 ore)
1. Rimuovere funzioni mai chiamate in admin.py (~500 righe)
2. Rimuovere funzioni legacy in ai_service.py
3. Rimuovere funzioni private inutilizzate in utils/

### Fase 4: Refactoring Duplicazioni (2 ore)
1. Creare helper per CSS bottoni download
2. Creare helper per box statistiche
3. Creare helper per config grafici Plotly
4. Creare helper per export Excel

### Fase 5: Ottimizzazioni (1 ora)
1. Consolidare regex in constants.py
2. Rimuovere time.sleep non necessari
3. Spostare import a livello modulo
4. Rimuovere chiamate cache_clear duplicate

---

## 📊 IMPATTO STIMATO

| Metrica | Prima | Dopo | Δ |
|---------|-------|------|---|
| Righe totali app.py | ~4818 | ~4200 | -13% |
| Righe totali admin.py | ~2415 | ~1900 | -21% |
| Import inutilizzati | ~50 | 0 | -100% |
| Tempo caricamento | ~3s | ~2.5s | -17% |
| Manutenibilità | Media | Alta | ⬆️ |

---

**Fine Report**

*Generato da GitHub Copilot - Analisi Debug Approfondita*
