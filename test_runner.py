import  requests                        #Requests zum Prüfen von Webseiten und APIs per HTTP-Anfragen,urls prüfen und Serverantworten auszulesen
import time
from urllib.parse import urlparse       #urlparse zum Zerlegen und Auslesen von Bestandteilen einer URL
import ssl                              #SSL/TLS = Transport Layer Security, sorgt für verschlüsselte Verbindungen und Zertifikatsprüfung
import socket                           #für eine direkte Netzwerkverbindung zum Server
from datetime import datetime           #datetime zum Erstellen, Umwandeln und Vergleichen von Datum und Uhrzeit
import re                               #Regular Expressions= Suchmuster für Text

def run_test(url, expected_title, expected_text):
    print("URL:", url)


# --------------------------------------------------
# HTTP-Anfrage
# --------------------------------------------------
    try:
        start = time.time()
        response = requests.get(url, timeout=10)
        end = time.time()

    except requests.exceptions.Timeout as error:
        print("Timeout: Anfrage dauerte länger als 10 Sekunden", error)

    except requests.exceptions.TooManyRedirects as error:
        print("Redirect: FAIL - too many redirects", error)

    except requests.exceptions.SSLError as error:
        print("Request: FAIL - SSL/TLS certificate error", error)

    except requests.exceptions.RequestException as error:
        print("Website nicht erreichbar", error)


# --------------------------------------------------
# HTTPS
# --------------------------------------------------
    try:
        if response.url.startswith("https://"):
            print("HTTPS: PASS -", response.url)
        else:
            print("HTTPS: FAIL", response.url)

    except Exception as error:
        print("HTTPS: FAIL - konnte nicht geprüft werden: ", error)


# --------------------------------------------------
# SSL/TLS + Zertifikat
# --------------------------------------------------
    try:
        parsed_url = urlparse(url)      #parsed_url zerlegt die komplette URL

        hostname = parsed_url.hostname
        context = ssl.create_default_context()                          #erstellt die Standard-TLS-Einstellungen für die Zertifikatsprüfung

        with socket.create_connection((hostname, 443), timeout=10) as sock:             #Port 443 = Standardport für HTTPS
            with context.wrap_socket(sock, server_hostname=hostname) as connection:      #wrap_socket = daraus eine TLS-Verbindung machen
                certificate = connection.getpeercert()                                  #getpeercert() = Zertifikat des Servers holen
        print("SSL/TLS: PASS")

        expiration_date = certificate["notAfter"]                   #notAfter = Datum, bis zu dem das Zertifikat gültig ist
        expiration_date = datetime.strptime(expiration_date,"%b %d %H:%M:%S %Y %Z")     #wandelt den Text des Ablaufdatums in ein datetime-Objekt um

        current_date = datetime.now()

        if expiration_date > current_date:
            print("Certificate: PASS - gültig bis:", expiration_date)
        else:
            print("Certificate: FAIL - expired", expiration_date)

    except ssl.SSLCertVerificationError:        #fängt Zertifikatsfehler bei der direkten SSL/TLS-Verbindung mit socket ab
        print("SSL/TLS: FAIL - certificate error")

    except requests.exceptions.SSLError:        #fängt SSL/TLS-Fehler ab, die bei requests auftreten
        print("SSL/TLS: FAIL - certificate error")

    except ConnectionRefusedError as error:  # fängt Fehler ab, wenn der Server die Verbindung ablehnt
        print("SSL/TLS: FAIL - connection refused:", error)


# --------------------------------------------------
# Domain
# --------------------------------------------------
    try:
        final_url = urlparse(response.url)

        start_domain = parsed_url.hostname.removeprefix("www.")
        final_domain = final_url.hostname.removeprefix("www.")

        if start_domain == final_domain:         #hostname gibt den Hostnamen der URL zurück
            print("Domain: PASS -", start_domain, "→", final_domain)
        else:
            print("Domain: WARNING - different domain", start_domain, "→", final_domain)

    except Exception as error:                                                     #fängt Fehler innerhalb dieses try-Blocks ab und führt danach den nächsten Code aus
        print("Domain: FAIL - konnte nicht geprüft werden: ", error)


# --------------------------------------------------
# Status
# --------------------------------------------------
    try:
        if 200 <= response.status_code < 300:
            print("Status: PASS -", response.status_code)

        elif 300 <= response.status_code < 400:
            print("Status: REDIRECT", response.status_code)

        elif 400 <= response.status_code < 500:
            print("Status: FAIL - Client Fehler", response.status_code)

        elif 500 <= response.status_code < 600:
            print("Status: FAIL - Server Fehler", response.status_code)

        else:
            print("Status: Unbekannter Status", response.status_code)

    except Exception as error:
        print("Status: FAIL - konnte nicht geprüft werden: ", error)


# --------------------------------------------------
# Performance
# --------------------------------------------------
    try:
        response_time = round(end - start, 2)       #round(..., 2) rundet auf 2 Nachkommastellen

        if response_time < 2:
            print("Performance: PASS -", response_time, "Sekunden")

        elif response_time <= 3:
            print("Performance: WARNING -", response_time, "Sekunden")

        else:
            print("Performance: FAIL -", response_time, "Sekunden")

    except Exception as error:
        print("Performance: FAIL - konnte nicht geprüft werden: ", error)


# --------------------------------------------------
# Content Check
# --------------------------------------------------
    try:
        start_title = response.text.find("<title>")                 #speichert position nicht titel
        end_title = response.text.find("</title>")

        actual_title = response.text[start_title + 7:end_title]

        if expected_title.strip().lower() == actual_title.strip().lower():
            print("Title: PASS -", actual_title)
        else:
            print("Title: FAIL - erwartet:", expected_title, "| gefunden:", actual_title)

        if expected_text.strip().lower() in response.text.strip().lower():
            print("Content: PASS - erwarteter Text gefunden:", expected_text)
        else:
            print("Content: FAIL - erwarteter Text nicht gefunden:", expected_text)

    except Exception as error:
        print("Content Check: FAIL - konnte nicht geprüft werden:", error)


# --------------------------------------------------
# Broken Links
# --------------------------------------------------
    try:
        links = re.findall(r'href=["\'](.*?)["\']', response.text)          #re.findall(...) =Der durchsucht response.text nach Stellen wie:
                                                                                   #r'href=["\'](.*?)["\']' = sucht href-Attribute und liest den Inhalt zwischen den Anführungszeichen aus
        for link in links:
            if link.startswith("#"):
                continue

            if link.startswith("javascript:"):
                continue

            if link.startswith("mailto:"):
                continue

            if link == "":
                continue

            print("Link gefunden:", link)

    except Exception as error:
        print("Broken Links: FAIL - konnte Links nicht finden:", error)