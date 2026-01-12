from argon2 import PasswordHasher

ph = PasswordHasher()
password_hash = ph.hash("20162124")
print("\n=== HASH ARGON2 ===")
print(password_hash)
print("\n=== ISTRUZIONI ===")
print("1. Vai su Supabase Dashboard")
print("2. Table Editor → users")
print("3. Trova email: mattiadavolio90@gmail.com")
print("4. Modifica campi:")
print("   - active: true")
print("   - password: copia hash sopra")
print("5. Salva")
