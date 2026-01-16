#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script per applicare le correzioni dal file Excel normalizzato al database.
Analizza errori e crea mappature per migliorare dictionary e AI.
"""
import pandas as pd
from config.constants import CATEGORIE_FOOD_BEVERAGE, CATEGORIE_MATERIALI, CATEGORIE_SPESE_OPERATIVE, DIZIONARIO_CORREZIONI

# Leggi il file normalizzato
df = pd.read_excel('dettaglio_20260116_1710_NORMALIZZATO.xlsx')

# Componi lista categorie valide
categorie_valide = CATEGORIE_FOOD_BEVERAGE + CATEGORIE_MATERIALI + CATEGORIE_SPESE_OPERATIVE

print("=" * 80)
print("📊 ANALISI ERRORI E PERFORMANCE")
print("=" * 80)

# 1. Righe con errore (Categoria != CORRETTA)
errori = df[df['Categoria'] != df['CORRETTA']].copy()
print(f"\n📋 RIGHE ERRATE:")
print(f"   Totale errori: {len(errori)} su {len(df)} ({100*len(errori)/len(df):.1f}%)")

# 2. Categorizza gli errori
dizionario_errors = []  # Errori che il dizionario ha fatto (doveva trovare la categoria giusta)
classificazione_errors = []  # Errori dove categoria è "DA CLASSIFICARE" o simile

for idx, row in errori.iterrows():
    desc = str(row['Descrizione']) if pd.notna(row['Descrizione']) else ""
    categoria_app = row['Categoria']
    categoria_corretta = row['CORRETTA']
    
    # Cerca keyword della descrizione nel dizionario
    keywords_trovati = [k for k in DIZIONARIO_CORREZIONI.keys() if k.upper() in desc.upper()]
    
    if keywords_trovati:
        # Il dizionario ha trovato qualcosa ma ha sbagliato
        dizionario_errors.append({
            'descrizione': desc,
            'keywords_trovati': keywords_trovati,
            'categoria_classificata': categoria_app,
            'categoria_corretta': categoria_corretta
        })
    else:
        # Il dizionario non ha trovato niente, probabilmente è andato all'AI
        classificazione_errors.append({
            'descrizione': desc,
            'categoria_classificata': categoria_app,
            'categoria_corretta': categoria_corretta
        })

print(f"\n❌ ERRORI DEL DIZIONARIO (matched keywords ma categoria sbagliata):")
print(f"   {len(dizionario_errors)} errori")
if dizionario_errors:
    print(f"\n   Primi 5 esempi:")
    for i, e in enumerate(dizionario_errors[:5], 1):
        print(f"   {i}. '{e['descrizione'][:50]}...'")
        print(f"      Keywords: {e['keywords_trovati']}")
        print(f"      Classificato: {e['categoria_classificata']} → Corretto: {e['categoria_corretta']}")

print(f"\n❌ ERRORI DELL'AI (nessun keyword trovato, classificazione sbagliata):")
print(f"   {len(classificazione_errors)} errori")
if classificazione_errors:
    print(f"\n   Primi 5 esempi:")
    for i, e in enumerate(classificazione_errors[:5], 1):
        print(f"   {i}. '{e['descrizione'][:50]}...'")
        print(f"      Classificato: {e['categoria_classificata']} → Corretto: {e['categoria_corretta']}")

# 3. Analisi per categoria di errore
print(f"\n📈 ERRORI PER CATEGORIA (categoria che ha ricevuto classificazione sbagliata):")
error_categories = errori['Categoria'].value_counts().head(10)
for cat, count in error_categories.items():
    pct = 100 * count / len(errori)
    print(f"   {cat}: {count} errori ({pct:.1f}%)")

# 4. Categoria corretta più frequente (cosa doveva essere)
print(f"\n✅ CATEGORIE CORRETTE PIÙ FREQUENTI (target delle correzioni):")
correct_categories = errori['CORRETTA'].value_counts().head(10)
for cat, count in correct_categories.items():
    pct = 100 * count / len(errori)
    print(f"   {cat}: {count} occorrenze ({pct:.1f}%)")

# 5. Percentuale per categoria
print(f"\n📊 ACCURATEZZA PER CATEGORIA (righe corrette):")
for cat in sorted(categorie_valide):
    righe_cat = df[df['CORRETTA'] == cat]
    corrette = righe_cat[righe_cat['Categoria'] == righe_cat['CORRETTA']]
    if len(righe_cat) > 0:
        acc = 100 * len(corrette) / len(righe_cat)
        print(f"   {cat:35s}: {acc:5.1f}% ({len(corrette)}/{len(righe_cat)} corrette)")

# 6. Categorie con 0% accuratezza
print(f"\n⚠️  CATEGORIE CON ERRORI AL 100% (tutte sbagliate):")
for cat in sorted(categorie_valide):
    righe_cat = df[df['CORRETTA'] == cat]
    corrette = righe_cat[righe_cat['Categoria'] == righe_cat['CORRETTA']]
    if len(righe_cat) > 0 and len(corrette) == 0:
        print(f"   {cat}: 0 corrette su {len(righe_cat)}")

print("\n" + "=" * 80)
print(f"📝 RIEPILOGO FINALE:")
print(f"   Righe totali analizzate: {len(df)}")
print(f"   Righe corrette: {len(df) - len(errori)} ({100*(len(df)-len(errori))/len(df):.1f}%)")
print(f"   Righe errate: {len(errori)} ({100*len(errori)/len(df):.1f}%)")
print(f"     - Errori dizionario: {len(dizionario_errors)}")
print(f"     - Errori AI: {len(classificazione_errors)}")
print("=" * 80)
