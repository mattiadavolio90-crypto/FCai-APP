#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verifica che non ci siano keywords duplicate nel dizionario.
"""
from config.constants import DIZIONARIO_CORREZIONI

# Trova duplicati
keywords_viste = {}
duplicati = {}

for keyword, categoria in DIZIONARIO_CORREZIONI.items():
    if keyword in keywords_viste:
        if keyword not in duplicati:
            duplicati[keyword] = [keywords_viste[keyword]]
        duplicati[keyword].append(categoria)
    else:
        keywords_viste[keyword] = categoria

print("=" * 80)
print("VERIFICA KEYWORDS DUPLICATE NEL DIZIONARIO")
print("=" * 80)

if duplicati:
    print(f"\n TROVATI {len(duplicati)} DUPLICATI:\n")
    for keyword, categorie in duplicati.items():
        print(f"   '{keyword}' -> {categorie}")
        print(f"      PROBLEMA: Categoria dipende dall'ordine di iterazione!")
else:
    print("\n ✅ NESSUN DUPLICATO! Dizionario pulito.")

print("\n" + "=" * 80)
print(f"Totale keywords: {len(DIZIONARIO_CORREZIONI)}")
print("=" * 80)
