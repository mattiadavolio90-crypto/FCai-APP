"""
🔍 DIAGNOSI COMPLETA SCHEMA SUPABASE
=====================================
Esegue query diagnostiche per identificare:
- Problema constraint campo piano
- Problema hash duplicato
- Tipo colonne
"""

import streamlit as st
from supabase import create_client

def main():
    st.set_page_config(page_title="Diagnosi Supabase", page_icon="🔍", layout="wide")
    
    st.title("🔍 Diagnosi Schema Supabase")
    st.write("---")
    
    try:
        # Connetti a Supabase
        supabase = create_client(
            st.secrets["supabase"]["url"],
            st.secrets["supabase"]["key"]
        )
        
        st.success("✅ Connesso a Supabase")
        
        # ========================================
        # 1️⃣ VALORI ATTUALI NEL DATABASE
        # ========================================
        st.header("1️⃣ Utenti Attuali nel Database")
        
        try:
            response = supabase.table('users').select('id, email, piano, password_hash, created_at').order('created_at', desc=True).limit(10).execute()
            
            if response.data:
                st.write(f"**Totale utenti (ultimi 10):** {len(response.data)}")
                
                for user in response.data:
                    with st.expander(f"👤 {user['email']} - Piano: {user['piano']}"):
                        st.write(f"**ID:** {user['id']}")
                        st.write(f"**Email:** {user['email']}")
                        st.write(f"**Piano:** `{user['piano']}`")
                        st.write(f"**Created:** {user['created_at']}")
                        st.write("")
                        
                        # Analisi hash
                        hash_val = user['password_hash']
                        st.write("**🔐 Analisi Password Hash:**")
                        st.write(f"- Primi 50 char: `{hash_val[:50]}`")
                        st.write(f"- Lunghezza totale: `{len(hash_val)}`")
                        st.write(f"- Inizia con '$argon2': `{hash_val.startswith('$argon2')}`")
                        st.write(f"- Caratteri '$' trovati: `{hash_val.count('$')}`")
                        
                        # Diagnosi
                        if hash_val.startswith('$argon2') and hash_val.count('$') == 5:
                            st.success("✅ Hash corretto!")
                        elif hash_val.startswith('argon2id'):
                            st.error("❌ PROBLEMA: Hash inizia con 'argon2id' invece di '$argon2id$'")
                            st.write("🐛 Possibile causa: '$' viene rimosso durante l'inserimento")
                        elif 'argon2idargon2id' in hash_val:
                            st.error("❌ PROBLEMA GRAVE: Hash duplicato!")
                            st.write("🐛 Possibile causa: doppia concatenazione del prefisso")
                        else:
                            st.warning("⚠️ Hash in formato sconosciuto")
            else:
                st.info("ℹ️ Nessun utente trovato nel database")
                
        except Exception as e:
            st.error(f"❌ Errore query utenti: {e}")
        
        st.write("---")
        
        # ========================================
        # 2️⃣ VALORI DISTINTI PIANO
        # ========================================
        st.header("2️⃣ Valori Campo Piano")
        
        try:
            response = supabase.table('users').select('piano').execute()
            
            if response.data:
                piani = {}
                for user in response.data:
                    piano_val = user['piano']
                    piani[piano_val] = piani.get(piano_val, 0) + 1
                
                st.write("**Valori distinti trovati:**")
                for piano, count in sorted(piani.items(), key=lambda x: x[1], reverse=True):
                    st.write(f"- `{piano}` (maiuscolo: {piano.isupper()}, lowercase: {piano.islower()}) → {count} utenti")
                    
                    if piano.isupper():
                        st.warning(f"⚠️ Trovato valore UPPERCASE: '{piano}'")
                        st.write("🛠️ Il constraint potrebbe richiedere lowercase")
                
        except Exception as e:
            st.error(f"❌ Errore query piani: {e}")
        
        st.write("---")
        
        # ========================================
        # 3️⃣ TEST INSERIMENTO
        # ========================================
        st.header("3️⃣ Test Inserimento (Simulazione)")
        
        st.write("**Test dati che verrebbero inviati:**")
        
        test_data = {
            'email': 'test-debug@example.com',
            'password_hash': '$argon2id$v=19$m=65536,t=3,p=4$test',
            'nome_ristorante': 'Test Debug',
            'piano': 'base',
            'ruolo': 'cliente',
            'attivo': True
        }
        
        st.json(test_data)
        
        st.write("**Validazioni:**")
        st.write(f"- Hash inizia con '$argon2': `{test_data['password_hash'].startswith('$argon2')}`")
        st.write(f"- Piano lowercase: `{test_data['piano'].islower()}`")
        st.write(f"- Caratteri '$' nell'hash: `{test_data['password_hash'].count('$')}`")
        
        if st.button("🚀 Esegui Test Inserimento Reale"):
            try:
                # Elimina se esiste già
                supabase.table('users').delete().eq('email', test_data['email']).execute()
                
                # Inserisci
                response = supabase.table('users').insert(test_data).execute()
                
                if response.data:
                    st.success("✅ Inserimento riuscito!")
                    st.write("Dati inseriti:")
                    st.json(response.data[0])
                    
                    # Rileggi dal database per verificare
                    verify = supabase.table('users').select('*').eq('email', test_data['email']).execute()
                    
                    if verify.data:
                        st.write("**🔍 Verifica - Dati riletti dal database:**")
                        riletto = verify.data[0]
                        
                        st.write(f"- Hash salvato (primi 50): `{riletto['password_hash'][:50]}`")
                        st.write(f"- Hash corretto: `{riletto['password_hash'].startswith('$argon2')}`")
                        st.write(f"- Piano salvato: `{riletto['piano']}`")
                        
                        # Confronto
                        if riletto['password_hash'] == test_data['password_hash']:
                            st.success("✅ Hash salvato correttamente (identico all'originale)")
                        else:
                            st.error("❌ PROBLEMA: Hash modificato durante salvataggio!")
                            st.write(f"**Inviato:** `{test_data['password_hash'][:50]}`")
                            st.write(f"**Salvato:** `{riletto['password_hash'][:50]}`")
                            
                        if riletto['piano'] == test_data['piano']:
                            st.success("✅ Piano salvato correttamente")
                        else:
                            st.error(f"❌ Piano modificato: '{test_data['piano']}' → '{riletto['piano']}'")
                            
                else:
                    st.error("❌ Inserimento fallito (nessun dato restituito)")
                    
            except Exception as e:
                st.error(f"❌ ERRORE durante inserimento: {e}")
                st.write("**Dettagli errore completo:**")
                st.exception(e)
                
                if 'piano' in str(e).lower():
                    st.warning("⚠️ Errore relativo al campo PIANO")
                    st.write("🛠️ **Possibile soluzione:**")
                    st.code("""
-- Rimuovi temporaneamente il constraint:
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_piano_check;

-- Poi ri-crealo con valori lowercase:
ALTER TABLE users ADD CONSTRAINT users_piano_check 
    CHECK (piano IN ('base', 'premium', 'enterprise'));
                    """)
        
        st.write("---")
        
        # ========================================
        # 4️⃣ QUERY SQL DA ESEGUIRE SU DASHBOARD
        # ========================================
        st.header("4️⃣ Query SQL per Supabase Dashboard")
        
        st.write("Se le query Python non bastano, esegui queste su **Supabase Dashboard → SQL Editor:**")
        
        with st.expander("📋 Query 1: Verifica Constraint Piano"):
            st.code("""
SELECT 
    constraint_name, 
    check_clause 
FROM information_schema.check_constraints 
WHERE table_name = 'users' 
AND constraint_name LIKE '%piano%';
            """)
        
        with st.expander("📋 Query 2: Dettagli Colonna Piano"):
            st.code("""
SELECT 
    column_name, 
    data_type, 
    column_default,
    is_nullable,
    character_maximum_length
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name = 'piano';
            """)
        
        with st.expander("📋 Query 3: Tutti i Constraint"):
            st.code("""
SELECT 
    tc.constraint_name, 
    tc.constraint_type,
    cc.check_clause
FROM information_schema.table_constraints tc
LEFT JOIN information_schema.check_constraints cc 
    ON tc.constraint_name = cc.constraint_name
WHERE tc.table_name = 'users'
ORDER BY tc.constraint_type;
            """)
        
        with st.expander("📋 Query 4: Dettagli Colonna Password Hash"):
            st.code("""
SELECT 
    column_name, 
    data_type, 
    character_maximum_length,
    is_nullable
FROM information_schema.columns 
WHERE table_name = 'users' 
AND column_name = 'password_hash';
            """)
        
        with st.expander("🛠️ Fix: Rimuovi Constraint Piano"):
            st.code("""
-- ⚠️ USA SOLO SE BLOCCA L'INSERIMENTO
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_piano_check;

-- Poi ri-crea con valori lowercase:
ALTER TABLE users ADD CONSTRAINT users_piano_check 
    CHECK (piano IN ('base', 'premium', 'enterprise'));
            """)
        
    except Exception as e:
        st.error(f"⛔ Errore connessione Supabase: {e}")
        st.write("Verifica che `.streamlit/secrets.toml` contenga le credenziali corrette")

if __name__ == "__main__":
    main()
