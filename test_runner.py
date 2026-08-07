import  requests                        #Requests zum Prüfen von Webseiten und APIs per HTTP-Anfragen,urls prüfen und Serverantworten auszulesen
import time


def run_test(url):
    start = time.time()                 #time.time() aus dem time Modul gibt die aktuelle Zeit in Sekunden zurück.

    try:
        response = requests.get(url, timeout=10)

        end = time.time()

        print("URL:", url)
        print("Status:", response.status_code)
        print("Antwortzeit:", round(end - start, 2), "Sekunden")                # round(..., 2) rundet auf 2 Nachkommastellen

    except requests.exceptions.RequestException:
        print("Website nicht erreichbar")
        return