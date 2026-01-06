"""
🧪 TEST PANNELLO ADMIN - CHECK FORNITORI AI
===========================================
Script per testare le funzionalità del pannello admin senza interfaccia Streamlit
"""

import sys
import os
from argon2 import PasswordHasher
import secrets
import string

print("=" * 60)
print("🧪 TEST PANNELLO ADMIN")
print("=" * 60)

# ============================================================
# TEST 1: Generazione Password
# ============================================================

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

print("\n📝 TEST 1: Generazione Password")
print("-" * 60)

for i in range(5):
    pwd = genera_password_sicura()
    print(f"Password {i+1}: {pwd}")
    
    # Verifica requisiti
    ha_maiuscola = any(c.isupper() for c in pwd)
    ha_minuscola = any(c.islower() for c in pwd)
    ha_numero = any(c.isdigit() for c in pwd)
    ha_simbolo = any(c in "!@#$%&*" for c in pwd)
    lunghezza_ok = len(pwd) >= 12
    
    if all([ha_maiuscola, ha_minuscola, ha_numero, ha_simbolo, lunghezza_ok]):
        print(f"   ✅ VALIDA (Lung: {len(pwd)}, Mai: ✓, Min: ✓, Num: ✓, Sim: ✓)")
    else:
        print(f"   ❌ PROBLEMI: Mai:{ha_maiuscola}, Min:{ha_minuscola}, Num:{ha_numero}, Sim:{ha_simbolo}, Lung:{lunghezza_ok}")

# ============================================================
# TEST 2: Hash Argon2
# ============================================================

print("\n🔐 TEST 2: Hash Argon2")
print("-" * 60)

ph = PasswordHasher()

password_test = "TestPassword123!"
print(f"Password originale: {password_test}")

# Genera hash
hash_password = ph.hash(password_test)
print(f"Hash generato: {hash_password[:50]}...")
print(f"Lunghezza hash: {len(hash_password)} caratteri")

# Verifica hash
try:
    ph.verify(hash_password, password_test)
    print("✅ Verifica password corretta: SUCCESSO")
except Exception as e:
    print(f"❌ Verifica fallita: {e}")

# Verifica password errata
try:
    ph.verify(hash_password, "PasswordErrata")
    print("❌ BUG: Verifica password errata dovrebbe fallire!")
except Exception:
    print("✅ Verifica password errata: RESPINTA correttamente")

# ============================================================
# TEST 3: Connessione Supabase
# ============================================================

print("\n🗄️  TEST 3: Connessione Supabase")
print("-" * 60)

try:
    import streamlit as st
    from supabase import create_client, Client
    
    supabase_url = st.secrets["supabase"]["url"]
    supabase_key = st.secrets["supabase"]["key"]
    supabase: Client = create_client(supabase_url, supabase_key)
    
    print(f"✅ Connessione stabilita")
    print(f"   URL: {supabase_url[:30]}...")
    
    # Test query (conta utenti)
    response = supabase.table('users').select('id', count='exact').execute()
    count = response.count if hasattr(response, 'count') else len(response.data or [])
    print(f"✅ Query test: {count} utenti nel database")
    
except Exception as e:
    print(f"❌ Errore connessione Supabase: {e}")
    print("⚠️  Verifica configurazione secrets.toml")

# ============================================================
# TEST 4: Configurazione Brevo
# ============================================================

print("\n📧 TEST 4: Configurazione Brevo")
print("-" * 60)

try:
    import streamlit as st
    
    brevo_cfg = st.secrets.get('brevo')
    
    if not brevo_cfg:
        print("❌ Sezione [brevo] non trovata in secrets.toml")
    else:
        api_key = brevo_cfg.get('api_key')
        sender_email = brevo_cfg.get('sender_email')
        sender_name = brevo_cfg.get('sender_name')
        
        if api_key:
            print(f"✅ API Key trovata: {api_key[:20]}...")
        else:
            print("❌ API Key non configurata")
        
        if sender_email:
            print(f"✅ Sender Email: {sender_email}")
        else:
            print("⚠️  Sender Email non configurato (userà default)")
        
        if sender_name:
            print(f"✅ Sender Name: {sender_name}")
        else:
            print("⚠️  Sender Name non configurato (userà default)")
        
        # Test invio (commentato per non inviare email durante test)
        print("\n💡 Per testare invio email, usa: test_brevo.py")
        
except Exception as e:
    print(f"❌ Errore configurazione Brevo: {e}")

# ============================================================
# TEST 5: Configurazione App URL
# ============================================================

print("\n🌐 TEST 5: Configurazione App URL")
print("-" * 60)

try:
    import streamlit as st
    
    app_url = st.secrets.get('app', {}).get('url')
    
    if not app_url:
        print("⚠️  URL app non configurato in secrets.toml")
        print("    Le email useranno: https://tuaapp.streamlit.app")
        print("    Aggiungi in secrets.toml:")
        print("    [app]")
        print("    url = \"https://tuaapp.streamlit.app\"")
    else:
        print(f"✅ URL App configurato: {app_url}")
        
        # Verifica formato URL
        if app_url.startswith('http://') or app_url.startswith('https://'):
            print("✅ Formato URL corretto")
        else:
            print("⚠️  URL dovrebbe iniziare con http:// o https://")
        
except Exception as e:
    print(f"❌ Errore verifica URL: {e}")

# ============================================================
# TEST 6: Admin Emails
# ============================================================

print("\n👤 TEST 6: Configurazione Admin")
print("-" * 60)

ADMIN_EMAILS = ["mattiadavolio90@gmail.com"]

print(f"Admin configurati: {len(ADMIN_EMAILS)}")
for email in ADMIN_EMAILS:
    print(f"   • {email}")

print("\n⚠️  IMPORTANTE:")
print("   Lista admin deve coincidere in:")
print("   1. app.py (linea ~650)")
print("   2. pages/admin.py (linea ~20)")

# ============================================================
# TEST 7: Struttura File
# ============================================================

print("\n📁 TEST 7: Struttura File")
print("-" * 60)

file_da_verificare = [
    ("app.py", "File principale applicazione"),
    ("pages/admin.py", "Pannello amministrazione"),
    ("pages/cambio_password.py", "Pagina cambio password"),
    (".streamlit/secrets.toml", "Configurazione secrets"),
    ("ADMIN_PANEL_README.md", "Documentazione pannello admin"),
    ("GUIDA_RAPIDA_ADMIN.md", "Guida rapida"),
]

for file_path, descrizione in file_da_verificare:
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        print(f"✅ {file_path} ({size} bytes)")
        print(f"   {descrizione}")
    else:
        print(f"⚠️  {file_path} - NON TROVATO")
        print(f"   {descrizione}")

# ============================================================
# RIEPILOGO
# ============================================================

print("\n" + "=" * 60)
print("📊 RIEPILOGO TEST")
print("=" * 60)

print("""
✅ Componenti Verificati:
   • Generazione password sicure
   • Hash Argon2
   • Connessione database
   • Configurazione email
   • Struttura file

💡 Prossimi Passi:
   1. Verifica file secrets.toml completo
   2. Testa invio email con test_brevo.py
   3. Avvia app: streamlit run app.py
   4. Login come admin
   5. Testa creazione cliente
   6. Verifica ricezione email

⚠️  Ricorda:
   • Non committare secrets.toml su Git
   • Configura URL app reale
   • Testa in ambiente sviluppo prima di produzione
""")

print("=" * 60)
print("🎉 TEST COMPLETATI!")
print("=" * 60)
