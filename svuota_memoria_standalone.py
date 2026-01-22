#!/usr/bin/env python3
"""Script standalone per svuotare la memoria globale AI"""

def main():
    """Svuota memoria globale con import inline"""
    import sys
    from pathlib import Path
    
    # Aggiungi path progetto
    BASE_DIR = Path(__file__).parent
    sys.path.insert(0, str(BASE_DIR))
    
    # Import inline per evitare problemi con venv
    print("📦 Caricamento moduli...")
    
    try:
        # Carica secrets manualmente
        secrets_file = BASE_DIR / '.streamlit' / 'secrets.toml'
        if not secrets_file.exists():
            print(f"❌ File secrets non trovato: {secrets_file}")
            return False
        
        # Parse manuale TOML (senza librerie esterne)
        secrets = {}
        current_section = None
        with open(secrets_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('[') and line.endswith(']'):
                    current_section = line[1:-1]
                    secrets[current_section] = {}
                elif '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if current_section:
                        secrets[current_section][key] = value
                    else:
                        secrets[key] = value
        
        supabase_url = secrets.get('supabase', {}).get('url')
        supabase_key = secrets.get('supabase', {}).get('key')
        
        if not supabase_url or not supabase_key:
            print("❌ SUPABASE_URL o SUPABASE_KEY non trovate in secrets.toml")
            return False
        
        print(f"🔗 Connessione a Supabase: {supabase_url[:30]}...")
        
        # Import supabase
        try:
            from supabase import create_client
        except ImportError:
            print("❌ Modulo 'supabase' non installato")
            print("   Installalo con: pip install supabase")
            return False
        
        supabase = create_client(supabase_url, supabase_key)
        
        # Preleva tutti i record
        print("📊 Caricamento record da prodotti_master...")
        resp = supabase.table('prodotti_master').select('id').execute()
        ids = [row['id'] for row in (resp.data or []) if 'id' in row]
        
        if not ids:
            print("ℹ️  Memoria globale già vuota (0 record)")
            return True
        
        print(f"🗑️  Cancellazione {len(ids)} record...")
        
        # Cancella in batch
        batch_size = 1000
        deleted = 0
        for i in range(0, len(ids), batch_size):
            batch = ids[i:i+batch_size]
            supabase.table('prodotti_master').delete().in_('id', batch).execute()
            deleted += len(batch)
            print(f"   → {deleted}/{len(ids)} record cancellati")
        
        print(f"✅ Memoria globale svuotata: {deleted} record rimossi")
        
        # Cancella file legacy se esiste
        legacy_file = BASE_DIR / 'memoria_ai_correzioni.json'
        if legacy_file.exists():
            legacy_file.unlink()
            print("🧹 File legacy memoria_ai_correzioni.json rimosso")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
