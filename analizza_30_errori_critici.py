#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analisi dettagliata dei 30 ERRORI VERI (priorità massima).
Identifica keywords problematiche da rimuovere/correggere.
"""
import pandas as pd
from config.constants import DIZIONARIO_CORREZIONI

# Leggi il file normalizzato
df = pd.read_excel('dettaglio_20260116_1710_NORMALIZZATO.xlsx')

# Filtra solo errori veri (non "Da Classificare")
errori_veri = df[~df['Categoria'].isin(['Da Classificare', 'DA CLASSIFICARE', '']) & df['Categoria'].notna()]

print("=" * 80)
print("🔴 ANALISI DEI 30 ERRORI CRITICI (prodotti categorizzati male)")
print("=" * 80)
print(f"\nTotale errori veri: {len(errori_veri)}\n")

# Analizza ogni errore
problemi_keywords = {}  # keyword -> lista di errori causati

for idx, row in errori_veri.iterrows():
    desc = str(row['Descrizione']) if pd.notna(row['Descrizione']) else ""
    cat_sbagliata = row['Categoria']
    cat_corretta = row['CORRETTA']
    
    # Trova keywords che hanno causato la classificazione sbagliata
    keywords_trovati = []
    for keyword, categoria in DIZIONARIO_CORREZIONI.items():
        if keyword.upper() in desc.upper() and categoria == cat_sbagliata:
            keywords_trovati.append(keyword)
            
            if keyword not in problemi_keywords:
                problemi_keywords[keyword] = []
            problemi_keywords[keyword].append({
                'desc': desc,
                'cat_sbagliata': cat_sbagliata,
                'cat_corretta': cat_corretta
            })
    
    print(f"📌 {desc[:70]}")
    print(f"   Classificato: {cat_sbagliata} → Doveva essere: {cat_corretta}")
    print(f"   Keywords trovati: {keywords_trovati if keywords_trovati else 'NESSUNO (errore AI?)'}")
    print()

# Riepilogo keywords problematiche
print("\n" + "=" * 80)
print("🔧 KEYWORDS PROBLEMATICHE DA CORREGGERE/RIMUOVERE:")
print("=" * 80)

for keyword, errori in sorted(problemi_keywords.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"\n❌ Keyword: '{keyword}' → Causa {len(errori)} errori")
    categoria_assegnata = DIZIONARIO_CORREZIONI[keyword]
    print(f"   Attualmente assegna: {categoria_assegnata}")
    print(f"   Esempi di errori causati:")
    for i, e in enumerate(errori[:3], 1):
        print(f"      {i}. {e['desc'][:60]}...")
        print(f"         {e['cat_sbagliata']} (sbagliato) → {e['cat_corretta']} (corretto)")

print("\n" + "=" * 80)
print("💡 RACCOMANDAZIONI:")
print("=" * 80)
print("1. RIMUOVERE keywords troppo generiche/ambigue che causano falsi positivi")
print("2. AGGIUNGERE keywords più specifiche per prodotti simili")
print("3. MIGLIORARE prompt AI per gestire casi ambigui")
print("=" * 80)
