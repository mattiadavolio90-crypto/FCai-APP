"""
Script per riclassificare automaticamente TUTTI i prodotti nel database
usando il dizionario aggiornato e l'AI.
"""

import os
import toml
from supabase import create_client
from services.ai_service import applica_correzioni_dizionario, categorizza_con_memoria
from config.constants import TUTTE_LE_CATEGORIE

# Carica credenziali
secrets_path = os.path.join(os.path.dirname(__file__), '.streamlit', 'secrets.toml')
secrets = toml.load(secrets_path)
SUPABASE_URL = secrets["supabase"]["url"]
SUPABASE_KEY = secrets["supabase"]["key"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("RICLASSIFICAZIONE AUTOMATICA PRODOTTI")
print("=" * 80)

# 1. Carica TUTTI i prodotti dalla tabella fatture
print("\n📥 Caricamento prodotti da fatture...")
response = supabase.table('fatture')\
    .select('id, descrizione, categoria, fornitore, totale_riga')\
    .execute()

print(f"✅ Caricati {len(response.data)} righe")

# 2. Analizza categorie attuali
categorie_count = {}
for row in response.data:
    cat = row.get('categoria', 'Da Classificare')
    if cat is None or cat == '':
        cat = 'Da Classificare'
    categorie_count[cat] = categorie_count.get(cat, 0) + 1

print("\n📊 STATISTICHE ATTUALI:")
for cat, count in sorted(categorie_count.items(), key=lambda x: x[1], reverse=True)[:20]:
    print(f"  {cat}: {count}")

# 3. Trova prodotti da riclassificare
da_riclassificare = []
for row in response.data:
    desc = row['descrizione']
    cat_attuale = row.get('categoria', '')
    
    if not desc or desc.strip() == '':
        continue
    
    # Applica dizionario per vedere categoria suggerita
    cat_suggerita = applica_correzioni_dizionario(desc, "Da Classificare")
    
    # Se categoria diversa o mancante, aggiungi a lista
    if (cat_attuale != cat_suggerita and cat_suggerita != "Da Classificare") or \
       (cat_attuale in [None, '', 'Da Classificare'] and cat_suggerita != "Da Classificare"):
        da_riclassificare.append({
            'id': row['id'],
            'descrizione': desc,
            'cat_vecchia': cat_attuale if cat_attuale else 'Da Classificare',
            'cat_nuova': cat_suggerita
        })

print(f"\n🔍 PRODOTTI DA RICLASSIFICARE: {len(da_riclassificare)}")

if da_riclassificare:
    print("\nPrimi 20 esempi:")
    for item in da_riclassificare[:20]:
        desc_short = item['descrizione'][:50] + "..." if len(item['descrizione']) > 50 else item['descrizione']
        print(f"  {desc_short:55} | {item['cat_vecchia']:20} → {item['cat_nuova']}")
    
    # Conferma
    print("\n" + "=" * 80)
    conferma = input(f"Vuoi riclassificare {len(da_riclassificare)} prodotti? (s/n): ").lower()
    
    if conferma == 's':
        print("\n🔄 Riclassificazione in corso...")
        aggiornati = 0
        errori = 0
        
        for item in da_riclassificare:
            try:
                supabase.table('fatture')\
                    .update({'categoria': item['cat_nuova']})\
                    .eq('id', item['id'])\
                    .execute()
                
                aggiornati += 1
                if aggiornati % 50 == 0:
                    print(f"  Processati {aggiornati}/{len(da_riclassificare)}...")
            
            except Exception as e:
                errori += 1
                if errori <= 5:  # Mostra solo primi 5 errori
                    print(f"  ❌ Errore: {item['descrizione'][:30]}: {e}")
        
        print(f"\n✅ COMPLETATO!")
        print(f"  - Aggiornati: {aggiornati}")
        print(f"  - Errori: {errori}")
        
        # Statistiche finali
        response_finale = supabase.table('fatture')\
            .select('categoria')\
            .execute()
        
        categorie_finale = {}
        for row in response_finale.data:
            cat = row.get('categoria', 'Da Classificare')
            if cat is None or cat == '':
                cat = 'Da Classificare'
            categorie_finale[cat] = categorie_finale.get(cat, 0) + 1
        
        print("\n📊 STATISTICHE FINALI:")
        for cat, count in sorted(categorie_finale.items(), key=lambda x: x[1], reverse=True)[:20]:
            delta = count - categorie_count.get(cat, 0)
            delta_str = f"({delta:+d})" if delta != 0 else ""
            print(f"  {cat}: {count} {delta_str}")
    
    else:
        print("\n❌ Riclassificazione annullata")
else:
    print("\n✅ Nessun prodotto da riclassificare!")
