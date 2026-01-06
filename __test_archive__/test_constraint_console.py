"""
🔍 Test Constraint Piano - Versione Console
===========================================
"""

import sys
sys.path.insert(0, '.')

try:
    import streamlit as st
    from supabase import create_client
    
    # Carica secrets
    import toml
    with open('.streamlit/secrets.toml', 'r') as f:
        secrets = toml.load(f)
    
    supabase = create_client(
        secrets["supabase"]["url"],
        secrets["supabase"]["key"]
    )
    
    print("=" * 60)
    print("🔍 TEST CONSTRAINT PIANO")
    print("=" * 60)
    
    test_email = "constraint-test@example.com"
    
    try:
        # Elimina se esiste
        print(f"\n🗑️  Rimuovo eventuale utente test esistente...")
        supabase.table('users').delete().eq('email', test_email).execute()
        
        # Prova inserimento con piano='base'
        print(f"\n✏️  Tento inserimento con piano='base'...")
        response = supabase.table('users').insert({
            'email': test_email,
            'password_hash': '$argon2id$v=19$m=65536,t=3,p=4$test',
            'nome_ristorante': 'Test Constraint',
            'piano': 'base',
            'ruolo': 'cliente',
            'attivo': True
        }).execute()
        
        if response.data:
            print("\n✅ SUCCESSO! Inserimento con piano='base' FUNZIONA!")
            print(f"   Valore accettato: 'base' (lowercase)")
            print(f"\n📊 Dati inseriti:")
            print(f"   Email: {response.data[0]['email']}")
            print(f"   Piano: {response.data[0]['piano']}")
            print(f"   Hash: {response.data[0]['password_hash'][:50]}...")
            
            # Pulisci
            print(f"\n🧹 Pulizia utente test...")
            supabase.table('users').delete().eq('email', test_email).execute()
            print("   ✅ Pulito")
        else:
            print("\n❌ ERRORE: Inserimento fallito (nessun dato restituito)")
            
    except Exception as e:
        print(f"\n❌ ERRORE durante inserimento:")
        print(f"   {str(e)}")
        
        if 'piano' in str(e).lower() or 'check' in str(e).lower():
            print(f"\n⚠️  Il constraint piano sta bloccando l'inserimento!")
            print(f"\n🛠️  SOLUZIONE: Esegui su Supabase SQL Editor:")
            print(f"   ALTER TABLE users DROP CONSTRAINT IF EXISTS users_piano_check;")
    
    print("\n" + "=" * 60)
    print("ℹ️  Per vedere il constraint esatto, esegui su Supabase:")
    print("=" * 60)
    print("""
SELECT check_clause 
FROM information_schema.check_constraints 
WHERE constraint_name = 'users_piano_check';
    """)
    print("=" * 60)
    
except ImportError as e:
    print(f"❌ Errore import: {e}")
    print("Installa: pip install toml")
except Exception as e:
    print(f"❌ Errore: {e}")
