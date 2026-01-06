# 🚨 DIAGNOSI PROFONDA BUG - ISTRUZIONI IMMEDIATE
=====================================

## ✅ MODIFICHE APPLICATE

### 1️⃣ Debug Visibile nell'Interfaccia (pages/admin.py)

Ho aggiunto **output visibili con st.write()** durante la creazione utente:
- 🔐 Password generata
- 📝 Hash (primi 50 caratteri)
- ✅ Validazione hash (inizia con '$argon2')
- 🔢 Conteggio caratteri '$' (devono essere 5)
- 🎯 Piano (lowercase)
- 📤 Dati completi inviati al database (JSON)

**Quando crei un utente, vedrai TUTTO nell'interfaccia prima dell'inserimento.**

### 2️⃣ Test Hash all'Avvio

All'avvio di `pages/admin.py`, viene generato un hash di test e scritto in `admin.log`:
```
🧪 Test hash all'avvio: $argon2id$v=19$m=65536,t=3,p=4$...
✅ Hash valido: True
```

Controlla `admin.log` per vedere se l'hash viene generato correttamente.

### 3️⃣ File Creati

- **verifica_schema_supabase.sql** - Query SQL complete per dashboard Supabase
- **diagnosi_supabase.py** - Script Python interattivo per diagnosi

## 🚀 ISTRUZIONI IMMEDIATE

### STEP 1: Testa Creazione Utente con Debug Visibile

```powershell
# Avvia l'app
streamlit run app.py

# Vai su Admin Panel e prova a creare un utente test
# Email: debug-test@example.com
# Nome: Test Debug
# Piano: base
```

**Osserva l'interfaccia - vedrai:**
- 🔐 Password generata
- 📝 Hash generato (DEVE iniziare con '$argon2id$')
- ✅ Hash valido (DEVE essere True)
- 🔢 Caratteri '$' (DEVONO essere 5)
- 📤 Dati JSON da inserire

**Se vedi hash corretto nell'interfaccia MA errore nel database → problema Supabase**

### STEP 2: Esegui Script Diagnosi Python

```powershell
streamlit run diagnosi_supabase.py
```

Questo script:
1. ✅ Mostra utenti attuali e analizza i loro hash
2. ✅ Identifica se hash sono corrotti nel database
3. ✅ Mostra valori campo piano (uppercase/lowercase)
4. ✅ Permette test inserimento controllato
5. ✅ Fornisce query SQL da eseguire su dashboard

**Clicca "Esegui Test Inserimento Reale"** e verifica se:
- Hash inviato = Hash salvato
- Piano inviato = Piano salvato

### STEP 3: Esegui Query SQL su Supabase Dashboard

Vai su: **Supabase Dashboard → SQL Editor**

**Query Critica #1 - Constraint Piano:**
```sql
SELECT 
    constraint_name, 
    check_clause 
FROM information_schema.check_constraints 
WHERE table_name = 'users' 
AND constraint_name LIKE '%piano%';
```

**RISULTATO ATTESO:**
```
constraint_name: users_piano_check
check_clause: (piano IN ('base', 'premium', 'enterprise'))
```

**SE VEDI UPPERCASE ('BASE', 'PREMIUM') → È QUI IL PROBLEMA!**

**Query Critica #2 - Tipo Password Hash:**
```sql
SELECT 
    column_name, 
    data_type, 
    character_maximum_length
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name = 'password_hash';
```

**RISULTATO ATTESO:**
```
data_type: text
character_maximum_length: NULL (illimitato)
```

**SE vedi character_maximum_length = 100 o simile → PROBLEMA!**

### STEP 4: Fix Constraint Piano (se necessario)

Se il constraint usa UPPERCASE, esegui su Supabase:

```sql
-- Rimuovi constraint vecchio
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_piano_check;

-- Crea constraint con lowercase
ALTER TABLE users ADD CONSTRAINT users_piano_check 
    CHECK (piano IN ('base', 'premium', 'enterprise'));
```

### STEP 5: Fix Colonna Password Hash (se necessario)

Se la colonna è troppo corta:

```sql
ALTER TABLE users ALTER COLUMN password_hash TYPE TEXT;
```

## 🔍 COSA CERCARE

### Scenario 1: Hash Corretto in Python MA Sbagliato in Database
**Sintomo:** Debug mostra `$argon2id$...` ma database ha `argon2idargon2id...`
**Causa:** Problema encoding Supabase
**Soluzione:** Verifica tipo colonna, contatta supporto Supabase

### Scenario 2: Hash Corretto Ovunque MA Constraint Blocca
**Sintomo:** Hash OK, ma errore "users_piano_check"
**Causa:** Constraint richiede UPPERCASE ma codice invia lowercase
**Soluzione:** Fix constraint con query sopra

### Scenario 3: Hash Sbagliato Già in Python
**Sintomo:** Debug mostra hash malformato (non inizia con '$')
**Causa:** Bug libreria argon2-cffi
**Soluzione:** Reinstalla argon2-cffi
```powershell
pip uninstall argon2-cffi
pip install argon2-cffi==23.1.0
```

## 📋 CHECKLIST DIAGNOSI

Esegui IN ORDINE e segna ✅:

- [ ] Step 1: Crea utente e verifica debug visibile (hash corretto in interfaccia?)
- [ ] Step 2: Esegui `streamlit run diagnosi_supabase.py`
- [ ] Step 3: Esegui query SQL su Supabase Dashboard
- [ ] Step 4: Identifica dove il dato si corrompe:
  - [ ] Python genera hash corretto? (vedi debug interfaccia)
  - [ ] Database salva hash corretto? (vedi diagnosi_supabase.py)
  - [ ] Constraint piano è lowercase? (vedi query SQL)
- [ ] Step 5: Applica fix appropriato
- [ ] Step 6: Riprova creazione utente

## 🆘 REPORT DIAGNOSTICO

Dopo aver eseguito i test, riporta:

1. **Output debug interfaccia quando crei utente:**
   - Hash inizia con '$argon2'? (SI/NO)
   - Caratteri '$' nell'hash? (numero)

2. **Output diagnosi_supabase.py:**
   - Hash in database iniziano con '$argon2'? (SI/NO)
   - Valori campo piano sono lowercase? (SI/NO)

3. **Output query SQL Supabase:**
   - Check clause constraint piano: (COPIA RISULTATO)
   - Tipo colonna password_hash: (COPIA RISULTATO)

Con queste informazioni identificheremo ESATTAMENTE il problema!

## 📞 CONTATTI RAPIDI

Se tutto quanto sopra è corretto MA errore persiste:
→ Problema di encoding/configurazione Supabase
→ Contatta supporto Supabase con screenshot debug
