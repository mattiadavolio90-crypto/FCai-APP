"""
Test funzione calcola_prezzo_standard_intelligente()
Verifica calcolo automatico prezzo standard per confronti F&B
"""

import sys
import re
import pandas as pd

# Simula la funzione (copia da app.py)
def calcola_prezzo_standard_intelligente(descrizione, quantita, unita_misura, prezzo_unitario, categoria):
    """
    Calcola prezzo standardizzato intelligente per confronti F&B.
    Estrae peso/volume dalla descrizione e calcola €/Kg o €/Lt.
    """
    # Filtro 1: Solo F&B (esclude solo NO FOOD, permette Da Classificare)
    if categoria and str(categoria).upper() == 'NO FOOD':
        return None
    
    if not prezzo_unitario or prezzo_unitario <= 0:
        return None
    
    um = str(unita_misura).upper().strip() if unita_misura else ""
    desc = str(descrizione).upper() if descrizione else ""
    
    # CASO 1: Già in KG
    if um in ['KG', 'KILOGRAMMI']:
        return float(prezzo_unitario)
    
    # CASO 2: Già in Litri
    if um in ['LT', 'L', 'LITRI', 'LITRO']:
        return float(prezzo_unitario)
    
    # CASO 3: Grammi → €/Kg
    if um in ['GR', 'G', 'GRAMMI', 'GRAMMO']:
        return float(prezzo_unitario) * 1000
    
    # CASO 4: Millilitri → €/Lt
    if um == 'ML':
        return float(prezzo_unitario) * 1000
    
    # CASO 4.5: CONFEZIONI con numero pezzi (es. "X 18 PZ", "PZ 30")
    # Applicabile quando U.M. = CT, CF, Nr, CONF
    if um in ['CT', 'CF', 'NR', 'CONF', 'CONFEZIONE', 'CARTONE', 'NUMERO', 'N.', 'N']:
        # Pattern per trovare numero di pezzi nella descrizione
        pattern_pezzi_conf = [
            r'X\s*(\d+)\s*PZ\b',           # "X 18 PZ", "X18PZ"
            r'PZ\s*(\d+)',                 # "PZ 30", "PZ30"
            r'(\d+)\s*PZ\b',               # "30 PZ"
            r'X\s*(\d+)\s*PEZZI',          # "X 18 PEZZI"
        ]
        
        for pattern in pattern_pezzi_conf:
            match = re.search(pattern, desc)
            if match:
                try:
                    num_pezzi = float(match.group(1))
                    if 1 <= num_pezzi <= 1000:  # Validazione
                        # Prezzo confezione ÷ numero pezzi = €/Pz
                        prezzo_pz = float(prezzo_unitario) / num_pezzi
                        return prezzo_pz
                except:
                    continue
    
    # CASO 5: Estrazione da descrizione
    
    # 5A: LITRI (es. "FUSTO LT 30", "BOTTIGLIA 1.5L")
    pattern_litri = [
        r'(\d+(?:[.,]\d+)?)\s*LT?\b',
        r'LT\s*(\d+(?:[.,]\d+)?)',
        r'(\d+(?:[.,]\d+)?)\s*LITR',
    ]
    for pattern in pattern_litri:
        match = re.search(pattern, desc)
        if match:
            try:
                litri = float(match.group(1).replace(',', '.'))
                if 0.01 <= litri <= 1000:
                    return float(prezzo_unitario) / litri
            except:
                continue
    
    # 5B: CENTILITRI (es. "CL.50", "CL 75")
    pattern_cl = [
        r'CL\.?\s*(\d+(?:[.,]\d+)?)',
        r'(\d+(?:[.,]\d+)?)\s*CL\b',
    ]
    for pattern in pattern_cl:
        match = re.search(pattern, desc)
        if match:
            try:
                cl = float(match.group(1).replace(',', '.'))
                if 1 <= cl <= 1000:
                    litri = cl / 100
                    return float(prezzo_unitario) / litri
            except:
                continue
    
    # 5C: MILLILITRI (es. "330ML")
    pattern_ml = [r'(\d+)\s*ML\b', r'(\d+)\s*MILLILIT']
    for pattern in pattern_ml:
        match = re.search(pattern, desc)
        if match:
            try:
                ml = float(match.group(1))
                if 10 <= ml <= 10000:
                    litri = ml / 1000
                    return float(prezzo_unitario) / litri
            except:
                continue
    
    # 5D: KILOGRAMMI (es. "1.5 KG")
    pattern_kg = [
        r'(\d+(?:[.,]\d+)?)\s*KG\b',
        r'KG\s*(\d+(?:[.,]\d+)?)',
        r'(\d+(?:[.,]\d+)?)\s*KILO',
    ]
    for pattern in pattern_kg:
        match = re.search(pattern, desc)
        if match:
            try:
                kg = float(match.group(1).replace(',', '.'))
                if 0.01 <= kg <= 1000:
                    return float(prezzo_unitario) / kg
            except:
                continue
    
    # 5E: GRAMMI (es. "250G")
    pattern_gr = [r'(\d+)\s*GR?\b', r'(\d+)\s*GRAMM']
    for pattern in pattern_gr:
        match = re.search(pattern, desc)
        if match:
            try:
                gr = float(match.group(1))
                if 1 <= gr <= 100000:
                    kg = gr / 1000
                    return float(prezzo_unitario) / kg
            except:
                continue
    
    # CASO 6: Non calcolabile
    return None


# ============================================
# TEST CASES
# ============================================
def test_prezzo_standard():
    """Test completo con scenari reali"""
    
    tests = [
        # CASO 1: GIÀ IN KG/LT
        ("PANE FRANCESINO", 55, "KG", 3.50, "PANE", 3.50),
        ("ACQUA NATURALE", 24, "LT", 0.32, "ACQUA", 0.32),
        
        # CASO 2: GRAMMI/MILLILITRI
        ("PASTA", 1000, "GR", 0.85, "PASTA", 850.0),  # €0.85/1000gr = €850/kg
        ("OLIO OLIVA", 500, "ML", 4.50, "OLIO", 4500.0),  # €4.50/500ml = €4500/lt
        
        # CASO 3: ESTRAZIONE DA DESCRIZIONE
        ("BIRRA FUSTO LT 30", 3, "FS", 76.00, "BIRRE", 2.53),  # €76/30lt
        ("ACQUA CL.50 X 24", 30, "CT", 3.84, "ACQUA", 7.68),  # €3.84/0.5lt
        ("COCA COLA 330ML", 24, "CT", 7.92, "BEVANDE", 24.0),  # €7.92/0.33lt
        ("PASTA PISTACCHIO 1.5 KG", 1, "PZ", 12.50, "PASTA", 8.33),  # €12.50/1.5kg
        ("MOZZARELLA 250G", 10, "PZ", 2.50, "FORMAGGI", 10.0),  # €2.50/0.25kg
        
        # CASO 3B: CONFEZIONI con numero pezzi
        ("CANNONCINI MISTI X 18 PZ", 1, "CT", 16.20, "PASTICCERIA", 0.90),  # €16.20/18pz = €0.90/pz
        ("MINI SACHER X 30 PZ", 1, "CT", 18.60, "PASTICCERIA", 0.62),  # €18.60/30pz = €0.62/pz
        ("PAIN AU CHOCOLAT PZ 70", 2, "NR", 18.52, "PANIFICATI", 0.26),  # €18.52/70pz = €0.26/pz (prezzo unitario)
        ("FIAMME X 24 PZ", 1, "CT", 14.88, "PASTICCERIA", 0.62),  # €14.88/24pz = €0.62/pz
        
        # CASO 4: FILTRI (solo NO FOOD viene escluso)
        ("DETERSIVO 1L", 5, "PZ", 3.50, "NO FOOD", None),
        ("LATTE INTERO", 12, "LT", 0.85, "DA CLASSIFICARE", 0.85),  # Calcola anche se non classificato
        
        # CASO 5: NON CALCOLABILE (manca peso nella descrizione)
        ("TEGLIE ALLUMINIO", 100, "PZ", 15.00, "ATTREZZATURE", None),
        ("CAFFÈ TOSTATO", 1, "PZ", 25.00, "CAFFÈ", None),  # Nessun peso in descrizione
    ]
    
    risultati = []
    successi = 0
    fallimenti = 0
    
    print("\n" + "="*80)
    print("🧪 TEST CALCOLO PREZZO STANDARDIZZATO INTELLIGENTE")
    print("="*80 + "\n")
    
    for desc, qta, um, prezzo, cat, expected in tests:
        result = calcola_prezzo_standard_intelligente(desc, qta, um, prezzo, cat)
        
        # Confronto con tolleranza per float
        if expected is None:
            passed = result is None
        else:
            passed = result is not None and abs(result - expected) < 0.1
        
        status = "✅ PASS" if passed else "❌ FAIL"
        successi += 1 if passed else 0
        fallimenti += 1 if not passed else 0
        
        risultati.append({
            "Descrizione": desc[:40],
            "Q.tà": qta,
            "U.M.": um,
            "Prezzo": f"€{prezzo:.2f}",
            "Categoria": cat,
            "Atteso": f"€{expected:.2f}" if expected else "None",
            "Calcolato": f"€{result:.2f}" if result else "None",
            "Status": status
        })
        
        print(f"{status} | {desc[:35]:35} | {um:5} | €{prezzo:6.2f} | Cat: {cat:15} | Atteso: {f'€{expected:.2f}' if expected else 'None':8} | Calc: {f'€{result:.2f}' if result else 'None':8}")
    
    print("\n" + "="*80)
    print(f"📊 RIEPILOGO: {successi}/{len(tests)} test superati ({fallimenti} falliti)")
    print("="*80 + "\n")
    
    if fallimenti == 0:
        print("🎉 TUTTI I TEST SUPERATI! La funzione funziona correttamente.\n")
    else:
        print(f"⚠️ {fallimenti} test falliti. Verifica i casi sopra.\n")
    
    # Crea DataFrame per visualizzazione
    df = pd.DataFrame(risultati)
    print("\n📋 TABELLA COMPLETA RISULTATI:")
    print(df.to_string(index=False))
    
    return successi == len(tests)


if __name__ == "__main__":
    success = test_prezzo_standard()
    sys.exit(0 if success else 1)
