"""
Script per cancellare TUTTA la memoria AI dal database.
Cancella:
1. prodotti_master (memoria globale condivisa)
2. prodotti_utente (memorie personalizzate per cliente)
"""

import os
import toml
from supabase import create_client

# Carica credenziali
secrets_path = os.path.join(os.path.dirname(__file__), '.streamlit', 'secrets.toml')
secrets = toml.load(secrets_path)
SUPABASE_URL = secrets["supabase"]["url"]
SUPABASE_KEY = secrets["supabase"]["key"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("CANCELLAZIONE MEMORIA GLOBALE AI")
print("=" * 80)

# 1. Conta prodotti master
print("\n📊 Analisi memoria...")
try:
    master_response = supabase.table('prodotti_master')\
        .select('id', count='exact')\
        .execute()
    master_count = master_response.count if master_response.count else 0
    print(f"  📚 Prodotti Master (memoria globale): {master_count}")
except Exception as e:
    print(f"  ❌ Errore lettura master: {e}")
    master_count = 0

# 2. Conta prodotti utente
try:
    utente_response = supabase.table('prodotti_utente')\
        .select('id', count='exact')\
        .execute()
    utente_count = utente_response.count if utente_response.count else 0
    print(f"  👤 Prodotti Utente (personali): {utente_count}")
except Exception as e:
    print(f"  ❌ Errore lettura utente: {e}")
    utente_count = 0

total = master_count + utente_count
print(f"\n  ⚠️  TOTALE DA CANCELLARE: {total} righe")

if total == 0:
    print("\n✅ La memoria AI è già vuota!")
    exit()

# 3. Conferma cancellazione
print("\n" + "=" * 80)
print("⚠️  ATTENZIONE: QUESTA OPERAZIONE NON PUÒ ESSERE ANNULLATA!")
print("=" * 80)

conferma = input(f"\nDigita 'CANCELLA' per eliminare TUTTA la memoria ({total} righe): ").strip()

if conferma != 'CANCELLA':
    print("\n❌ Operazione annullata.")
    exit()

# 4. Cancella prodotti_master
print("\n🔄 Cancellazione memoria globale...")
try:
    # Cancella TUTTI i record (usando un filtro sempre vero)
    # Metodo: cancella in base a un campo che esiste sempre
    master_response = supabase.table('prodotti_master').select('id').execute()
    
    if master_response.data:
        for row in master_response.data:
            supabase.table('prodotti_master').delete().eq('id', row['id']).execute()
        
        # Verifica
        verify = supabase.table('prodotti_master').select('id', count='exact').execute()
        remaining = verify.count if verify.count else 0
        
        if remaining == 0:
            print(f"  ✅ Cancellati {master_count} prodotti master")
        else:
            print(f"  ⚠️  Rimasti {remaining} prodotti master")
    else:
        print(f"  ✅ Nessun prodotto master da cancellare")
            
except Exception as e:
    print(f"  ❌ Errore cancellazione master: {e}")

# 5. Cancella prodotti_utente
print("\n🔄 Cancellazione memoria utente...")
try:
    utente_response = supabase.table('prodotti_utente')\
        .select('id')\
        .execute()
    
    if utente_response.data:
        utente_ids = [row['id'] for row in utente_response.data]
        
        for pid in utente_ids:
            supabase.table('prodotti_utente').delete().eq('id', pid).execute()
        
        # Verifica cancellazione
        verify = supabase.table('prodotti_utente').select('id', count='exact').execute()
        remaining = verify.count if verify.count else 0
        
        if remaining == 0:
            print(f"  ✅ Cancellati {utente_count} prodotti utente")
        else:
            print(f"  ⚠️  Rimasti {remaining} prodotti utente")
            
except Exception as e:
    print(f"  ❌ Errore cancellazione utente: {e}")

# 6. Riepilogo finale
print("\n" + "=" * 80)
print("✅ MEMORIA AI COMPLETAMENTE CANCELLATA!")
print("=" * 80)
print("\nLa memoria AI ricomincia da zero.")
print("I nuovi prodotti caricati verranno riclassificati da zero.")
