import  requests                        #Requests zum Prüfen von Webseiten und APIs per HTTP-Anfragen,urls prüfen und Serverantworten auszulesen
import time
from urllib.parse import urlparse       #urlparse zum Zerlegen und Auslesen von Bestandteilen einer URL
import ssl                              #SSL/TLS = Transport Layer Security, sorgt für verschlüsselte Verbindungen und Zertifikatsprüfung
import socket                           #für eine direkte Netzwerkverbindung zum Server
from datetime import datetime           #datetime zum Erstellen, Umwandeln und Vergleichen von Datum und Uhrzeit



def run_test(url):
    start = time.time()                 #time.time() aus dem time Modul gibt die aktuelle Zeit in Sekunden zurück.

    try:
        print("URL:", url)
        parsed_url = urlparse(url)      #parsed_url  zerlegt die komplette

        hostname = parsed_url.hostname
        context = ssl.create_default_context()                          #erstellt die Standard-TLS-Einstellungen für die Zertifikatsprüfung

        with socket.create_connection((hostname, 443), timeout=10) as sock:             #port 443 standartsgemäß für https
            with context.wrap_socket(sock, server_hostname=hostname) as connection:             #wrap_socket = daraus eine TLS-Verbindung machen
                certificate = connection.getpeercert()                  #getpeercert()=Zertifikat des Servers holen
        print("SSL/TLS: PASS")
        expiration_date = certificate["notAfter"]                   #notAfter = Datum, bis zu dem das Zertifikat gültig ist
        expiration_date = datetime.strptime(expiration_date,"%b %d %H:%M:%S %Y %Z")     # wandelt den Text des Ablaufdatums in ein datetime-Objekt um

        current_date = datetime.now()
        if expiration_date > current_date:
            print("Certificate: PASS")
        else:
            print("Certificate: FAIL - expired")


        response = requests.get(url, timeout=10)


        final_url = urlparse(response.url)
        start_domain = parsed_url.hostname.removeprefix("www.")
        final_domain = final_url.hostname.removeprefix("www.")

        if start_domain == final_domain:         #hostname gibt den Hostnamen der URL zurück
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
    except requests.exceptions.TooManyRedirects:
        print("Redirect: FAIL - too many redirects")
    except requests.exceptions.SSLError:
        print("SSL/TLS: FAIL - certificate error")
    except requests.exceptions.RequestException:
        print("Website nicht erreichbar")
        return

