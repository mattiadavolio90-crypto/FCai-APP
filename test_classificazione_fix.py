"""
Test per verificare la classificazione corretta dei prodotti.
Verifica che:
1. "FOOD" non venga mai generata come categoria
2. Bicchieri, coperchi → NO FOOD
3. Dizionario correzioni funzioni
"""

from config.constants import DIZIONARIO_CORREZIONI, TUTTE_LE_CATEGORIE
from services.ai_service import applica_correzioni_dizionario

# Test prodotti problematici
test_cases = [
    # (descrizione, categoria_attesa)
    ("BICCHIERI PLASTICA", "NO FOOD"),
    ("COPERCHI", "NO FOOD"),
    ("TOVAGLIOLI", "NO FOOD"),
    ("PELLICOLA", "NO FOOD"),
    ("SACCHETTI", "NO FOOD"),
    ("POLLO INTERO", "CARNE"),
    ("SALMONE", "PESCE"),
    ("CAFFÈ ARABICA", "CAFFÈ"),
    ("VINO ROSSO", "VINI"),
    ("PASTA PENNE", "SECCO"),
]

print("=" * 80)
print("TEST DIZIONARIO CORREZIONI")
print("=" * 80)

errori = []
for descrizione, attesa in test_cases:
    risultato = applica_correzioni_dizionario(descrizione, "Da Classificare")
    status = "✅" if risultato == attesa else "❌"
    print(f"{status} '{descrizione}' → {risultato} (atteso: {attesa})")
    
    if risultato != attesa:
        errori.append((descrizione, risultato, attesa))

print("\n" + "=" * 80)
print("VERIFICA CATEGORIE DISPONIBILI")
print("=" * 80)

if "FOOD" in TUTTE_LE_CATEGORIE:
    print("❌ ERRORE: 'FOOD' è presente in TUTTE_LE_CATEGORIE!")
else:
    print("✅ 'FOOD' NON è in TUTTE_LE_CATEGORIE")

print(f"\n📋 Categorie totali: {len(TUTTE_LE_CATEGORIE)}")
print(f"📖 Keyword dizionario: {len(DIZIONARIO_CORREZIONI)}")

print("\n" + "=" * 80)
print("KEYWORD DIZIONARIO PER NO FOOD")
print("=" * 80)

no_food_keywords = [k for k, v in DIZIONARIO_CORREZIONI.items() if v == "NO FOOD"]
print(f"Totale keyword NO FOOD: {len(no_food_keywords)}")
print("\nPrime 20 keyword NO FOOD:")
for keyword in sorted(no_food_keywords)[:20]:
    print(f"  - {keyword}")

if errori:
    print("\n" + "=" * 80)
    print(f"❌ TROVATI {len(errori)} ERRORI:")
    print("=" * 80)
    for desc, ris, att in errori:
        print(f"  '{desc}': {ris} ≠ {att}")
else:
    print("\n" + "=" * 80)
    print("✅ TUTTI I TEST SUPERATI!")
    print("=" * 80)
