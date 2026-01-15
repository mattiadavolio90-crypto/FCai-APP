import os
from supabase import create_client
import toml

# Carica secrets
secrets_path = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")
secrets = toml.load(secrets_path)
SUPABASE_URL = secrets["supabase"]["url"]
SUPABASE_KEY = secrets["supabase"]["key"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Parametri
user_id = "df4e89fa-4a93-46e8-9924-85bb7d840a49"
descrizione = "COPPETTA SANGO 10CM WB"
categoria = "ALTRO FOOD"

print(f"🔄 Aggiornamento forzato:")
print(f"   User: {user_id}")
print(f"   Descrizione: {descrizione}")
print(f"   Categoria: {categoria}\n")

# TENTATIVO 1: Match esatto
print("TENTATIVO 1: Match esatto...")
result = supabase.table("fatture").update(
    {"categoria": categoria}
).eq("user_id", user_id).eq("descrizione", descrizione).execute()

num_aggiornate = len(result.data) if result.data else 0
print(f"   Righe aggiornate: {num_aggiornate}")

if num_aggiornate == 0:
    # TENTATIVO 2: Con trim
    print("\nTENTATIVO 2: Con trim...")
    desc_trimmed = descrizione.strip()
    result2 = supabase.table("fatture").update(
        {"categoria": categoria}
    ).eq("user_id", user_id).eq("descrizione", desc_trimmed).execute()
    
    num_aggiornate = len(result2.data) if result2.data else 0
    print(f"   Righe aggiornate: {num_aggiornate}")

if num_aggiornate == 0:
    # TENTATIVO 3: ILIKE
    print("\nTENTATIVO 3: ILIKE...")
    result3 = supabase.table("fatture").update(
        {"categoria": categoria}
    ).eq("user_id", user_id).ilike("descrizione", f"%{descrizione.strip()}%").execute()
    
    num_aggiornate = len(result3.data) if result3.data else 0
    print(f"   Righe aggiornate: {num_aggiornate}")

if num_aggiornate > 0:
    print(f"\n✅ SUCCESSO! Aggiornate {num_aggiornate} righe")
    
    # Verifica
    verify = supabase.table("fatture").select("descrizione, categoria").eq("descrizione", descrizione).execute()
    if verify.data:
        print(f"\n📋 Verifica:")
        for row in verify.data:
            print(f"   Descrizione: '{row['descrizione']}'")
            print(f"   Categoria: '{row['categoria']}'")
else:
    print("\n❌ NESSUNA RIGA AGGIORNATA!")
    
    # Debug: cerca il prodotto
    print("\n🔍 Debug: cerca prodotto...")
    search = supabase.table("fatture").select("*").eq("user_id", user_id).ilike("descrizione", "%COPPETTA%").execute()
    if search.data:
        print(f"   Trovate {len(search.data)} righe con 'COPPETTA'")
        for row in search.data:
            print(f"   - Desc: '{row['descrizione']}' (len={len(row['descrizione'])})")
            print(f"     Cat: '{row.get('categoria', 'N/A')}'")
            print(f"     User: {row['user_id']}")
