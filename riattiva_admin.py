"""
Script per creare o riattivare account admin.
"""
import os
import sys
import hashlib
from datetime import datetime

# Aggiungi il path del progetto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from services import get_supabase_client
    
    # Configurazione admin
    ADMIN_EMAIL = "mattiadavolio90@gmail.com"
    ADMIN_PASSWORD = "admin123"  # Password di default - CAMBIARLA dopo primo accesso!
    ADMIN_NOME = "Mattia Davolio - Admin"
    
    print(f"🔄 Gestione account admin: {ADMIN_EMAIL}")
    print("=" * 60)
    
    # Connessione al database
    supabase = get_supabase_client()
    
    # Verifica stato corrente
    print("\n📊 Verifica stato corrente...")
    response = supabase.table("users").select("*").eq("email", ADMIN_EMAIL).execute()
    
    if not response.data:
        print(f"⚠️  Account {ADMIN_EMAIL} non trovato!")
        print("   Procedo con la creazione di un nuovo account admin...")
        
        # Crea hash password (SHA256)
        password_hash = hashlib.sha256(ADMIN_PASSWORD.encode()).hexdigest()
        
        # Crea nuovo account admin
        new_admin = {
            'email': ADMIN_EMAIL.lower().strip(),
            'nome_ristorante': ADMIN_NOME,
            'password_hash': password_hash,
            'attivo': True,  # Account attivo da subito
            'created_at': datetime.utcnow().isoformat(),
            'login_attempts': 0,
            'partita_iva': None,
            'ragione_sociale': None,
            'reset_code': None,
            'reset_expires': None,
            'password_changed_at': datetime.utcnow().isoformat()
        }
        
        insert_response = supabase.table("users").insert(new_admin).execute()
        
        if insert_response.data:
            print(f"\n✅ Account admin creato con successo!")
            print(f"\n📧 Email: {ADMIN_EMAIL}")
            print(f"🔑 Password: {ADMIN_PASSWORD}")
            print(f"\n⚠️  IMPORTANTE: Cambia la password dopo il primo accesso!")
        else:
            print(f"\n❌ ERRORE durante la creazione!")
            print(f"   Dettagli: {insert_response}")
            sys.exit(1)
            
    else:
        # Account esiste
        user = response.data[0]
        stato_attuale = user.get("attivo", False)
        
        print(f"\n✅ Account trovato nel database:")
        print(f"   • Email: {user.get('email')}")
        print(f"   • Nome: {user.get('nome_ristorante', 'N/A')}")
        print(f"   • P.IVA: {user.get('partita_iva', 'N/A')}")
        print(f"   • Stato attivo: {stato_attuale}")
        print(f"   • Creato: {user.get('created_at', 'N/A')}")
        print(f"   • Ultimo accesso: {user.get('last_login', 'Mai')}")
        
        if stato_attuale:
            print("\n✅ L'account è già attivo!")
            print("\n   Se non riesci ad accedere, controlla:")
            print("   - Password corretta")
            print("   - Cache del browser (prova CTRL+F5)")
            print("   - Connessione al database")
            
            # Offri opzione di reset password
            print(f"\n💡 Vuoi resettare la password a: {ADMIN_PASSWORD} ?")
            risposta = input("   Digita 'SI' per confermare: ").strip().upper()
            
            if risposta == "SI":
                password_hash = hashlib.sha256(ADMIN_PASSWORD.encode()).hexdigest()
                update_response = supabase.table("users").update({
                    "password_hash": password_hash,
                    "password_changed_at": datetime.utcnow().isoformat(),
                    "login_attempts": 0
                }).eq("email", ADMIN_EMAIL).execute()
                
                if update_response.data:
                    print(f"\n✅ Password resettata con successo!")
                    print(f"🔑 Nuova password: {ADMIN_PASSWORD}")
                else:
                    print(f"\n❌ ERRORE durante il reset!")
            else:
                print("\n   Reset password annullato.")
        else:
            print("\n⚠️  Account DISATTIVATO - procedo con la riattivazione...")
            
            # Riattiva account
            update_response = supabase.table("users").update({
                "attivo": True,
                "login_attempts": 0
            }).eq("email", ADMIN_EMAIL).execute()
            
            if update_response.data:
                print(f"\n✅ Account riattivato con successo!")
                print(f"\n🎉 Ora puoi accedere all'app con le tue credenziali.")
            else:
                print(f"\n❌ ERRORE durante la riattivazione!")
                print(f"   Dettagli: {update_response}")
                sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ Script completato con successo")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ ERRORE: {str(e)}")
    print(f"   Tipo: {type(e).__name__}")
    import traceback
    print("\n📋 Stack trace completo:")
    traceback.print_exc()
    sys.exit(1)
