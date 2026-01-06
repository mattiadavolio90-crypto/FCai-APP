"""
Script per verificare la struttura della tabella fatture su Supabase
"""
import os
import toml
from supabase import create_client

# Carica configurazione da .streamlit/secrets.toml
secrets_path = os.path.join(os.path.dirname(__file__), '.streamlit', 'secrets.toml')
if os.path.exists(secrets_path):
    secrets = toml.load(secrets_path)
    SUPABASE_URL = secrets.get("SUPABASE_URL")
    SUPABASE_KEY = secrets.get("SUPABASE_KEY")
else:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Manca configurazione Supabase")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("🔍 VERIFICA STRUTTURA TABELLA FATTURE")
print("=" * 80)

try:
    # Prova a leggere una riga per vedere tutte le colonne
    response = supabase.table("fatture").select("*").limit(1).execute()
    
    if response.data and len(response.data) > 0:
        print("\n✅ Colonne disponibili nella tabella:")
        print("-" * 80)
        for col in sorted(response.data[0].keys()):
            print(f"  - {col}")
        
        # Verifica specifiche per le nuove colonne
        print("\n📊 Verifica nuove colonne:")
        print("-" * 80)
        row = response.data[0]
        
        if 'peso_unitario' in row:
            print(f"  ✅ peso_unitario presente (valore: {row['peso_unitario']})")
        else:
            print(f"  ❌ peso_unitario NON presente")
        
        if 'prezzo_standard_kg' in row:
            print(f"  ✅ prezzo_standard_kg presente (valore: {row['prezzo_standard_kg']})")
        else:
            print(f"  ❌ prezzo_standard_kg NON presente")
        
    else:
        print("⚠️ Tabella vuota, impossibile verificare struttura")
        print("💡 Carica almeno una fattura per vedere le colonne")

except Exception as e:
    print(f"❌ Errore: {e}")

print("\n" + "=" * 80)
