import os
from supabase import create_client
import pandas as pd
import toml

# Carica secrets da file .streamlit/secrets.toml
secrets_path = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")
try:
    secrets = toml.load(secrets_path)
    SUPABASE_URL = secrets["supabase"]["url"]
    SUPABASE_KEY = secrets["supabase"]["key"]
    print(f"✅ Secrets caricati da: {secrets_path}")
except Exception as e:
    print(f"❌ Errore caricamento secrets: {e}")
    print(f"ℹ️ Percorso cercato: {secrets_path}")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Cerca prodotto specifico
print("🔍 Cercando 'COPPETTA SANGO' nel database...")

# Query per trovare il prodotto con tutti i dettagli
result = supabase.table("fatture").select("*").ilike("descrizione", "%COPPETTA%SANGO%").execute()

if result.data:
    df = pd.DataFrame(result.data)
    print(f"\n✅ Trovate {len(df)} righe con 'COPPETTA SANGO':\n")
    
    for idx, row in df.iterrows():
        print(f"Riga {idx + 1}:")
        print(f"  Descrizione: '{row['descrizione']}'")
        print(f"  Fornitore: '{row.get('fornitore', 'N/A')}'")
        print(f"  Categoria: '{row['categoria']}'")
        print(f"  needs_review: {row.get('needs_review', 'N/A')}")
        print(f"  Categoria type: {type(row['categoria'])}")
        print(f"  Categoria is None: {row['categoria'] is None}")
        print(f"  User ID: {row['user_id']}")
        print()
else:
    print("❌ Nessuna riga trovata")

# Prova anche ricerca esatta
print("\n🔍 Ricerca esatta...")
result2 = supabase.table("fatture").select("*").eq("descrizione", "COPPETTA SANGO 10CM WB").execute()
if result2.data:
    print(f"✅ Trovate {len(result2.data)} righe con match esatto")
    for row in result2.data:
        print(f"  Fornitore: '{row.get('fornitore', 'N/A')}'")
        print(f"  needs_review: {row.get('needs_review', 'N/A')}")
else:
    print("❌ Nessun match esatto")
