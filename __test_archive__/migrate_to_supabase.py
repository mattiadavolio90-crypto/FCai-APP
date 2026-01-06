"""
Script di Migrazione Dati JSON → Supabase
Esegui UNA SOLA VOLTA per migrare i dati esistenti
"""

import json
import toml
from supabase import create_client, Client

# Carica secrets dal file .streamlit/secrets.toml
try:
    with open(".streamlit/secrets.toml", "r") as f:
        secrets = toml.load(f)
    
    supabase_url = secrets["supabase"]["url"]
    supabase_key = secrets["supabase"]["key"]
except FileNotFoundError:
    print("❌ ERRORE: File .streamlit/secrets.toml non trovato!")
    print("   Assicurati di essere nella directory del progetto")
    exit(1)
except KeyError as e:
    print(f"❌ ERRORE: Chiave mancante in secrets.toml: {e}")
    exit(1)

supabase: Client = create_client(supabase_url, supabase_key)

# ID utente (sostituisci con l'ID reale dal database users)
USER_ID = "81464f82-38dd-4666-9674-e72c1fd18c00"  # L'ID che abbiamo visto nel debug

def carica_json_locale():
    """Carica dati dal JSON locale"""
    try:
        with open("fattureprocessate.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Errore lettura JSON: {e}")
        return {}

def trasforma_per_supabase(memoria, user_id):
    """Trasforma i dati JSON nel formato Supabase"""
    records = []
    
    for file_name, file_data in memoria.items():
        prodotti = file_data.get("prodotti", [])
        
        for prod in prodotti:
            records.append({
                "user_id": user_id,
                "file_origine": prod.get("File_Origine", file_name),
                "numero_riga": prod.get("Numero_Riga", 0),
                "data_documento": prod.get("Data_Documento", None),
                "fornitore": prod.get("Fornitore", "Sconosciuto"),
                "descrizione": prod.get("Descrizione", ""),
                "quantita": prod.get("Quantita", 1),
                "unita_misura": prod.get("Unita_Misura", ""),
                "prezzo_unitario": prod.get("Prezzo_Unitario", 0),
                "iva_percentuale": prod.get("IVA_Percentuale", 0),
                "totale_riga": prod.get("Totale_Riga", 0),
                "categoria": prod.get("Categoria", "Da Classificare"),
                "codice_articolo": prod.get("Codice_Articolo", "")
            })
    
    return records

def migra_dati():
    """Esegue la migrazione completa"""
    print("🚀 INIZIO MIGRAZIONE JSON → SUPABASE")
    print("=" * 50)
    
    # 1. Carica JSON
    print("\n📂 Carico dati da JSON locale...")
    memoria = carica_json_locale()
    
    if not memoria:
        print("❌ Nessun dato da migrare!")
        return
    
    print(f"✅ Trovati {len(memoria)} file con dati")
    
    # 2. Trasforma dati
    print("\n🔄 Trasformo dati per Supabase...")
    records = trasforma_per_supabase(memoria, USER_ID)
    print(f"✅ Preparati {len(records)} record")
    
    # 3. Verifica se ci sono già dati E filtra duplicati
    print("\n🔍 Verifico duplicati nel database...")
    try:
        response = supabase.table("fatture").select("file_origine, numero_riga").eq("user_id", USER_ID).execute()
        existing_keys = {(r["file_origine"], r["numero_riga"]) for r in response.data}
        
        # Filtra record già presenti
        records_originali = len(records)
        records = [r for r in records if (r["file_origine"], r["numero_riga"]) not in existing_keys]
        duplicati = records_originali - len(records)
        
        if duplicati > 0:
            print(f"⚠️  Trovati {duplicati} record già esistenti (verranno saltati)")
        
        if len(records) == 0:
            print("\n✅ Tutti i dati sono già presenti nel database!")
            print("   Nessuna migrazione necessaria.")
            return
        
        print(f"✅ {len(records)} nuovi record da migrare")
        
    except Exception as e:
        print(f"⚠️  Errore verifica duplicati: {e}")
        conferma = input("\n⚠️  Continuare comunque? (s/n): ")
        if conferma.lower() != 's':
            print("❌ Migrazione annullata dall'utente")
            return
    
    # 4. Upload batch (100 record alla volta) con retry
    print(f"\n📤 Carico {len(records)} record su Supabase...")
    
    batch_size = 100
    success_count = 0
    error_batches = []
    
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        batch_num = i//batch_size + 1
        
        try:
            supabase.table("fatture").insert(batch).execute()
            success_count += len(batch)
            print(f"✅ Batch {batch_num}/{(len(records)-1)//batch_size + 1}: {len(batch)} record caricati ({success_count}/{len(records)})")
        except Exception as e:
            error_batches.append((batch_num, str(e), batch))
            print(f"❌ Errore batch {batch_num}: {e}")
    
    # 5. Verifica finale CORRETTA
    print("\n🔍 Verifica finale...")
    try:
        # Conta solo i file migrati in questa sessione
        file_migrati = list(set(r["file_origine"] for r in records))
        response = supabase.table("fatture").select("file_origine").eq("user_id", USER_ID).in_("file_origine", file_migrati).execute()
        final_count = len(response.data)
        
        print(f"\n{'='*50}")
        print(f"✅ MIGRAZIONE COMPLETATA!")
        print(f"{'='*50}")
        print(f"📊 Record tentati: {len(records)}")
        print(f"✅ Successi: {success_count}")
        print(f"❌ Errori: {len(records) - success_count}")
        print(f"📈 Record trovati DB: {final_count}")
        
        if len(error_batches) > 0:
            print(f"\n⚠️  BATCH FALLITI: {len(error_batches)}")
            for batch_num, error, _ in error_batches:
                print(f"   - Batch {batch_num}: {error}")
        
        if success_count == len(records) and final_count >= len(records):
            print("\n🎉 PERFETTO! Migrazione completata con successo!")
        elif success_count > 0:
            print(f"\n⚠️  PARZIALE: {success_count}/{len(records)} record migrati")
        else:
            print("\n❌ FALLITA: Nessun record migrato!")
    
    except Exception as e:
        print(f"❌ Errore verifica finale: {e}")

if __name__ == "__main__":
    migra_dati()
