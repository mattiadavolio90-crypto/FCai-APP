"""
Script per eseguire migration 008: Aggiungi campo verified a prodotti_master
"""
import os
from supabase import create_client, Client

def run_migration():
    """Esegue migration 008"""
    # Carica credenziali
    url = os.environ.get("SUPABASE_URL") or input("SUPABASE_URL: ")
    key = os.environ.get("SUPABASE_KEY") or input("SUPABASE_KEY: ")
    
    supabase: Client = create_client(url, key)
    
    # Leggi migration SQL
    with open('migrations/008_add_verified_to_prodotti_master.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
    
    print("📝 Esecuzione migration 008...")
    print("=" * 60)
    print(sql)
    print("=" * 60)
    
    try:
        # Esegui SQL (nota: Supabase Python client non ha .rpc() per SQL raw)
        # Devi eseguirlo manualmente dal dashboard Supabase SQL Editor
        print("\n⚠️ IMPORTANTE:")
        print("Il Supabase Python client non supporta esecuzione SQL raw.")
        print("\n📋 COPIA il contenuto sopra ed eseguilo nel Supabase Dashboard:")
        print("   https://supabase.com/dashboard/project/[YOUR_PROJECT]/sql")
        print("\nOPPURE usa psql:")
        print(f"   psql {url} -c \"$(cat migrations/008_add_verified_to_prodotti_master.sql)\"")
        
        # Verifica se campo esiste (test)
        print("\n🔍 Verifica struttura tabella prodotti_master...")
        result = supabase.table('prodotti_master').select('*').limit(1).execute()
        
        if result.data:
            columns = list(result.data[0].keys())
            print(f"✅ Colonne attuali: {columns}")
            
            if 'verified' in columns:
                print("✅ Campo 'verified' presente!")
            else:
                print("⚠️ Campo 'verified' NON trovato - esegui migration manualmente")
        else:
            print("ℹ️ Tabella vuota, impossibile verificare struttura")
            
    except Exception as e:
        print(f"❌ Errore: {e}")

if __name__ == "__main__":
    run_migration()
