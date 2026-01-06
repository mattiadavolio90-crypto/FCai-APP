"""
🔍 TEST HASH ARGON2 - Diagnosi Bug Hash Duplicato
===================================================
Script per testare se l'hash Argon2 viene generato correttamente
"""

from argon2 import PasswordHasher
import secrets
import string

print("=" * 60)
print("🔍 TEST HASH ARGON2")
print("=" * 60)

def genera_password_sicura(lunghezza=12):
    """Genera una password casuale forte"""
    caratteri = string.ascii_letters + string.digits + "!@#$%&*"
    password = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice("!@#$%&*")
    ]
    password += [secrets.choice(caratteri) for _ in range(lunghezza - 4)]
    secrets.SystemRandom().shuffle(password)
    return ''.join(password)

# Crea hasher
ph = PasswordHasher()

print("\n📝 TEST 1: Generazione Hash Singola")
print("-" * 60)

password = genera_password_sicura()
print(f"Password generata: {password}")

hash1 = ph.hash(password)
print(f"\nHash generato:")
print(f"  Completo: {hash1}")
print(f"  Lunghezza: {len(hash1)} caratteri")
print(f"  Primi 30: {hash1[:30]}")
print(f"  Ultimi 30: {hash1[-30:]}")

# Verifica formato
print(f"\nVerifica formato:")
if hash1.startswith('$argon2'):
    print(f"  ✅ Inizia con '$argon2'")
else:
    print(f"  ❌ NON inizia con '$argon2'!")
    print(f"  Inizio reale: {hash1[:20]}")

# Conta $
dollar_count = hash1.count('$')
print(f"  Numero di '$': {dollar_count}")
if dollar_count == 5:
    print(f"  ✅ Formato corretto (5 '$' attesi)")
else:
    print(f"  ⚠️  Formato anomalo (attesi 5 '$', trovati {dollar_count})")

# Parti dell'hash
parts = hash1.split('$')
print(f"\nParti dell'hash (split su '$'):")
for i, part in enumerate(parts):
    if part:
        print(f"  [{i}] {part[:50]}{'...' if len(part) > 50 else ''}")

print("\n📝 TEST 2: Verifica Hash")
print("-" * 60)

try:
    ph.verify(hash1, password)
    print("✅ Verifica hash SUCCESSO - Password corretta")
except Exception as e:
    print(f"❌ Verifica hash FALLITA: {e}")

try:
    ph.verify(hash1, "password_errata")
    print("❌ BUG: Hash accetta password errata!")
except Exception:
    print("✅ Verifica password errata RESPINTA correttamente")

print("\n📝 TEST 3: Hash Multipli della Stessa Password")
print("-" * 60)

password_test = "TestPassword123!"
hashes = []

for i in range(3):
    h = ph.hash(password_test)
    hashes.append(h)
    print(f"\nHash {i+1}:")
    print(f"  Primi 30: {h[:30]}")
    print(f"  Uguale ai precedenti: {h in hashes[:-1]}")

print("\n📝 TEST 4: Simulazione Bug 'argon2idargon2id'")
print("-" * 60)

# Prova a ricreare il bug
test_hash = ph.hash("test123")
print(f"Hash normale: {test_hash[:50]}...")

# Possibili cause del bug
print("\nPossibili manipolazioni che causerebbero il bug:")

# 1. Rimozione del primo $
mangled1 = test_hash[1:]  # Rimuove primo $
print(f"1. Senza primo '$': {mangled1[:50]}...")

# 2. Replace di $
mangled2 = test_hash.replace('$', '')
print(f"2. Senza tutti '$': {mangled2[:50]}...")

# 3. Doppio hash
mangled3 = test_hash + test_hash[:20]
print(f"3. Concatenato: {mangled3[:50]}...")

print("\n" + "=" * 60)
print("💡 CONCLUSIONI:")
print("=" * 60)

if hash1.startswith('$argon2') and dollar_count == 5:
    print("✅ L'hash viene generato CORRETTAMENTE da PasswordHasher")
    print("\n⚠️  Se vedi 'argon2idargon2id' nel database, il problema è:")
    print("   1. Nel salvataggio su Supabase (encoding?)")
    print("   2. In una conversione/processing dell'hash")
    print("   3. In una lettura errata dal database")
    print("\n🔍 Verifica:")
    print("   - Controlla i log con il debug aggiunto")
    print("   - Guarda cosa viene realmente inviato a Supabase")
    print("   - Verifica il tipo di dato della colonna (TEXT)")
else:
    print("❌ L'hash NON viene generato correttamente!")
    print("   C'è un problema con argon2-cffi")

print("\n" + "=" * 60)
