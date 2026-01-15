"""
Script per verificare righe €0 per TUTTI gli utenti
"""
import toml
from supabase import create_client
import pandas as pd

# Carica secrets
secrets = toml.load(".streamlit/secrets.toml")
supabase_url = secrets.get("supabase", {}).get("url")
supabase_key = secrets.get("supabase", {}).get("key")  # Usa la key normale, non service_role

supabase = create_client(supabase_url, supabase_key)

print("\n" + "="*80)
print("🔍 VERIFICA RIGHE €0 PER TUTTI GLI UTENTI")
print("="*80 + "\n")

# Query per trovare tutte le righe con prezzo €0 O needs_review=true
response = supabase.table("fatture") \
    .select("*") \
    .or_('prezzo_unitario.eq.0,needs_review.eq.true') \
    .execute()

if response.data:
    df = pd.DataFrame(response.data)
    
    print(f"✅ Totale righe con €0 O needs_review=True: {len(df)}")
    print(f"✅ Numero fatture uniche: {df['numero_fattura'].nunique()}")
    print(f"✅ Numero utenti coinvolti: {df['user_id'].nunique()}")
    
    # Breakdown per user
    print("\n📊 BREAKDOWN PER UTENTE:")
    user_stats = df.groupby('user_id').agg({
        'id': 'count',
        'numero_fattura': 'nunique'
    }).rename(columns={'id': 'righe', 'numero_fattura': 'fatture'})
    
    for user_id, row in user_stats.iterrows():
        # Prendi email utente
        user_response = supabase.auth.admin.get_user_by_id(user_id)
        email = user_response.user.email if user_response.user else "N/A"
        print(f"  👤 {email[:30]}: {row['righe']} righe, {row['fatture']} fatture")
    
    # Statistiche needs_review
    print(f"\n💰 Righe con prezzo €0: {len(df[df['prezzo_unitario'] == 0])}")
    print(f"🔍 Righe con needs_review=True: {len(df[df['needs_review'] == True])}")
    
    # Mostra prime 10 righe
    print("\n📋 PRIME 10 RIGHE DA REVISIONARE:")
    cols_display = ['descrizione_prodotto', 'prezzo_unitario', 'categoria', 'needs_review', 'user_id']
    print(df[cols_display].head(10).to_string(index=False))
    
else:
    print("❌ Nessuna riga con €0 o needs_review=True trovata nel database")

print("\n" + "="*80)
