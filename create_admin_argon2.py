import streamlit as st
from supabase import create_client, Client
from argon2 import PasswordHasher

print("=" * 60)
print("👤 CREAZIONE UTENTE ADMIN (Argon2)")
print("=" * 60)

# Connetti a Supabase (usa secrets di Streamlit)
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ============================================
# INSERISCI I TUOI DATI QUI
# ============================================
EMAIL_ADMIN = "mattiadavolio90@gmail.com"
PASSWORD_ADMIN = "Cratos.2025@VS"
NOME_RISTORANTE = "Admin"
# ============================================

print(f"📧 Email: {EMAIL_ADMIN}")
print(f"🏪 Ristorante: {NOME_RISTORANTE}")

ph = PasswordHasher()

try:
    # Elimina eventuale utente esistente con stessa email
    supabase.table('users').delete().eq('email', EMAIL_ADMIN).execute()

    # Crea hash Argon2
    password_hash = ph.hash(PASSWORD_ADMIN)

    # Inserisci utente admin
    response = supabase.table('users').insert({
        'email': EMAIL_ADMIN,
        'password_hash': password_hash,
        'nome_ristorante': NOME_RISTORANTE,
        'piano': 'enterprise',
        'ruolo': 'admin',
        'attivo': True
    }).execute()

    print("✅ UTENTE ADMIN CREATO CON SUCCESSO (Argon2)!")
    print()
    print("🔑 Credenziali di accesso:")
    print(f"   Email: {EMAIL_ADMIN}")
    print(f"   Password: {PASSWORD_ADMIN}")
    print()
    print("⚠️  IMPORTANTE: Salva queste credenziali!")
    print("=" * 60)

except Exception as e:
    if "duplicate key" in str(e).lower():
        print("⚠️  Utente già esistente!")
    else:
        print(f"❌ ERRORE: {e}")
