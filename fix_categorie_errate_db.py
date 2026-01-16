"""
Script per correggere categorie errate in memoria globale.
Trova e corregge:
1. Categorie "FOOD" → applica dizionario
2. Bicchieri, coperchi classificati male → NO FOOD
"""

import os
import toml
from supabase import create_client
from services.ai_service import applica_correzioni_dizionario
from config.constants import TUTTE_LE_CATEGORIE

# Carica credenziali da secrets.toml
secrets_path = os.path.join(os.path.dirname(__file__), '.streamlit', 'secrets.toml')
secrets = toml.load(secrets_path)
SUPABASE_URL = secrets["supabase"]["url"]
SUPABASE_KEY = secrets["supabase"]["key"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("VERIFICA CATEGORIE ERRATE IN MEMORIA GLOBALE")
print("=" * 80)

# 1. Trova categorie non valide
response = supabase.table('prodotti_master').select('id, descrizione, categoria').execute()

categorie_non_valide = []
categorie_food = []
prodotti_materiali = []

for row in response.data:
    desc = row['descrizione']
    cat = row['categoria']
    
    # Categoria non valida (non in lista ufficiale)
    if cat not in TUTTE_LE_CATEGORIE and cat not in ["📝 NOTE E DICITURE", "Da Classificare"]:
        categorie_non_valide.append((row['id'], desc, cat))
    
    # Categoria "FOOD" specifica
    if cat == "FOOD":
        categorie_food.append((row['id'], desc, cat))
    
    # Materiali classificati male (keyword NO FOOD ma categoria diversa)
    materiali_keywords = ['BICCHIER', 'COPERCH', 'TOVAGLIO', 'PELLICO', 'SACCHETT', 
                          'CONTENITOR', 'ROTOL', 'CARTA', 'SPUGN', 'DETERSIV']
    if any(kw in desc.upper() for kw in materiali_keywords) and cat != "NO FOOD":
        prodotti_materiali.append((row['id'], desc, cat))

print(f"\n📊 ANALISI:")
print(f"  - Totale prodotti: {len(response.data)}")
print(f"  - Categorie non valide: {len(categorie_non_valide)}")
print(f"  - Categoria 'FOOD': {len(categorie_food)}")
print(f"  - Materiali classificati male: {len(prodotti_materiali)}")

# Mostra primi 10 di ogni tipo
if categorie_non_valide:
    print(f"\n❌ CATEGORIE NON VALIDE (prime 10):")
    for idx, desc, cat in categorie_non_valide[:10]:
        print(f"  - '{desc}' → {cat}")

if categorie_food:
    print(f"\n❌ CATEGORIA 'FOOD' (tutte):")
    for idx, desc, cat in categorie_food:
        print(f"  - '{desc}' → {cat}")

if prodotti_materiali:
    print(f"\n⚠️ MATERIALI CLASSIFICATI MALE (primi 10):")
    for idx, desc, cat in prodotti_materiali[:10]:
        print(f"  - '{desc}' → {cat} (dovrebbe essere NO FOOD)")

# Conferma correzione
print("\n" + "=" * 80)
correggere = input("Vuoi correggere questi errori? (s/n): ").lower()

if correggere == 's':
    corretti = 0
    
    # Correggi tutti gli errori
    tutti_errori = set(categorie_non_valide + categorie_food + prodotti_materiali)
    
    for idx, desc, cat_vecchia in tutti_errori:
        # Applica dizionario per trovare categoria corretta
        cat_nuova = applica_correzioni_dizionario(desc, "Da Classificare")
        
        if cat_nuova != cat_vecchia:
            try:
                supabase.table('prodotti_master')\
                    .update({'categoria': cat_nuova})\
                    .eq('id', idx)\
                    .execute()
                
                print(f"✅ '{desc[:50]}': {cat_vecchia} → {cat_nuova}")
                corretti += 1
            except Exception as e:
                print(f"❌ Errore correzione '{desc}': {e}")
    
    print(f"\n✅ Corretti {corretti} prodotti!")
    
    # Anche in prodotti_utente
    print("\n" + "=" * 80)
    print("VERIFICA PRODOTTI_UTENTE...")
    
    response_utente = supabase.table('prodotti_utente').select('id, descrizione, categoria').execute()
    
    corretti_utente = 0
    for row in response_utente.data:
        desc = row['descrizione']
        cat = row['categoria']
        
        if cat not in TUTTE_LE_CATEGORIE and cat not in ["📝 NOTE E DICITURE", "Da Classificare"]:
            cat_nuova = applica_correzioni_dizionario(desc, "Da Classificare")
            
            if cat_nuova != cat:
                try:
                    supabase.table('prodotti_utente')\
                        .update({'categoria': cat_nuova})\
                        .eq('id', row['id'])\
                        .execute()
                    
                    print(f"✅ UTENTE - '{desc[:50]}': {cat} → {cat_nuova}")
                    corretti_utente += 1
                except Exception as e:
                    print(f"❌ Errore correzione utente '{desc}': {e}")
    
    print(f"\n✅ Corretti {corretti_utente} prodotti utente!")
    
else:
    print("\n❌ Correzione annullata.")
