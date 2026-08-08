import  requests                        #Requests zum Prüfen von Webseiten und APIs per HTTP-Anfragen,urls prüfen und Serverantworten auszulesen
import time
from urllib.parse import urlparse       #urlparse zum Zerlegen und Auslesen von Bestandteilen einer URL



def run_test(url):
    start = time.time()                 #time.time() aus dem time Modul gibt die aktuelle Zeit in Sekunden zurück.

    try:
        parsed_url = urlparse(url)      #parsed_url  zerlegt die komplette URL
        response = requests.get(url, timeout=10)
        final_url = urlparse(response.url)

        print("URL:", url)

        if parsed_url.hostname == final_url.hostname:               #hostname gibt den Hostnamen der URL zurück
            print("Domain: PASS")
        else:
            print("Domain: WARNING - different domain")

        if response.url.startswith("https://"):
            print("HTTPS: PASS")
        else:
            print("HTTPS: FAIL")

        end = time.time()

        if 200 <= response.status_code < 300:
            print("Status: PASS")
        elif 300 <= response.status_code < 400:
            print("Status: REDIRECT")
        elif 400 <= response.status_code < 500:
            print("Status: FAIL - Client Fehler")
        elif 500 <= response.status_code < 600:
            print("Status: FAIL - Server Fehler")
        else:
            print("Status: Unbekannter Status")

        response_time = round(end - start, 2)               # round(..., 2) rundet auf 2 Nachkommastellen

        if response_time < 2:
            print("Performance: PASS")
        elif response_time <= 3:
            print("Performance: WARNING SLOW")
        else:
            print("Performance: FAIL")


    except requests.exceptions.Timeout:
        print("Timeout: Anfrage dauerte länger als 10 Sekunden")
    except requests.exceptions.RequestException:
        print("Website nicht erreichbar")
        return

