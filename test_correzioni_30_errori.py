#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test delle correzioni applicate al dizionario.
Verifica che i 30 errori critici siano stati risolti.
"""
import pandas as pd
from config.constants import DIZIONARIO_CORREZIONI

# Leggi il file normalizzato
df = pd.read_excel('dettaglio_20260116_1710_NORMALIZZATO.xlsx')

# Filtra solo errori veri (non "Da Classificare")
errori_veri = df[~df['Categoria'].isin(['Da Classificare', 'DA CLASSIFICARE', '']) & df['Categoria'].notna()]

print("=" * 80)
print("🧪 TEST CORREZIONI DIZIONARIO SUI 30 ERRORI CRITICI")
print("=" * 80)
print(f"\nTestando {len(errori_veri)} prodotti che erano categorizzati male...\n")

errori_risolti = 0
errori_rimasti = 0
dettaglio_errori = []

for idx, row in errori_veri.iterrows():
    desc = str(row['Descrizione']) if pd.notna(row['Descrizione']) else ""
    cat_vecchia = row['Categoria']
    cat_corretta = row['CORRETTA']
    
    # Simula la classificazione con il nuovo dizionario
    keywords_trovati = []
    categoria_predetta = None
    
    # Cerca keywords (stesso algoritmo dell'app)
    for keyword, categoria in DIZIONARIO_CORREZIONI.items():
        if keyword.upper() in desc.upper():
            keywords_trovati.append((keyword, categoria))
            # Prende l'ultima keyword trovata (priorità più specifica)
            categoria_predetta = categoria
    
    # Verifica se ora è corretto
    if categoria_predetta == cat_corretta:
        errori_risolti += 1
        status = "✅ RISOLTO"
    else:
        errori_rimasti += 1
        status = "❌ ANCORA ERRORE"
        dettaglio_errori.append({
            'desc': desc,
            'cat_vecchia': cat_vecchia,
            'cat_predetta': categoria_predetta if categoria_predetta else "Da Classificare",
            'cat_corretta': cat_corretta,
            'keywords': keywords_trovati
        })
    
    print(f"{status} | {desc[:60]}")
    print(f"           Vecchia: {cat_vecchia} → Predetta: {categoria_predetta if categoria_predetta else 'Da Classificare'} → Corretta: {cat_corretta}")
    if keywords_trovati:
        print(f"           Keywords: {[(k, c) for k, c in keywords_trovati[-3:]]}")  # Ultimi 3
    print()

print("=" * 80)
print("📊 RISULTATI TEST:")
print("=" * 80)
print(f"✅ Errori risolti: {errori_risolti}/{len(errori_veri)} ({100*errori_risolti/len(errori_veri):.1f}%)")
print(f"❌ Errori rimasti: {errori_rimasti}/{len(errori_veri)} ({100*errori_rimasti/len(errori_veri):.1f}%)")

if errori_rimasti > 0:
    print(f"\n⚠️  ERRORI ANCORA DA RISOLVERE ({errori_rimasti}):")
    for i, e in enumerate(dettaglio_errori, 1):
        print(f"\n{i}. {e['desc'][:70]}")
        print(f"   Predetta: {e['cat_predetta']} → Dovrebbe essere: {e['cat_corretta']}")
        if e['keywords']:
            print(f"   Keywords trovati: {e['keywords']}")
else:
    print("\n🎉 TUTTI I 30 ERRORI SONO STATI RISOLTI!")

print("=" * 80)
