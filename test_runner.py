import  requests                        #Requests zum Prüfen von Webseiten und APIs per HTTP-Anfragen,urls prüfen und Serverantworten auszulesen
import time
from urllib.parse import urlparse       #urlparse zum Zerlegen und Auslesen von Bestandteilen einer URL
from urllib.parse import urljoin        #setzt einen relativen Link mit der Ausgangs-URL zu einer vollständigen URL zusammen
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
        print("HTTP-Anfrage")
        print("  Timeout: Anfrage dauerte länger als 10 Sekunden", error)

    except requests.exceptions.TooManyRedirects as error:
        print("HTTP-Anfrage")
        print("  Redirect: FAIL - too many redirects", error)

    except requests.exceptions.SSLError as error:
        print("HTTP-Anfrage")
        print("  Request: FAIL - SSL/TLS certificate error", error)

    except requests.exceptions.RequestException as error:
        print("HTTP-Anfrage")
        print("  Website nicht erreichbar", error)


# --------------------------------------------------
# HTTPS
# --------------------------------------------------
    try:
        print()
        print("HTTPS Prüfung")

        if response.url.startswith("https://"):
            print("  HTTPS: PASS -", response.url)
        else:
            print("  HTTPS: FAIL", response.url)

    except Exception as error:
        print("HTTPS Prüfung")
        print("  HTTPS: FAIL - konnte nicht geprüft werden: ", error)


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

        print()
        print("SSL/TLS Prüfung")
        print("  SSL/TLS: PASS")

        expiration_date = certificate["notAfter"]                   #notAfter = Datum, bis zu dem das Zertifikat gültig ist
        expiration_date = datetime.strptime(expiration_date,"%b %d %H:%M:%S %Y %Z")     #wandelt den Text des Ablaufdatums in ein datetime-Objekt um

        current_date = datetime.now()

        if expiration_date > current_date:
            print("  Certificate: PASS - gültig bis:", expiration_date)
        else:
            print("  Certificate: FAIL - expired", expiration_date)

    except ssl.SSLCertVerificationError:        #fängt Zertifikatsfehler bei der direkten SSL/TLS-Verbindung mit socket ab
        print("SSL/TLS Prüfung")
        print("  SSL/TLS: FAIL - certificate error")

    except requests.exceptions.SSLError:        #fängt SSL/TLS-Fehler ab, die bei requests auftreten
        print("SSL/TLS Prüfung")
        print("  SSL/TLS: FAIL - certificate error")

    except ConnectionRefusedError as error:  # fängt Fehler ab, wenn der Server die Verbindung ablehnt
        print("SSL/TLS Prüfung")
        print("  SSL/TLS: FAIL - connection refused:", error)


# --------------------------------------------------
# Domain
# --------------------------------------------------
    try:
        final_url = urlparse(response.url)

        start_domain = parsed_url.hostname.removeprefix("www.")
        final_domain = final_url.hostname.removeprefix("www.")

        print()
        print("Domain Prüfung")

        if start_domain == final_domain:         #hostname gibt den Hostnamen der URL zurück
            print("  Domain: PASS -", start_domain, "→", final_domain)
        else:
            print("  Domain: WARNING - different domain", start_domain, "→", final_domain)

    except Exception as error:                                                     #fängt Fehler innerhalb dieses try-Blocks ab und führt danach den nächsten Code aus
        print("Domain Prüfung")
        print("  Domain: FAIL - konnte nicht geprüft werden: ", error)


# --------------------------------------------------
# Status
# --------------------------------------------------
    try:
        print()
        print("Status Prüfung")

        if 200 <= response.status_code < 300:
            print("  Status: PASS -", response.status_code)

        elif 300 <= response.status_code < 400:
            print("  Status: REDIRECT", response.status_code)

        elif 400 <= response.status_code < 500:
            print("  Status: FAIL - Client Fehler", response.status_code)

        elif 500 <= response.status_code < 600:
            print("  Status: FAIL - Server Fehler", response.status_code)

        else:
            print("  Status: Unbekannter Status", response.status_code)

    except Exception as error:
        print("Status Prüfung")
        print("  Status: FAIL - konnte nicht geprüft werden: ", error)


# --------------------------------------------------
# Performance
# --------------------------------------------------
    try:
        response_time = round(end - start, 2)       #round(..., 2) rundet auf 2 Nachkommastellen

        print()
        print("Performance Prüfung")

        if response_time < 2:
            print("  Ladezeit: PASS -", response_time, "Sekunden")

        elif response_time <= 3:
            print("  Ladezeit: WARNING -", response_time, "Sekunden")

        else:
            print("  Ladezeit: FAIL -", response_time, "Sekunden")

    except Exception as error:
        print("Performance Prüfung")
        print("  Ladezeit: FAIL - konnte nicht geprüft werden: ", error)


# --------------------------------------------------
# Content Check
# --------------------------------------------------
    try:
        start_title = response.text.find("<title>")                 #speichert position nicht titel
        end_title = response.text.find("</title>")

        actual_title = response.text[start_title + 7:end_title]

        print()
        print("Content Check Prüfung")

        if expected_title.strip().lower() == actual_title.strip().lower():
            print("  Title: PASS -", actual_title)
        else:
            print("  Title: FAIL - erwartet:", expected_title, "| gefunden:", actual_title)

        if expected_text.strip().lower() in response.text.strip().lower():
            print("  Content: PASS - erwarteter Text gefunden:", expected_text)
        else:
            print("  Content: FAIL - erwarteter Text nicht gefunden:", expected_text)

    except Exception as error:
        print("Content Check Prüfung")
        print("  Content Check: FAIL - konnte nicht geprüft werden:", error)


# --------------------------------------------------
# Broken Links
# --------------------------------------------------
    passed_links = []
    failed_links = []

    try:
        print()
        print("Broken Links Prüfung")
        links = re.findall(r'href=["\'](.*?)["\']', response.text)          #re.findall(...) =Der durchsucht response.text nach Stellen wie:
                                                                                   #r'href=["\'](.*?)["\']' = sucht href-Attribute und liest den Inhalt zwischen den Anführungszeichen aus
        if not links:
            print("  Keine Links gefunden")

        else:
            filtered_links = []

            for link in links:
                if link.startswith("#"):
                    continue

                if link.startswith("javascript:"):
                    continue

                if link.startswith("mailto:"):
                    continue

                if link == "":
                    continue

                full_url = urljoin(response.url, link)                          #setzt relative Links zur vollständigen URL zusammen

                if full_url not in filtered_links:
                    filtered_links.append(full_url)

            links = filtered_links                      #bereinigte Liste wird zur Prüfliste keine doppelten mehr
            for full_url in links:

                try:
                    link_response = requests.get(full_url, timeout=10)

                    if link_response.status_code < 400:
                        passed_links.append(full_url)
                    else:
                        failed_links.append(full_url)

                except requests.RequestException:
                    failed_links.append(full_url)

                #fortschrittszeile
                print(f"\rBroken Links: Prüfe Links... {len(passed_links) + len(failed_links)}/{len(links)}", end="")       #\r= innerhalb der aktuellen Zeile wieder an den Anfang
                                                                                                                            #end ="" = kein zeilenburch, der Cursor in derselben Zeile
            #Zeilenumbruch nach der Fortschrittsanzeige
            print()

            print(f"  Broken Links: {len(passed_links)} PASS - {len(failed_links)} FAIL")

            for link in failed_links:
                print("FAIL:", link)

    except Exception as error:
        print("Broken Links Prüfung")
        print(" Broken Links: FAIL - konnte Links nicht finden:", error)


# --------------------------------------------------
# Bilder / Dateien
# --------------------------------------------------
    passed_images = []
    failed_images = []

    try:
        print()
        print("Bilder / Dateien Prüfung")
        images = re.findall(r'<img[^>]+src=["\'](.*?)["\']', response.text)

        if not images:
            print("  Keine Bilder gefunden")

        else:
            filtered_images = []

            for image in images:

                full_url = urljoin(response.url, image)

                if full_url not in filtered_images:
                    filtered_images.append(full_url)

            images = filtered_images

            for full_url in images:

                try:
                    image_response = requests.get(full_url, timeout=10)

                    content_type = image_response.headers.get("Content-Type", "")        #.headers = enthält Zusatzinformationen zur HTTP-Antwort = Content-Type: image/png

                    if image_response.status_code < 400 and content_type.startswith("image/"):
                        passed_images.append(full_url)
                    else:
                        failed_images.append(full_url)

                except requests.RequestException:
                    failed_images.append(full_url)


                print(f"\rBilder: Prüfe Bilder... {len(passed_images) + len(failed_images)}/{len(images)}", end="")

            print()

            print(f"  Bilder: {len(passed_images)} PASS - {len(failed_images)} FAIL")

            for image in failed_images:
                print("  FAIL:", image)

    except Exception as error:
        print("Bilder / Dateien Prüfung")
        print("  Bilder: FAIL - konnte Bilder nicht prüfen:", error)


# --------------------------------------------------
# HTML-Struktur
# --------------------------------------------------
    print()
    print("HTML-Struktur Prüfung")

    #Sprachprüfung
    try:
        lang_names = {"de": "Deutsch","en": "Englisch","fr": "Französisch","es": "Spanisch","it": "Italienisch"}

        lang = re.search(r'<html[^>]*lang=["\'](.*?)["\']', response.text, re.IGNORECASE)           #re.search = sucht nach dem ersten passenden Treffer

        print("  Sprache:")
        if lang:
            language_code = lang.group(1).lower()
            language_name = lang_names.get(language_code, "Unbekannte Sprache")

            print(f"    Lang: PASS - {language_code} = {language_name}")
        else:
            print("    Lang: FAIL - kein Sprachattribut gefunden")

    except Exception as error:
        print("HTML-Struktur Sprachprüfung")
        print("  HTML/Struktur: FAIL - konnte nicht prüfen:", error)


    #Grundstruktur <head>,<body>
    try:
        head = re.search(r"<head\b[^>]*>", response.text, re.IGNORECASE)        #\b = Wortgrenze, damit nur das Tag "head" bzw. "body" erkannt wird
        body = re.search(r"<body\b[^>]*>", response.text, re.IGNORECASE)

        print()
        print("Grundstruktur:")

        if head:
            print("  HEAD: PASS - vorhanden")
        else:
            print("  HEAD: FAIL - nicht vorhanden")

        if body:
            print("  BODY: PASS - vorhanden")
        else:
            print("  BODY: FAIL - nicht vorhanden")

    except Exception as error:
        print("Grundstruktur Prüfung")
        print("  Grundstruktur: FAIL - konnte nicht geprüft werden:", error)


    #Überschriften H1 check
    try:
        headings = re.findall(r"<(h[1-6])[^>]*>(.*?)</\1>",response.text,re.IGNORECASE | re.DOTALL) #re.IGNORECASE = Ignoriert Groß-/Kleinschreibung
                                                                                                           #re.DOTALL =sorgt dafür dass . auch Zeilenumbrüche erfasst
        headings_by_level = {"h1": [],"h2": [],"h3": [],"h4": [],"h5": [],"h6": []}

        for level, text in headings:
            if text not in headings_by_level[level]:
                headings_by_level[level].append(text)

        print()
        print("Überschriften:")
        if not headings_by_level["h1"]:
            print("  H1: FAIL - keine H1 gefunden")
        else:
            print(f"  H1: PASS - {len(headings_by_level['h1'])} gefunden")

        for level in ["h2", "h3", "h4", "h5", "h6"]:
            print(f"    {level.upper()}: INFO - {len(headings_by_level[level])} gefunden")

    except Exception as error:
        print("HTML-Struktur Überschrift Prüfung")
        print("  HTML/Struktur: FAIL - konnte nicht prüfen:", error)


    #Meta Informationen
    #Charset prüfen --> damit Zeichen korrekt interpretiert werden
    try:
        charset = re.search(r'<meta[^>]*charset=["\']?(.*?)["\']?[^>]*>', response.text, re.IGNORECASE)

        print()
        print("Meta-Informationen Prüfung")
        print("  Charset:")

        if charset:
            charset_value = charset.group(1).lower()
            print(f"    Charset: PASS - {charset_value}")
        else:
            print("    Charset: FAIL - nicht vorhanden")

    except Exception as error:
        print("Meta-Informationen Prüfung")
        print("  Meta-Informationen Charset: FAIL - konnte nicht geprüft werden:", error)

