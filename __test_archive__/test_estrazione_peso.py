"""
Test dell'estrazione automatica peso/volume da descrizione
"""
import re
import pandas as pd

class MockLogger:
    def debug(self, msg): print(f"DEBUG: {msg}")
    def warning(self, msg): print(f"WARNING: {msg}")

logger = MockLogger()

def estrai_peso_da_descrizione(descrizione, unita_misura=None):
    """Test locale della funzione"""
    if not descrizione or pd.isna(descrizione):
        return None
    
    desc = str(descrizione).upper()
    
    patterns = [
        # KILOGRAMMI
        (r'(\d+(?:[.,]\d+)?)\s*KG\b', 1.0),
        (r'(\d+(?:[.,]\d+)?)\s*KILO\b', 1.0),
        (r'(\d+(?:[.,]\d+)?)\s*KILOGRAM', 1.0),
        
        # GRAMMI
        (r'(\d+)\s*GR\b', 0.001),
        (r'(\d+)\s*G\b', 0.001),
        (r'(\d+)\s*GRAMM', 0.001),
        
        # LITRI
        (r'(\d+(?:[.,]\d+)?)\s*LT\b', 1.0),
        (r'(\d+(?:[.,]\d+)?)\s*L\b', 1.0),
        (r'(\d+(?:[.,]\d+)?)\s*LITR', 1.0),
        
        # CENTILITRI
        (r'CL\.?\s*(\d+(?:[.,]\d+)?)', 0.01),
        (r'(\d+(?:[.,]\d+)?)\s*CL\b', 0.01),
        
        # MILLILITRI
        (r'(\d+)\s*ML\b', 0.001),
        (r'(\d+)\s*MILLILIT', 0.001),
    ]
    
    for pattern, multiplier in patterns:
        match = re.search(pattern, desc)
        if match:
            try:
                valore_str = match.group(1).replace(',', '.')
                valore = float(valore_str)
                peso_standard = valore * multiplier
                
                if 0.001 <= peso_standard <= 100:
                    logger.debug(f"✓ Estratto: '{descrizione[:50]}' → {peso_standard:.3f} Kg/Lt")
                    return peso_standard
                else:
                    logger.warning(f"✗ Peso fuori range: {peso_standard} da '{descrizione[:50]}'")
                    continue
                    
            except (ValueError, AttributeError, IndexError) as e:
                logger.warning(f"✗ Errore parsing '{descrizione[:50]}': {e}")
                continue
    
    return None


# Test cases
print("=" * 80)
print("🧪 TEST ESTRAZIONE AUTOMATICA PESO/VOLUME")
print("=" * 80)

test_cases = [
    ("MOLINARI SAMBUCA 1.5L", "PZ", 1.5),
    ("COCACOLA LATTINA 330ML", "PZ", 0.33),
    ("PASTA PISTACCHIO 1.5 KG", "PZ", 1.5),
    ("MOZZARELLA 250G", "PZ", 0.25),
    ("ACQUA CL.75", "PZ", 0.75),
    ("ACQUA 75 CL", "PZ", 0.75),
    ("OLIO EXTRA VERGINE 1LT", "PZ", 1.0),
    ("PARMIGIANO REGGIANO 500GR", "PZ", 0.5),
    ("BIRRA MORETTI 66 CL", "PZ", 0.66),
    ("VINO ROSSO 750ML", "PZ", 0.75),
    ("FARINA TIPO 00 1KG", "PZ", 1.0),
    ("PASTA BARILLA 500 GR", "PZ", 0.5),
    ("PROSECCO 0.75L", "PZ", 0.75),
    ("CAFFE' ILLY 250G", "PZ", 0.25),
    ("ZUCCHERO 1 KILO", "PZ", 1.0),
    ("SALE FINO 1KILO", "PZ", 1.0),
    ("PRODOTTO GENERICO", "PZ", None),  # Nessun peso
    ("ARTICOLO VARIO", "KG", None),  # Non serve estrazione per KG
]

print("\n📦 Test Estrazione:\n")
successi = 0
fallimenti = 0

for desc, um, expected in test_cases:
    result = estrai_peso_da_descrizione(desc, um)
    
    if expected is None:
        if result is None:
            status = "✅ PASS"
            successi += 1
        else:
            status = f"❌ FAIL (atteso None, ottenuto {result})"
            fallimenti += 1
    else:
        if result is not None and abs(result - expected) < 0.01:
            status = "✅ PASS"
            successi += 1
        else:
            status = f"❌ FAIL (atteso {expected}, ottenuto {result})"
            fallimenti += 1
    
    print(f"{status:15} | {desc:40} → {result if result else 'None'}")

print("\n" + "=" * 80)
print(f"📊 RISULTATI: {successi} successi, {fallimenti} fallimenti")
print("=" * 80)
