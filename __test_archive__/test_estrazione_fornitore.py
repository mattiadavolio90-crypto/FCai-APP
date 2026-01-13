"""
Test script per verificare l'estrazione corretta dei fornitori
da fatture XML (società e persone fisiche)
"""
import xmltodict
import os
from utils.text_utils import normalizza_stringa

def safe_get(dizionario, percorso_chiavi, default=None, keep_list=False):
    """Naviga dizionario annidato in sicurezza"""
    valore_corrente = dizionario
    
    for chiave in percorso_chiavi:
        if isinstance(valore_corrente, dict):
            valore_corrente = valore_corrente.get(chiave)
            if valore_corrente is None:
                return default
            
            if isinstance(valore_corrente, list):
                if keep_list:
                    return valore_corrente if valore_corrente else default
                else:
                    if len(valore_corrente) > 0:
                        valore_corrente = valore_corrente[0]
                    else:
                        return default
        else:
            return default
    
    return valore_corrente if valore_corrente is not None else default


def estrai_fornitore_xml(fattura):
    """
    Estrae il nome del fornitore gestendo sia società che persone fisiche.
    
    Priorità:
    1. Denominazione (società)
    2. Nome + Cognome (persona fisica) 
    3. Solo Nome (fallback)
    4. "Fornitore Sconosciuto"
    """
    try:
        # Estrai nodo Anagrafica
        anagrafica = safe_get(
            fattura,
            ['FatturaElettronicaHeader', 'CedentePrestatore', 'DatiAnagrafici', 'Anagrafica'],
            default=None,
            keep_list=False
        )
        
        if anagrafica is None:
            return 'Fornitore Sconosciuto', 'Nodo Anagrafica non trovato'
        
        # Priorità 1: Denominazione (società)
        denominazione = safe_get(anagrafica, ['Denominazione'], default=None, keep_list=False)
        if denominazione and isinstance(denominazione, str) and denominazione.strip():
            fornitore = normalizza_stringa(denominazione)
            return fornitore, f"🏢 Denominazione: '{denominazione}'"
        
        # Priorità 2: Nome + Cognome (persona fisica)
        nome = safe_get(anagrafica, ['Nome'], default=None, keep_list=False)
        cognome = safe_get(anagrafica, ['Cognome'], default=None, keep_list=False)
        
        nome_str = nome.strip() if nome and isinstance(nome, str) else ""
        cognome_str = cognome.strip() if cognome and isinstance(cognome, str) else ""
        
        if nome_str and cognome_str:
            fornitore = f"{nome_str} {cognome_str}".upper()
            return fornitore, f"👤 Nome+Cognome: '{nome}' + '{cognome}'"
        elif cognome_str:
            fornitore = cognome_str.upper()
            return fornitore, f"👤 Solo Cognome: '{cognome}'"
        elif nome_str:
            fornitore = nome_str.upper()
            return fornitore, f"👤 Solo Nome: '{nome}'"
        
        # Fallback finale
        return 'Fornitore Sconosciuto', '⚠️ Nessun campo fornitore trovato'
        
    except Exception as e:
        return 'Fornitore Sconosciuto', f'❌ Errore: {e}'


def test_file_xml(file_path):
    """Testa estrazione fornitore da un file XML"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            contenuto = f.read()
        
        doc = xmltodict.parse(contenuto)
        root_key = list(doc.keys())[0]
        fattura = doc[root_key]
        
        fornitore, dettaglio = estrai_fornitore_xml(fattura)
        
        print(f"\n{'='*80}")
        print(f"File: {os.path.basename(file_path)}")
        print(f"{'='*80}")
        print(f"Fornitore: {fornitore}")
        print(f"Dettaglio: {dettaglio}")
        print(f"{'='*80}")
        
    except Exception as e:
        print(f"\n❌ ERRORE nel file {file_path}: {e}")


if __name__ == "__main__":
    print("\n🧪 TEST ESTRAZIONE FORNITORI DA XML")
    print("="*80)
    
    # Testa tutti i file XML nella cartella dati_input
    dati_input_dir = "c:\\Users\\matti\\Desktop\\FCI_PROJECT\\dati_input"
    
    xml_files = [f for f in os.listdir(dati_input_dir) if f.endswith('.xml')]
    
    print(f"\nTrovati {len(xml_files)} file XML da testare\n")
    
    for xml_file in xml_files[:5]:  # Test primi 5 file
        file_path = os.path.join(dati_input_dir, xml_file)
        test_file_xml(file_path)
    
    print("\n✅ Test completato!")
