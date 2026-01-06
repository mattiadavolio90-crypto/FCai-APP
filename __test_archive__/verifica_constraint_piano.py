"""
🔍 VERIFICA CONSTRAINT PIANO - Supabase
==========================================
Script per identificare il constraint sul campo 'piano' nella tabella users
"""

import streamlit as st
from supabase import create_client, Client

print("=" * 60)
print("🔍 VERIFICA CONSTRAINT PIANO")
print("=" * 60)

try:
    # Connetti a Supabase
    supabase_url = st.secrets["supabase"]["url"]
    supabase_key = st.secrets["supabase"]["key"]
    supabase: Client = create_client(supabase_url, supabase_key)
    
    print("\n✅ Connesso a Supabase")
    print(f"URL: {supabase_url}\n")
    
    # Query per vedere i valori attuali di 'piano' nel database
    print("📊 VALORI ATTUALI DEL CAMPO 'piano' NEL DATABASE:")
    print("-" * 60)
    
    response = supabase.table('users').select('email, piano').execute()
    
    if response.data:
        piani_esistenti = {}
        for user in response.data:
            piano = user.get('piano', 'NULL')
            if piano not in piani_esistenti:
                piani_esistenti[piano] = 0
            piani_esistenti[piano] += 1
        
        print(f"Totale utenti: {len(response.data)}\n")
        print("Valori 'piano' trovati:")
        for piano, count in sorted(piani_esistenti.items()):
            print(f"  • '{piano}': {count} utenti")
    else:
        print("⚠️  Nessun utente trovato nel database")
    
    print("\n" + "=" * 60)
    print("💡 SOLUZIONE:")
    print("=" * 60)
    print("\nSe vedi valori diversi da 'base', 'premium', 'enterprise',")
    print("devi usare QUEI valori nel dropdown del pannello admin.")
    print("\nOppure esegui questa query su Supabase SQL Editor:")
    print("\n-- Vedi il constraint attuale")
    print("SELECT constraint_name, check_clause")
    print("FROM information_schema.check_constraints")
    print("WHERE constraint_name = 'users_piano_check';")
    print("\n-- Se vuoi accettare i valori: base, premium, enterprise")
    print("ALTER TABLE users DROP CONSTRAINT IF EXISTS users_piano_check;")
    print("ALTER TABLE users ADD CONSTRAINT users_piano_check")
    print("  CHECK (piano IN ('base', 'premium', 'enterprise'));")
    
except Exception as e:
    print(f"\n❌ ERRORE: {e}")
    print("\nVerifica:")
    print("  1. Che secrets.toml sia configurato correttamente")
    print("  2. Che la connessione a Supabase funzioni")

print("\n" + "=" * 60)
