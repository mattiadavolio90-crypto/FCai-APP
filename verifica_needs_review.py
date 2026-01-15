"""
Script di verifica per testare la funzione needs_review.
Controlla le righe con prezzo €0 nelle fatture caricate.
"""

import os
import sys
from pathlib import Path
import toml

# Aggiungi il percorso del progetto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from supabase import create_client
import pandas as pd

# Carica secrets.toml
try:
    secrets_path = project_root / ".streamlit" / "secrets.toml"
    secrets = toml.load(secrets_path)
    SUPABASE_URL = secrets.get("supabase", {}).get("url") or secrets.get("SUPABASE_URL")
    SUPABASE_KEY = secrets.get("supabase", {}).get("key") or secrets.get("SUPABASE_KEY")
except Exception as e:
    print(f"❌ ERRORE caricamento secrets.toml: {e}")
    sys.exit(1)

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ ERRORE: Credenziali Supabase mancanti")
    print(f"secrets.toml path: {secrets_path}")
    print(f"URL presente: {bool(SUPABASE_URL)}")
    print(f"KEY presente: {bool(SUPABASE_KEY)}")
    sys.exit(1)

# Crea client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# User ID da verificare (utente che ha caricato le 16 fatture)
USER_ID = "349027d1-3ed1-4b53-b75b-7104dc65db76"

print("=" * 70)
print("🔍 VERIFICA FUNZIONE needs_review")
print("=" * 70)
print()

# Query 1: Statistiche generali utente
print("📊 STATISTICHE UTENTE")
print("-" * 70)

try:
    response = supabase.table('fatture')\
        .select('*', count='exact')\
        .eq('user_id', USER_ID)\
        .execute()
    
    total_rows = response.count
    print(f"✅ Totale righe fatture: {total_rows}")
    
    if total_rows > 0:
        df_all = pd.DataFrame(response.data)
        num_fatture = df_all['file_origine'].nunique()
        print(f"✅ Numero fatture uniche: {num_fatture}")
        
        # Conta per categoria
        print(f"\n📋 Righe per categoria:")
        cat_counts = df_all['categoria'].value_counts()
        for cat, count in cat_counts.head(10).items():
            print(f"   {cat}: {count}")
        
        # Conta righe €0
        righe_zero = len(df_all[df_all['prezzo_unitario'] == 0])
        print(f"\n💰 Righe con prezzo €0: {righe_zero}")
        
        # Conta needs_review
        if 'needs_review' in df_all.columns:
            righe_review = len(df_all[df_all['needs_review'] == True])
            print(f"🔍 Righe con needs_review=True: {righe_review}")
        else:
            print("⚠️ Colonna 'needs_review' NON PRESENTE nel DataFrame!")
            
    else:
        print("⚠️ Nessuna fattura trovata per questo utente")
        sys.exit(0)
        
except Exception as e:
    print(f"❌ Errore caricamento dati: {e}")
    sys.exit(1)

print()
print("=" * 70)
print("🔍 DETTAGLIO RIGHE €0 CON needs_review")
print("=" * 70)
print()

# Query 2: Righe €0 con dettagli needs_review
try:
    response_zero = supabase.table('fatture')\
        .select('descrizione, prezzo_unitario, categoria, needs_review, file_origine')\
        .eq('user_id', USER_ID)\
        .eq('prezzo_unitario', 0)\
        .order('file_origine')\
        .limit(50)\
        .execute()
    
    if response_zero.data:
        df_zero = pd.DataFrame(response_zero.data)
        
        print(f"📌 Trovate {len(df_zero)} righe con prezzo €0\n")
        
        # Mostra dettaglio
        for idx, row in df_zero.iterrows():
            desc = row['descrizione'][:60] + "..." if len(row['descrizione']) > 60 else row['descrizione']
            cat = row['categoria']
            needs_rev = row.get('needs_review', 'N/A')
            file = row['file_origine']
            
            badge = "🔍" if needs_rev == True else "✅" if needs_rev == False else "❓"
            
            print(f"{badge} {desc}")
            print(f"   Categoria: {cat}")
            print(f"   needs_review: {needs_rev}")
            print(f"   File: {file}")
            print()
        
        # Statistiche
        print("-" * 70)
        if 'needs_review' in df_zero.columns:
            review_true = len(df_zero[df_zero['needs_review'] == True])
            review_false = len(df_zero[df_zero['needs_review'] == False])
            review_null = len(df_zero[df_zero['needs_review'].isna()])
            
            print(f"\n📊 RIEPILOGO needs_review:")
            print(f"   🔍 True (da validare): {review_true}")
            print(f"   ✅ False (normale): {review_false}")
            print(f"   ❓ NULL/NA: {review_null}")
            
            if review_true > 0:
                print(f"\n✅ SUCCESSO: Funzione needs_review attiva!")
                print(f"   {review_true} righe marcate per review in Admin Panel")
            else:
                print(f"\n⚠️ ATTENZIONE: Nessuna riga marcata needs_review=True")
                print("   Possibili cause:")
                print("   - Le righe €0 sono già categorizzate correttamente (omaggi)")
                print("   - Non ci sono diciture nelle fatture caricate")
        else:
            print("⚠️ Colonna 'needs_review' mancante!")
            
    else:
        print("✅ Nessuna riga con prezzo €0 trovata")
        print("   Le 16 fatture caricate non hanno righe a prezzo zero")
        
except Exception as e:
    print(f"❌ Errore query righe €0: {e}")
    sys.exit(1)

print()
print("=" * 70)
print("🎯 VERIFICA COMPLETATA")
print("=" * 70)
