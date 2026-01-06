# 🎓 SISTEMA LEARNING DA CORREZIONI UTENTE

**Data Implementazione**: 30/12/2025  
**Versione**: 1.0  
**Obiettivo**: Memoria globale auto-migliorante tramite feedback utenti

---

## 🎯 PROBLEMA RISOLTO

### Prima (Senza Learning)
- ❌ Utente A corregge "POLLO RUSPANTE" da NO FOOD → CARNE
- ❌ Correzione salvata SOLO per Utente A
- ❌ Utente B riceve ancora NO FOOD (AI sbaglia di nuovo)
- ❌ Ogni utente deve correggere gli stessi errori
- ❌ Memoria globale non migliora

### Dopo (Con Learning)
- ✅ Utente A corregge "POLLO RUSPANTE" da NO FOOD → CARNE
- ✅ Correzione salvata in **memoria globale**
- ✅ Utente B riceve automaticamente CARNE (memoria usa correzione)
- ✅ Confidence = "altissima" (correzione umana)
- ✅ Memoria globale migliora continuamente

---

## 🧠 COME FUNZIONA

### Flusso Completo

```
┌──────────────────────────────────────────────┐
│ UTENTE MODIFICA CATEGORIA                    │
│ - Apre TAB "Dettaglio Articoli"             │
│ - Cambia categoria nella tabella            │
│ - Clicca "💾 Salva Modifiche Categorie"     │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│ SISTEMA SALVA MODIFICHE                      │
│ 1. Aggiorna database fatture                │
│ 2. Aggiorna memoria AI locale               │
│ 3. Chiama salva_correzione_in_memoria_globale() │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│ CHECK MEMORIA GLOBALE                        │
│ - Normalizza descrizione                    │
│ - Cerca in prodotti_master                  │
└──────────────────────────────────────────────┘
                    ↓
        ┌───────────┴───────────┐
        │                       │
    ESISTE                  NON ESISTE
        │                       │
        ↓                       ↓
┌─────────────┐        ┌─────────────┐
│ AGGIORNA    │        │ INSERISCI   │
│ - categoria │        │ - categoria │
│ - confidence│        │ - confidence│
│   (altissima)│        │   (altissima)│
│ - da utente │        │ - da utente │
└─────────────┘        └─────────────┘
        │                       │
        └───────────┬───────────┘
                    ↓
┌──────────────────────────────────────────────┐
│ PROSSIMI CARICAMENTI                         │
│ - TUTTI i clienti beneficiano               │
│ - Categoria corretta usata automaticamente  │
│ - Nessuna chiamata AI (usa memoria)        │
└──────────────────────────────────────────────┘
```

---

## 🔧 MODIFICHE IMPLEMENTATE

### 1. [app.py](app.py#L143) - Funzione `salva_correzione_in_memoria_globale()`

**Nuova funzione**:
```python
def salva_correzione_in_memoria_globale(descrizione, vecchia_categoria, nuova_categoria, user_email):
    """Salva correzione utente in memoria globale"""
    # Normalizza descrizione
    desc_normalized, desc_original = get_descrizione_normalizzata_e_originale(descrizione)
    
    # Check se esiste
    existing = supabase.table('prodotti_master').select(...).eq('descrizione', desc_normalized).execute()
    
    if existing.data:
        # AGGIORNA con categoria corretta
        supabase.table('prodotti_master').update({
            'categoria': nuova_categoria,
            'classificato_da': f'Utente ({user_email})',
            'confidence': 'altissima'  # Correzione umana = max confidenza
        }).execute()
    else:
        # INSERISCI nuovo record
        supabase.table('prodotti_master').insert({
            'descrizione': desc_normalized,
            'categoria': nuova_categoria,
            'classificato_da': f'Utente ({user_email})',
            'confidence': 'altissima',
            'volte_visto': 1
        }).execute()
```

### 2. [app.py](app.py#L3575) - Integrazione nel Salvataggio

**Modificato bottone "💾 Salva Modifiche Categorie"**:
```python
if result.data:
    aggiorna_memoria_ai(descrizione, nuova_cat)
    
    # NUOVO: Se categoria è cambiata, salva in memoria globale
    if vecchia_cat and vecchia_cat != nuova_cat:
        salva_correzione_in_memoria_globale(
            descrizione=descrizione,
            vecchia_categoria=vecchia_cat,
            nuova_categoria=nuova_cat,
            user_email=user_email
        )
```

### 3. [pages/admin.py](pages/admin.py#L680) - Sezione Correzioni TAB 4

**Aggiunta sezione "🎓 Correzioni Utente"**:
- Filtra prodotti con `classificato_da` contenente "Utente"
- Mostra metriche: prodotti corretti, utilizzi post-correzione
- Tabella con descrizione, categoria, utilizzi, corretto da
- Info se nessuna correzione

---

## 📊 ESEMPI REALI

### Caso 1: Primo Utente Corregge

**Scenario**:
1. Cliente A carica fattura con "POLLO RUSPANTE"
2. AI categorizza come "NO FOOD" (errore)
3. Utente A apre "Dettaglio Articoli"
4. Cambia categoria: NO FOOD → CARNE
5. Clicca "💾 Salva Modifiche"

**Risultato**:
```
📚 CORREZIONE UTENTE salvata in memoria: 'POLLO RUSPANTE' → CARNE (by cliente@example.com)
```

**Database `prodotti_master`**:
```
descrizione: POLLO RUSPANTE
categoria: CARNE
classificato_da: Utente (cliente@example.com)
confidence: altissima
volte_visto: 1
```

### Caso 2: Secondo Utente Beneficia

**Scenario**:
1. Cliente B (diverso) carica fattura con "POLLO RUSPANTE KG 1.5"
2. Sistema normalizza: "POLLO RUSPANTE KG 1.5" → "POLLO RUSPANTE"
3. Cerca in memoria globale
4. **TROVA** record (salvato da Cliente A)
5. Usa categoria CARNE direttamente

**Log**:
```
🧠 MEMORIA GLOBALE: 'POLLO RUSPANTE KG 1.5' → CARNE (visto 2x, norm: 'POLLO RUSPANTE')
```

**Nessuna correzione necessaria! ✅**

### Caso 3: Terzo Utente (Stesso Prodotto)

**Scenario**:
1. Cliente C carica "POLLO RUSPANTE BIOLOGICO"
2. Normalizza: "POLLO RUSPANTE BIOLOGICO" → "POLLO RUSPANTE BIOLOGICO"
3. **NON** trova in memoria (variante diversa)
4. Usa keyword → CARNE (giusto per fortuna)
5. Salva "POLLO RUSPANTE BIOLOGICO" in memoria

**Nota**: Varianti molto diverse potrebbero non matchare, serve normalizzazione più aggressiva o sinonimi.

---

## 🎯 BENEFICI

### ✅ Qualità Crescente
- Memoria migliora con ogni correzione
- Errori AI corretti una sola volta
- Confidence aumenta (altissima per correzioni umane)

### ✅ Esperienza Utente
- Meno correzioni manuali nel tempo
- Sistema "impara" dalle interazioni
- Nuovi clienti beneficiano subito

### ✅ Scalabilità
- 1000 clienti = 1000 correttori
- Crowd-sourced training gratuito
- Database self-improving

### ✅ Trasparenza
- Admin vede chi ha corretto cosa
- Tracciamento modifiche
- Audit trail completo

---

## 🧪 TESTING

### Test 1: Correzione Salva in Memoria

1. **Carica fattura** con prodotto mal categorizzato
2. **Vai su "Dettaglio Articoli"**
3. **Cambia categoria** nella tabella
4. **Clicca "💾 Salva Modifiche Categorie"**
5. **Verifica log console**:
   ```
   📚 CORREZIONE UTENTE salvata in memoria: 'NOME PRODOTTO' → CATEGORIA (by tuo@email.com)
   ```
6. **Vai su Admin Panel → TAB 4**
7. **Scroll giù** fino a "🎓 Correzioni Utente"
8. **Verifica** prodotto appare nella lista ✅

### Test 2: Secondo Utente Usa Correzione

1. **Logout** dal primo utente
2. **Login** con altro account (o usa Impersonazione admin)
3. **Carica fattura** con STESSO prodotto (anche con variante peso/misura)
4. **Verifica categoria automatica** = quella corretta ✅
5. **Controlla log**:
   ```
   🧠 MEMORIA GLOBALE: 'PRODOTTO' → CATEGORIA (visto 2x, norm: '...')
   ```

### Test 3: Admin Vede Statistiche

1. **Vai Admin Panel → TAB 4**
2. **Scroll a "🎓 Correzioni Utente"**
3. **Verifica metriche**:
   - Prodotti Corretti > 0 ✅
   - Utilizzi Post-Correzione ≥ Prodotti Corretti ✅
4. **Tabella mostra**:
   - Descrizione prodotto
   - Categoria corretta
   - Utilizzi (quante volte usato dopo correzione)
   - Corretto da (email utente)
   - Ultima modifica

---

## 📊 METRICHE ATTESE

### Dopo 1 Settimana
- Correzioni: 10-50
- Prodotti migliorati: 5-10%
- Riuso correzioni: 2-5x per prodotto

### Dopo 1 Mese
- Correzioni: 100-300
- Prodotti migliorati: 20-30%
- Riuso correzioni: 5-15x per prodotto
- **Qualità categorizzazione: +15%** 🎯

### Dopo 6 Mesi
- Correzioni: 500-1500
- Prodotti migliorati: 60-80%
- Riuso correzioni: 20-50x per prodotto
- **Qualità categorizzazione: +40%** 🎯
- Interventi manuali: **-70%** ⚡

---

## 🔮 ROADMAP FUTURI MIGLIORAMENTI

### Fase 2: Confidence Voting
- [ ] Se 3+ utenti confermano stessa categoria → confidence "massima"
- [ ] Se utenti discordano → flag "revisione necessaria"
- [ ] Admin panel mostra prodotti con conflitti

### Fase 3: Suggerimenti Proattivi
- [ ] Sistema suggerisce correzioni probabili
- [ ] "Hai categorizzato X come Y, confermi?"
- [ ] One-click per accettare/rifiutare

### Fase 4: Machine Learning
- [ ] Analizza pattern correzioni
- [ ] Predice categorie con ML model
- [ ] Auto-correzione errori frequenti

### Fase 5: Gamification
- [ ] Badge per utenti che correggono molto
- [ ] Leaderboard correttori top
- [ ] Statistiche contributi per cliente

---

## 🐛 TROUBLESHOOTING

### Problema: Correzione non salvata in memoria globale

**Causa**: Errore durante INSERT/UPDATE

**Debug**:
1. Controlla log: cerca `📚 CORREZIONE UTENTE`
2. Se vedi errore, controlla Supabase (table exists? permissions?)
3. Verifica che tabella `prodotti_master` esista

### Problema: Correzione salvata ma non usata

**Causa**: Normalizzazione non matcha

**Debug**:
```python
from app import normalizza_descrizione
desc1 = "POLLO INTERO KG 2.5"
desc2 = "POLLO INTERO"
print(normalizza_descrizione(desc1))  # Devono matchare
print(normalizza_descrizione(desc2))
```

### Problema: Admin panel non mostra correzioni

**Causa**: Filtro `classificato_da` non trova "Utente"

**Soluzione**: Verifica che `classificato_da` contenga "Utente" nel database

---

## 📚 CAMPO `confidence` NEL DATABASE

### Livelli Confidence

- **`bassa`**: Categoria da dizionario keyword (pattern match generico)
- **`media`**: Categoria da dizionario keyword specifico
- **`alta`**: Categoria da AI OpenAI
- **`altissima`**: Categoria corretta manualmente da utente ⭐

### Priorità Uso

Quando memoria globale ha prodotto con confidence:
1. **altissima** → Usa sempre (correzione umana)
2. **alta** → Usa (AI)
3. **media** → Usa (keyword)
4. **bassa** → Usa ma considera re-check

---

## 🔗 LINK UTILI

- **Funzione Salvataggio**: [app.py#L143](app.py#L143)
- **Integrazione**: [app.py#L3575](app.py#L3575)
- **Admin Panel**: [pages/admin.py#L680](pages/admin.py#L680)
- **Normalizzazione**: [app.py#L19](app.py#L19)

---

## 📞 SUPPORTO

**File Modificati**:
- [app.py](app.py) - Funzione salvataggio + integrazione
- [pages/admin.py](pages/admin.py) - Sezione correzioni TAB 4

**Log da Monitorare**:
- `📚 CORREZIONE UTENTE salvata` = Nuovo record
- `📚 CORREZIONE UTENTE aggiornata` = Record esistente modificato
- `🧠 MEMORIA GLOBALE: ... (Utente)` = Uso correzione utente

**Metriche Chiave**:
- Prodotti corretti: target **>100** dopo 1 mese
- Riuso correzioni: target **>5x** media
- Qualità categorizzazione: target **+40%** dopo 6 mesi

---

**Implementato**: 30/12/2025  
**Status**: ✅ Pronto per produzione  
**Testing**: In corso  
**Impact**: **Sistema auto-migliorante** 🎓
