"""
🔍 VERIFICA HASH NEL DATABASE - Diagnosi Bug
=============================================
Script per vedere esattamente cosa è salvato nel database Supabase
"""

import streamlit as st
from supabase import create_client, Client

print("=" * 60)
print("🔍 VERIFICA HASH NEL DATABASE SUPABASE")
print("=" * 60)

try:
    # Connetti a Supabase
    supabase_url = st.secrets["supabase"]["url"]
    supabase_key = st.secrets["supabase"]["key"]
    supabase: Client = create_client(supabase_url, supabase_key)
    
    print("\n✅ Connesso a Supabase\n")
    
    # Recupera tutti gli utenti con hash
    print("📊 HASH SALVATI NEL DATABASE:")
    print("-" * 60)
    
    response = supabase.table('users').select('email, password_hash, piano, ruolo, created_at').execute()
    
    if response.data:
        for i, user in enumerate(response.data, 1):
            email = user.get('email', 'N/A')
            hash_value = user.get('password_hash', '')
            piano = user.get('piano', 'N/A')
            ruolo = user.get('ruolo', 'N/A')
            created = user.get('created_at', 'N/A')
            
            print(f"\n[{i}] Utente: {email}")
            print(f"    Ruolo: {ruolo}")
            print(f"    Piano: {piano}")
            print(f"    Created: {created[:10] if created != 'N/A' else 'N/A'}")
            print(f"\n    Password Hash:")
            
            if hash_value:
                print(f"    - Lunghezza: {len(hash_value)} caratteri")
                print(f"    - Primi 50: {hash_value[:50]}")
                print(f"    - Ultimi 20: ...{hash_value[-20:]}")
                
                # Analisi formato
                print(f"\n    Analisi:")
                
                # Check inizio
                if hash_value.startswith('$argon2'):
                    print(f"    ✅ Inizia con '$argon2'")
                elif hash_value.startswith('argon2'):
                    print(f"    ❌ INIZIA CON 'argon2' (manca il '$' iniziale!)")
                else:
                    print(f"    ❌ Formato sconosciuto: {hash_value[:20]}...")
                
                # Conta $
                dollar_count = hash_value.count('$')
                print(f"    - Numero '$': {dollar_count}")
                if dollar_count == 5:
                    print(f"      ✅ Corretto (5)")
                elif dollar_count == 0:
                    print(f"      ❌ ZERO '$' - hash completamente corrotto!")
                else:
                    print(f"      ⚠️  Anomalo (attesi 5, trovati {dollar_count})")
                
                # Check duplicazione
                if 'argon2idargon2id' in hash_value or 'argon2i$argon2i' in hash_value:
                    print(f"    🚨 DUPLICAZIONE RILEVATA!")
                
                # Parti
                if '$' in hash_value:
                    parts = hash_value.split('$')
                    print(f"\n    Parti (split '$'):")
                    for j, part in enumerate(parts[:6]):  # Prime 6 parti
                        if part:
                            display = part if len(part) <= 20 else f"{part[:20]}..."
                            print(f"      [{j}] {display}")
            else:
                print(f"    ⚠️  Hash vuoto o NULL!")
            
            print("-" * 60)
    else:
        print("⚠️  Nessun utente trovato nel database")
    
    print("\n" + "=" * 60)
    print("💡 DIAGNOSI:")
    print("=" * 60)
    
    print("""
Se vedi hash che iniziano con 'argon2' invece di '$argon2':
  → Il primo '$' viene rimosso durante il salvataggio

Se vedi 'argon2idargon2id':
  → C'è una concatenazione/duplicazione dell'hash

Se vedi numero '$' diverso da 5:
  → L'hash viene modificato prima o durante il salvataggio

AZIONI SUCCESSIVE:
1. Confronta con output di test_hash_argon2.py
2. Controlla i log dell'app (debug aggiunto in pages/admin.py)
3. Verifica tipo colonna su Supabase (deve essere TEXT)
    """)
    
except Exception as e:
    print(f"\n❌ ERRORE: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
