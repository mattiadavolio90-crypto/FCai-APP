"""
🔍 VERIFICA CONSTRAINT PIANO - Quick Check
==========================================
Script rapido per verificare quale constraint esiste sul campo piano
"""

import streamlit as st
from supabase import create_client

try:
    supabase = create_client(
        st.secrets["supabase"]["url"],
        st.secrets["supabase"]["key"]
    )
    
    st.title("🔍 Verifica Constraint Piano")
    
    st.write("**Test 1: Prova inserimento con piano='base'**")
    
    # Tenta inserimento test
    test_email = "constraint-test@example.com"
    
    try:
        # Elimina se esiste
        supabase.table('users').delete().eq('email', test_email).execute()
        
        # Prova inserimento con piano='base'
        response = supabase.table('users').insert({
            'email': test_email,
            'password_hash': '$argon2id$v=19$m=65536,t=3,p=4$test',
            'nome_ristorante': 'Test Constraint',
            'piano': 'base',
            'ruolo': 'cliente',
            'attivo': True
        }).execute()
        
        if response.data:
            st.success("✅ Inserimento con piano='base' FUNZIONA!")
            st.write("**Valore accettato:** `base` (lowercase)")
            
            # Pulisci
            supabase.table('users').delete().eq('email', test_email).execute()
        else:
            st.error("❌ Inserimento fallito")
            
    except Exception as e:
        st.error(f"❌ Errore: {e}")
        
        if 'piano' in str(e).lower() or 'check' in str(e).lower():
            st.warning("⚠️ Il constraint piano sta bloccando l'inserimento!")
            st.write("**Soluzione:** Esegui su Supabase SQL Editor:")
            st.code("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_piano_check;")
        
    st.write("---")
    st.write("**Constraint attuale:**")
    st.info("Se vuoi vedere il constraint esatto, esegui su Supabase SQL Editor:")
    st.code("""
SELECT check_clause 
FROM information_schema.check_constraints 
WHERE constraint_name = 'users_piano_check';
    """)
    
except Exception as e:
    st.error(f"Errore connessione: {e}")
