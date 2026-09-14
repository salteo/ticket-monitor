import os
import time
import requests
from bs4 import BeautifulSoup

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
                # BeautifulSoup ci aiuta a estrarre solo il testo visibile dalla pagina, rimuovendo il codice HTML
                soup = BeautifulSoup(risposta.text, "html.parser")
                testo_pagina = soup.get_text(separator=" ", strip=True)
                
                zone_trovate = []
                
                for zona in ZONE_INTERESSATE:
                    if zona in testo_pagina:
                        # Troviamo a che punto del testo si trova il nome della zona
                        indice = testo_pagina.find(zona)
                        
                        # "Ritagliamo" i 200 caratteri successivi al nome della zona.
                        # Lì in mezzo ci sarà il prezzo, oppure la scritta "Non disponibile"
                        contesto = testo_pagina[indice : indice + 200]
                        
                        # Se nel testo vicino alla zona NON c'è scritto che è esaurita...
                        if "Non disponibile" not in contesto and "Esaurito" not in contesto:
                            zone_trovate.append(zona)
                
                # Se abbiamo trovato almeno una zona disponibile...
                if len(zone_trovate) > 0:
                    # Creiamo un bell'elenco puntato per il messaggio Telegram
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
            
        time.sleep(3) # Pausa tra una data e l'altra

if __name__ == "__main__":
    controlla_biglietti()
