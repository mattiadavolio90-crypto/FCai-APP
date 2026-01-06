import streamlit as st
from supabase import create_client, Client

print("=" * 60)
print("🧪 TEST CONNESSIONE SUPABASE")
print("=" * 60)

try:
    # Leggi credenziali
    SUPABASE_URL = st.secrets["supabase"]["url"]
    SUPABASE_KEY = st.secrets["supabase"]["key"]
    
    print(f"📍 URL: {SUPABASE_URL}")
    print(f"🔑 Key: {SUPABASE_KEY[:20]}... (nascosta)")
    print()
    
    # Connetti
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Test query
    response = supabase.table('users').select("*", count='exact').execute()
    
    print("✅ CONNESSIONE RIUSCITA!")
    print(f"📊 Utenti nel database: {response.count}")
    print("=" * 60)
    print()
    print("🎉 Database pronto! Puoi procedere con lo Step 2.")
    
except KeyError as e:
    print(f"❌ ERRORE: Chiave mancante in secrets.toml")
    print(f"   Controlla che ci sia: {e}")
    
except Exception as e:
    print(f"❌ ERRORE CONNESSIONE:")
    print(f"   {e}")