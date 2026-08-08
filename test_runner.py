import  requests                        #Requests zum Prüfen von Webseiten und APIs per HTTP-Anfragen,urls prüfen und Serverantworten auszulesen
import time


def run_test(url):
    start = time.time()                 #time.time() aus dem time Modul gibt die aktuelle Zeit in Sekunden zurück.

    try:
        response = requests.get(url, timeout=10)

        end = time.time()

        print("URL:", url)

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

    except requests.exceptions.RequestException:
        print("Website nicht erreichbar")
        return

