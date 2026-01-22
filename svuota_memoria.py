#!/usr/bin/env python3
"""Script per svuotare la memoria globale AI"""
import os
import sys
from pathlib import Path

# Configura percorso
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

# Import streamlit per accedere ai secrets
try:
    import streamlit as st
    from services import get_supabase_client
except ImportError as e:
    print(f"❌ Errore import: {e}")
    sys.exit(1)

def main():
    """Svuota memoria globale"""
    try:
        # Crea client Supabase
        supabase = get_supabase_client()
        
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
    success = main()
    sys.exit(0 if success else 1)
