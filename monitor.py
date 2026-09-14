import os
import time
import requests
from bs4 import BeautifulSoup
import random  # Aggiunto per generare pause casuali

# Recupera i dati dai segreti di GitHub che abbiamo impostato
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

URLS = [
    "https://www.ticketone.it/event/harry-styles-together-together-circo-massimo-22109735/",
    "https://www.ticketone.it/event/harry-styles-together-together-circo-massimo-22114624/",
    "https://www.ticketmaster.it/biglietti/harry-styles-together-together-roma-07-08-2027/event/72zs3kweso14/ticketmaster",
    "https://www.ticketmaster.it/biglietti/harry-styles-together-together-roma-08-08-2027/event/t6u6dw40wb3n/ticketmaster"
]

# Inseriamo SOLO le zone che ti interessano. Ho volutamente escluso "Posto Unico".
ZONE_INTERESSATE = [
    "Circle PIT",
    "Disco PIT",
    "Kiss PIT",
    "Square PIT",
    "Front Standing",
    "Front Standing Lateral"
]

def invia_messaggio_telegram(messaggio):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Errore: Credenziali Telegram mancanti!")
        return
        
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": messaggio,
        "parse_mode": "HTML"
    }
    requests.post(url, json=payload)

def controlla_biglietti():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, come Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    for url in URLS:
        try:
            risposta = requests.get(url, headers=headers, timeout=10)
            
            if risposta.status_code == 200:
                soup = BeautifulSoup(risposta.text, "html.parser")
                testo_pagina = soup.get_text(separator=" ", strip=True)
                
                # TRUCCO: Trasformiamo TUTTO il testo della pagina in minuscolo
                testo_pagina_lower = testo_pagina.lower()
                
                zone_trovate = []
                
                for zona in ZONE_INTERESSATE:
                    # Trasformiamo in minuscolo anche il nome della zona che stiamo cercando
                    zona_lower = zona.lower()
                    
                    if zona_lower in testo_pagina_lower:
                        # Troviamo l'indice nel testo tutto in minuscolo
                        indice = testo_pagina_lower.find(zona_lower)
                        
                        # Ritagliamo i 200 caratteri successivi
                        contesto = testo_pagina_lower[indice : indice + 200]
                        
                        # Cerchiamo le parole di esaurimento (scritte rigorosamente in minuscolo!)
                        if "non disponibile" not in contesto and "esaurito" not in contesto and "sold out" not in contesto:
                            # Aggiungiamo la 'zona' originale (con le maiuscole belle da vedere) alla lista
                            zone_trovate.append(zona)
                
                if len(zone_trovate) > 0:
                    elenco = "\n- ".join(zone_trovate)
                    testo = f"🚨 <b>ALLARME HARRY STYLES!</b> 🚨\n\nHai trovato i biglietti! Settori disponibili:\n- {elenco}\n\nCorri: {url}"
                    invia_messaggio_telegram(testo)
                    print(f"Trovata disponibilità per {url}: {zone_trovate}")
                else:
                    print(f"Nessuna delle zone premium disponibile per: {url[-10:]}")
                    
            elif risposta.status_code == 403:
                print("TicketOne ci ha temporaneamente bloccato (Errore 403).")
                
        except Exception as e:
            print(f"Errore: {e}")
            
        # Pausa CASUALE tra 4 e 12 secondi (fa impazzire i sistemi antibot perché sembra umano!)
        attesa_casuale = random.randint(4, 12)
        print(f"Aspetto {attesa_casuale} secondi prima della prossima data...")
        time.sleep(attesa_casuale)

if __name__ == "__main__":
    controlla_biglietti()
