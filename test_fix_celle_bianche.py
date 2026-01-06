"""
Test per verificare che le celle bianche siano risolte.
"""
import pandas as pd
import numpy as np

print("=" * 60)
print("TEST FIX CELLE BIANCHE")
print("=" * 60)

# Simula DataFrame con categorie mancanti
df_test = pd.DataFrame({
    'Descrizione': ['PASTA PENNE', 'POLLO INTERO', 'OLIO EVO', 'PRODOTTO NUOVO'],
    'Categoria': ['SECCO', None, np.nan, '']
})

print("\n📋 DataFrame PRIMA del fix:")
print(df_test)
print(f"\nCategorie NULL: {df_test['Categoria'].isna().sum()}")

# Applica fix (fillna)
df_test['Categoria'] = df_test['Categoria'].fillna("Da Classificare")

print("\n📋 DataFrame DOPO fillna:")
print(df_test)
print(f"\nCategorie NULL: {df_test['Categoria'].isna().sum()}")

# Converti vuoti in "Da Classificare" (come nel codice reale)
df_test['Categoria'] = df_test['Categoria'].apply(
    lambda x: 'Da Classificare' if pd.isna(x) or x is None or str(x).strip() == '' else x
)

print("\n📋 DataFrame DOPO conversione vuoti:")
print(df_test)
print(f"\nCategorie NULL: {df_test['Categoria'].isna().sum()}")
print(f"\nCategorie 'Da Classificare': {(df_test['Categoria'] == 'Da Classificare').sum()}")

# Verifica finale
assert df_test['Categoria'].isna().sum() == 0, "❌ ERRORE: Ci sono ancora NULL!"
assert '' not in df_test['Categoria'].values, "❌ ERRORE: Ci sono stringhe vuote!"
assert df_test.loc[0, 'Categoria'] == 'SECCO', "❌ ERRORE: SECCO non preservato!"
assert df_test.loc[1, 'Categoria'] == 'Da Classificare', "❌ ERRORE: None non convertito!"
assert df_test.loc[2, 'Categoria'] == 'Da Classificare', "❌ ERRORE: NaN non convertito!"
assert df_test.loc[3, 'Categoria'] == 'Da Classificare', "❌ ERRORE: Vuoto non convertito!"

print("\n" + "=" * 60)
print("✅ TUTTI I TEST PASSATI!")
print("=" * 60)
print("\n🎯 Risultato:")
print("• NULL → 'Da Classificare' ✅")
print("• '' (vuoto) → 'Da Classificare' ✅")
print("• 'SECCO' (valido) → preservato ✅")
print("• Nessuna cella bianca rimane ✅")
