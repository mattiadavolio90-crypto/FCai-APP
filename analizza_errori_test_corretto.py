#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per analizzare correttamente il file Excel di test.
Il file contiene SOLO le righe problematiche (307 su 881 totali).
"""
import pandas as pd
from config.constants import DIZIONARIO_CORREZIONI

# Leggi il file normalizzato
df = pd.read_excel('dettaglio_20260116_1710_NORMALIZZATO.xlsx')

# Statistiche generali
RIGHE_TOTALI_ORIGINALI = 881
righe_problematiche = len(df)
righe_corrette = RIGHE_TOTALI_ORIGINALI - righe_problematiche
accuratezza_generale = 100 * righe_corrette / RIGHE_TOTALI_ORIGINALI

print("=" * 80)
print("📊 ANALISI ACCURATEZZA CLASSIFICAZIONE")
print("=" * 80)
print(f"\n✅ ACCURATEZZA GENERALE:")
print(f"   Righe totali caricate: {RIGHE_TOTALI_ORIGINALI}")
print(f"   Righe corrette: {righe_corrette} ({accuratezza_generale:.1f}%)")
print(f"   Righe problematiche: {righe_problematiche} ({100*righe_problematiche/RIGHE_TOTALI_ORIGINALI:.1f}%)")

# Distingui tra "Da Classificare" e "Errori veri"
da_classificare = df[df['Categoria'].isin(['Da Classificare', 'DA CLASSIFICARE', '']) | df['Categoria'].isna()]
errori_veri = df[~df.index.isin(da_classificare.index)]

print(f"\n📋 BREAKDOWN DEI 307 PROBLEMI:")
print(f"   1. Da Classificare: {len(da_classificare)} righe (dizionario+AI non hanno trovato nulla)")
print(f"   2. Errori veri: {len(errori_veri)} righe (categoria assegnata ma sbagliata)")

# Analisi "Da Classificare"
print(f"\n🔍 ANALISI 'DA CLASSIFICARE' ({len(da_classificare)} righe):")
print(f"   Categoria corretta che dovevano avere:")
target_da_classificare = da_classificare['CORRETTA'].value_counts()
for cat, count in target_da_classificare.head(10).items():
    pct = 100 * count / len(da_classificare)
    print(f"      {cat:35s}: {count:3d} righe ({pct:.1f}%)")

# Analisi errori veri
print(f"\n❌ ANALISI ERRORI VERI ({len(errori_veri)} righe):")
if len(errori_veri) > 0:
    print(f"   Categoria assegnata (sbagliata):")
    cat_errate = errori_veri['Categoria'].value_counts()
    for cat, count in cat_errate.head(10).items():
        pct = 100 * count / len(errori_veri)
        print(f"      {cat:35s}: {count:3d} errori ({pct:.1f}%)")
    
    print(f"\n   Categoria corretta che dovevano avere:")
    target_errori = errori_veri['CORRETTA'].value_counts()
    for cat, count in target_errori.head(10).items():
        pct = 100 * count / len(errori_veri)
        print(f"      {cat:35s}: {count:3d} righe ({pct:.1f}%)")
    
    # Esempi di errori veri più comuni
    print(f"\n   Esempi di errori veri (categoria sbagliata → corretta):")
    for i, (idx, row) in enumerate(errori_veri.head(10).iterrows(), 1):
        desc = str(row['Descrizione'])[:50]
        cat_sbagliata = row['Categoria']
        cat_corretta = row['CORRETTA']
        print(f"      {i}. {desc}...")
        print(f"         {cat_sbagliata} → {cat_corretta}")

# Analisi dizionario per gli errori veri
print(f"\n🔑 ANALISI KEYWORDS NEGLI ERRORI VERI:")
errori_con_keywords = 0
errori_senza_keywords = 0
esempi_keywords = []

for idx, row in errori_veri.iterrows():
    desc = str(row['Descrizione']) if pd.notna(row['Descrizione']) else ""
    keywords = [k for k in DIZIONARIO_CORREZIONI.keys() if k.upper() in desc.upper()]
    
    if keywords:
        errori_con_keywords += 1
        if len(esempi_keywords) < 5:
            esempi_keywords.append({
                'desc': desc[:50],
                'keywords': keywords,
                'cat_sbagliata': row['Categoria'],
                'cat_corretta': row['CORRETTA']
            })
    else:
        errori_senza_keywords += 1

print(f"   Errori con keywords trovati: {errori_con_keywords}")
print(f"   Errori senza keywords: {errori_senza_keywords}")

if esempi_keywords:
    print(f"\n   Esempi errori con keywords (dizionario ha sbagliato):")
    for i, e in enumerate(esempi_keywords, 1):
        print(f"      {i}. '{e['desc']}...'")
        print(f"         Keywords: {e['keywords']}")
        print(f"         {e['cat_sbagliata']} → {e['cat_corretta']}")

print("\n" + "=" * 80)
print(f"📝 RIEPILOGO FINALE:")
print(f"   Accuratezza generale: {accuratezza_generale:.1f}% ({righe_corrette}/{RIGHE_TOTALI_ORIGINALI})")
print(f"   ")
print(f"   Problemi totali: {righe_problematiche} ({100*righe_problematiche/RIGHE_TOTALI_ORIGINALI:.1f}%)")
print(f"      - Da classificare: {len(da_classificare)} ({100*len(da_classificare)/RIGHE_TOTALI_ORIGINALI:.1f}%)")
print(f"      - Errori veri: {len(errori_veri)} ({100*len(errori_veri)/RIGHE_TOTALI_ORIGINALI:.1f}%)")
print(f"   ")
print(f"   Conclusione:")
print(f"      ✅ 65% di accuratezza è un buon punto di partenza!")
print(f"      🎯 Obiettivo: aggiungere keywords per ridurre i 'Da Classificare'")
print(f"      🔧 Obiettivo: correggere dizionario per i {errori_con_keywords} errori con keywords")
print("=" * 80)
