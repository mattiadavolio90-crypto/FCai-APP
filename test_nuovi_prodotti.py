"""Test veloce per verificare i nuovi prodotti"""
from services.ai_service import applica_correzioni_dizionario

prodotti_test = [
    'SALSICCIA FRESCA',
    'RAVIOLI RICOTTA',
    'TORTELLINI CARNE',
    'GNOCCHI PATATE',
    'WURSTEL',
    'BURRO',
    'LASAGNE FRESCHE',
    'CANNELLONI',
    'COPPETTA SANGO 10CM WB',
    'COPPETTE TRASPARENTI',
    'VASCHETTE ALLUMINIO'
]

print("=" * 60)
print("TEST NUOVE KEYWORD DIZIONARIO")
print("=" * 60)

for prodotto in prodotti_test:
    categoria = applica_correzioni_dizionario(prodotto, "Da Classificare")
    status = "✅" if categoria != "Da Classificare" else "❌"
    print(f"{status} {prodotto:30} → {categoria}")

print("=" * 60)
