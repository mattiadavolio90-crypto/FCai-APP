"""
Test della funzione calcola_prezzo_standard
"""

def calcola_prezzo_standard(prezzo_unitario, quantita, unita_misura, peso_unitario=None):
    """Test locale della funzione"""
    try:
        if not prezzo_unitario or prezzo_unitario <= 0:
            return None
        
        um = str(unita_misura).upper().strip() if unita_misura else ""
        
        if um == "KG":
            return float(prezzo_unitario)
        
        if um in ["LT", "L", "LITRI", "LITRO"]:
            return float(prezzo_unitario)
        
        if um in ["GR", "G", "GRAMMI", "GRAMMO"]:
            return float(prezzo_unitario) * 1000
        
        if um in ["ML", "MILLILITRI", "MILLILITRO"]:
            return float(prezzo_unitario) * 1000
        
        if um in ["PZ", "NR", "CONF", "CF", "PEZZI", "PEZZO", "CONFEZIONE", "CONFEZIONI", "N"]:
            if peso_unitario and peso_unitario > 0:
                return float(prezzo_unitario) / float(peso_unitario)
            else:
                return None
        
        return None
        
    except (ValueError, TypeError, ZeroDivisionError) as e:
        print(f"Errore: {e}")
        return None


# Test cases
print("=" * 80)
print("🧪 TEST FUNZIONE calcola_prezzo_standard()")
print("=" * 80)

test_cases = [
    # (prezzo_unit, quantita, um, peso_unit, descrizione)
    (3.50, 55, "KG", None, "PANE in KG"),
    (12.00, 0.5, "PZ", 0.3, "FOCACCIA in PZ (0.3kg/pezzo)"),
    (8.50, 1, "LT", None, "OLIO in LT"),
    (2.50, 1, "PZ", 0.2, "MOZZARELLA in PZ (0.2kg/pezzo)"),
    (0.80, 1000, "GR", None, "SALE in GR"),
    (15.00, 500, "ML", None, "ACETO in ML"),
    (5.00, 1, "PZ", None, "PRODOTTO in PZ (no peso)"),
    (10.00, 1, "CONF", 2.5, "CONFEZIONE (2.5kg)"),
]

for prezzo, qty, um, peso, desc in test_cases:
    result = calcola_prezzo_standard(prezzo, qty, um, peso)
    print(f"\n📦 {desc}")
    print(f"   Input: €{prezzo} / {um}" + (f" (peso: {peso}kg)" if peso else ""))
    if result:
        print(f"   ✅ Prezzo Standard: €{result:.2f}/kg")
    else:
        print(f"   ⚠️ Non calcolabile (manca peso unitario)")

print("\n" + "=" * 80)
print("✅ Test completato!")
print("=" * 80)
