"""
Verifica dati utente davide.pizzata.78@gmail.com
"""
import toml
from supabase import create_client
import pandas as pd

# Carica secrets
secrets = toml.load(".streamlit/secrets.toml")
supabase_url = secrets.get("supabase", {}).get("url")
supabase_key = secrets.get("supabase", {}).get("key")

supabase = create_client(supabase_url, supabase_key)

print("\n" + "="*80)
print("🔍 VERIFICA DATI UTENTE davide.pizzata.78@gmail.com")
print("="*80 + "\n")

# Query tutte le fatture
response = supabase.table("fatture").select("*").execute()

if response.data:
    df = pd.DataFrame(response.data)
    
    print(f"✅ Totale righe database: {len(df)}")
    print(f"✅ Colonne presenti: {', '.join(df.columns.tolist()[:10])}...")
    print(f"✅ Numero utenti: {df['user_id'].nunique()}")
    
    # Trova l'utente davide
    user_counts = df['user_id'].value_counts()
    
    print("\n📊 RIGHE PER UTENTE:")
    for user_id, count in user_counts.items():
        print(f"  👤 {user_id[:8]}...: {count} righe")
    
    # Controlla righe con prezzo €0
    df_zero = df[df['prezzo_unitario'] == 0]
    print(f"\n💰 Totale righe con prezzo €0: {len(df_zero)}")
    
    if len(df_zero) > 0:
        print("\n📋 BREAKDOWN RIGHE €0 PER UTENTE:")
        for user_id, count in df_zero['user_id'].value_counts().items():
            fatture_count = len(df_zero[df_zero['user_id'] == user_id]['numero_fattura'].unique())
            print(f"  👤 {user_id[:8]}...: {count} righe €0, {fatture_count} fatture")
        
        # Mostra esempi
        print("\n📋 ESEMPI RIGHE €0:")
        cols_display = ['descrizione_prodotto', 'categoria', 'fornitore', 'needs_review', 'user_id']
        print(df_zero[cols_display].head(10).to_string(index=False))
    
    # Controlla campo needs_review
    if 'needs_review' in df.columns:
        df_review = df[df['needs_review'] == True]
        print(f"\n🔍 Righe con needs_review=True: {len(df_review)}")
    else:
        print("\n⚠️ Campo 'needs_review' NON presente nel database!")
    
else:
    print("❌ Nessun dato trovato nel database")

print("\n" + "="*80)
