import os
from supabase import create_client
from openai import OpenAI
import toml

# Carica secrets
secrets_path = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")
secrets = toml.load(secrets_path)
SUPABASE_URL = secrets["supabase"]["url"]
SUPABASE_KEY = secrets["supabase"]["key"]
OPENAI_API_KEY = secrets["OPENAI_API_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
client = OpenAI(api_key=OPENAI_API_KEY)

# Test categorizzazione AI
descrizione = "COPPETTA SANGO 10CM WB"
fornitore = "FABRIZIO CARUSO"

print(f"🧠 Test AI categorizzazione:")
print(f"   Descrizione: {descrizione}")
print(f"   Fornitore: {fornitore}\n")

# Categorie disponibili
CATEGORIE = [
    "CARNE", "PESCE", "VERDURE", "FRUTTA", "LATTICINI",
    "PANE E PIZZA", "PASTA", "RISO", "FARINE", "DOLCI E DESSERT",
    "SALUMI E AFFETTATI", "FORMAGGI", "UOVA", "CONDIMENTI",
    "BEVANDE ALCOLICHE", "BEVANDE ANALCOLICHE", "CAFFÈ",
    "SURGELATI", "CONSERVE", "SECCO", "ALTRO FOOD"
]

prompt = f"""Classifica questo prodotto in una delle categorie disponibili:

Descrizione: {descrizione}
Fornitore: {fornitore}

Categorie disponibili: {', '.join(CATEGORIE)}

REGOLE:
- "COPPETTA", "PIATTO", "BICCHIERE", "POSATE" = ALTRO FOOD (utensili/contenitori)
- Rispondi SOLO con il nome della categoria, niente altro
- Se non sei sicuro, usa "ALTRO FOOD"
"""

try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Sei un esperto classificatore di prodotti alimentari e per ristorazione."},
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        max_tokens=50
    )
    
    categoria = response.choices[0].message.content.strip()
    print(f"✅ AI risposta: '{categoria}'")
    
    # Verifica se è una categoria valida
    if categoria in CATEGORIE:
        print(f"✅ Categoria valida!")
    else:
        print(f"⚠️ Categoria NON nella lista: '{categoria}'")
        print(f"   Categorie valide: {CATEGORIE}")
        
except Exception as e:
    print(f"❌ Errore AI: {e}")
