import  requests                        #Requests zum Prüfen von Webseiten und APIs per HTTP-Anfragen,urls prüfen und Serverantworten auszulesen
import time
from urllib.parse import urlparse       #urlparse zum Zerlegen und Auslesen von Bestandteilen einer URL
from urllib.parse import urljoin        #setzt einen relativen Link mit der Ausgangs-URL zu einer vollständigen URL zusammen
import ssl                              #SSL/TLS = Transport Layer Security, sorgt für verschlüsselte Verbindungen und Zertifikatsprüfung
import socket                           #für eine direkte Netzwerkverbindung zum Server
from datetime import datetime           #datetime zum Erstellen, Umwandeln und Vergleichen von Datum und Uhrzeit
import re                               #Regular Expressions= Suchmuster für Text
from playwright.sync_api import sync_playwright     #playwright für Browser-Automatisierung und Browser-Tests     #sync_playwright() startet die Schnittstelle, über die Python den Browser steuern kann
from playwright.sync_api import expect              #expect zum Prüfen, ob ein erwarteter Zustand eingetreten ist(speziell für Browser-Elemente und Browser-Zustände)


# --------------------------------------------------
# HTML-Testreport erstellen
# --------------------------------------------------
def create_report(report_file, test_start, url, report_results):
    #strf = string format
    # %d → Tag %m → Monat %Y → Jahr
    # %H → Stunde %M → Minute %S → Sekunde

    html = f"""<!DOCTYPE html>
<html lang="de">

<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="2">
    <title>QA Automation Test Report</title>
</head>

<body>

    <h1>QA Automation Test Report</h1>
    <p style="text-align: right; font-size: 12px;">
        Hinweis: Genauere Fehlerdetails werden in der Konsole angezeigt.
    </p>

    <h2>Testinformationen</h2>
    
    <h3>Anfrage QA-Test:</h3>
                                                                
    <p>Datum: {test_start.strftime("%d.%m.%Y")}</p>             
    <p>Uhrzeit: {test_start.strftime("%H:%M:%S")}</p>      
    <p>URL: {url}</p>     
    
    {''.join(report_results)}

</body>

</html>
"""

    #Neuen HTML-Report mit den Testergebnissen schreiben
    with open(report_file, "w", encoding="utf-8") as file:
        file.write(html)

# --------------------------------------------------
# Zeitabfrage / Teststart
# --------------------------------------------------
def run_test(url, expected_title, expected_text):
    test_start = datetime.now()

    print(f"Datum: {test_start.strftime('%d.%m.%Y')}")
    print(f"Uhrzeit: {test_start.strftime('%H:%M:%S')}")
    print()
    print("URL:", url)

    report_file = "qa_test_report.html"
    report_results = []

# --------------------------------------------------
# HTTP-Anfrage
# --------------------------------------------------
    try:
        start = time.time()
        response = requests.get(url, timeout=10)
        end = time.time()

        status_code = response.status_code

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
            https_result = f"HTTPS: PASS {response.url}"

        else:
            print("  HTTPS: FAIL", response.url)
            https_result = f"HTTPS: FAIL {response.url}"

        report_results.append(f"""
        <h3>HTTPS Prüfung</h3>
        <p>&nbsp;&nbsp;&nbsp;&nbsp;{https_result}</p>
        """)

        create_report(report_file, test_start, url, report_results)

    except Exception as error:
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
            ssl_result = f"""
            <p>SSL/TLS: PASS</p>
            <p>Certificate: PASS - gültig bis: {expiration_date}</p>
            """
        else:
            print("  Certificate: FAIL - expired", expiration_date)
            ssl_result = f"""
            <p>SSL/TLS: PASS</p>
            <p>Certificate: FAIL - expired {expiration_date}</p>
            """

    except ssl.SSLCertVerificationError:        #fängt Zertifikatsfehler bei der direkten SSL/TLS-Verbindung mit socket ab
        print("SSL/TLS Prüfung")
        print("  SSL/TLS: FAIL - certificate error")
        ssl_result = "<p>SSL/TLS: FAIL - certificate error</p>"

    except requests.exceptions.SSLError:        #fängt SSL/TLS-Fehler ab, die bei requests auftreten
        print("SSL/TLS Prüfung")
        print("  SSL/TLS: FAIL - certificate error")
        ssl_result = "<p>SSL/TLS: FAIL - certificate error</p>"

    except ConnectionRefusedError as error:  # fängt Fehler ab, wenn der Server die Verbindung ablehnt
        print("SSL/TLS Prüfung")
        print("  SSL/TLS: FAIL - connection refused:", error)
        ssl_result = "<p>SSL/TLS: FAIL - connection refused</p>"

    report_results.append(f"""
    <h3>SSL/TLS Prüfung</h3>
    <p>{ssl_result}</p>
    """)

    create_report(report_file, test_start, url, report_results)

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
            domain_result = f"Domain: PASS - {start_domain} → {final_domain}"
        else:
            print("  Domain: WARNING - different domain", start_domain, "→", final_domain)
            domain_result = f"Domain: WARNING - different domain {start_domain} → {final_domain}"

    except Exception as error:                                                     #fängt Fehler innerhalb dieses try-Blocks ab und führt danach den nächsten Code aus
        print("  Domain: FAIL - konnte nicht geprüft werden: ", error)
        domain_result = "Domain: FAIL - konnte nicht geprüft werden"

    report_results.append(f"""
    <h3>Domain Prüfung</h3>
    <p>&nbsp;&nbsp;&nbsp;&nbsp;{domain_result}</p>
    """)

    create_report(report_file, test_start, url, report_results)

# --------------------------------------------------
# Status
# --------------------------------------------------
    try:
        print()
        print("Status Prüfung")

        if 200 <= response.status_code < 300:
            print("  Status: PASS -", response.status_code)
            status_result = f"Status: PASS - {response.status_code}"

        elif 300 <= response.status_code < 400:
            print("  Status: REDIRECT", response.status_code)
            status_result = f"Status: REDIRECT {response.status_code}"

        elif 400 <= response.status_code < 500:
            print("  Status: FAIL - Client Fehler", response.status_code)
            status_result = f"Status: FAIL - Client Fehler {response.status_code}"

        elif 500 <= response.status_code < 600:
            print("  Status: FAIL - Server Fehler", response.status_code)
            status_result = f"Status: FAIL - Server Fehler {response.status_code}"

        else:
            print("  Status: Unbekannter Status", response.status_code)
            status_result = f"Status: Unbekannter Status {response.status_code}"

    except Exception as error:
        print("  Status: FAIL - konnte nicht geprüft werden: ", error)
        status_result = "Status: FAIL - konnte nicht geprüft werden"

    report_results.append(f"""
    <h3>Status Prüfung</h3>
    <p>&nbsp;&nbsp;&nbsp;&nbsp;{status_result}</p>
    """)

    create_report(report_file, test_start, url, report_results)


# --------------------------------------------------
# Performance
# --------------------------------------------------
    try:
        response_time = round(end - start, 2)       #round(..., 2) rundet auf 2 Nachkommastellen

        print()
        print("Performance Prüfung")

        if response_time < 2:
            print("  Ladezeit: PASS -", response_time, "Sekunden")
            performance_result = f"Ladezeit: PASS - {response_time} Sekunden"

        elif response_time <= 3:
            print("  Ladezeit: WARNING -", response_time, "Sekunden")
            performance_result = f"Ladezeit: WARNING - {response_time} Sekunden"

        else:
            print("  Ladezeit: FAIL -", response_time, "Sekunden")
            performance_result = f"Ladezeit: FAIL - {response_time} Sekunden"

    except Exception as error:
        print("  Ladezeit: FAIL - konnte nicht geprüft werden: ", error)
        performance_result = "Ladezeit: FAIL - konnte nicht geprüft werden"

    report_results.append(f"""
    <h3>Performance Prüfung</h3>
    <p>&nbsp;&nbsp;&nbsp;&nbsp;{performance_result}</p>
    """)

    create_report(report_file, test_start, url, report_results)

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
            title_result = f"Title: PASS - {actual_title}"
        else:
            print("  Title: FAIL - erwartet:", expected_title, "| gefunden:", actual_title)
            title_result = f"Title: FAIL - erwartet: {expected_title} | gefunden: {actual_title}"

        if expected_text.strip().lower() in response.text.strip().lower():
            print("  Content: PASS - erwarteter Text gefunden:", expected_text)
            content_result = f"Content: PASS - erwarteter Text gefunden: {expected_text}"
        else:
            print("  Content: FAIL - erwarteter Text nicht gefunden:", expected_text)
            content_result = f"Content: FAIL - erwarteter Text nicht gefunden: {expected_text}"

    except Exception as error:
        print("  Content Check: FAIL - konnte nicht geprüft werden:", error)
        title_result = "Title: FAIL - konnte nicht geprüft werden"
        content_result = "Content: FAIL - konnte nicht geprüft werden"

    report_results.append(f"""
    <h3>Content Check Prüfung</h3>
    <p>&nbsp;&nbsp;&nbsp;&nbsp;{title_result}</p>
    <p>&nbsp;&nbsp;&nbsp;&nbsp;{content_result}</p>
    """)

    create_report(report_file, test_start, url, report_results)

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

        #sucht JavaScript-Navigationen über window.location.href und fügt die gefundenen Zielseiten zur Linkliste hinzu, z. B. beim Test von Button 4
        onclick_links = re.findall(r'window\.location\.href\s*=\s*["\'](.*?)["\']',response.text)
        links.extend(onclick_links)

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
            broken_links_result = (
                f"Broken Links: {len(passed_links)} PASS - "
                f"{len(failed_links)} FAIL<br>"
            )

            for link in failed_links:
                print("FAIL:", link)

    except Exception as error:
        print(" Broken Links: FAIL - konnte Links nicht finden:", error)
        broken_links_result = "Broken Links: FAIL - konnte Links nicht finden"

    report_results.append(f"""
    <h3>Broken Links Prüfung</h3>
    <p>&nbsp;&nbsp;&nbsp;&nbsp;{broken_links_result}</p>
    """)

    create_report(report_file, test_start, url, report_results)

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
            images_result = "Bilder: Keine Bilder gefunden"

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
            images_result = (
                f"Bilder: {len(passed_images)} PASS - "
                f"{len(failed_images)} FAIL<br>"
            )

            for image in failed_images:
                print("  FAIL:", image)

    except Exception as error:
        print("  Bilder: FAIL - konnte Bilder nicht prüfen:", error)
        images_result = "Bilder: FAIL - konnte Bilder nicht prüfen"

    report_results.append(f"""
    <h3>Bilder / Dateien Prüfung</h3>
    <p>&nbsp;&nbsp;&nbsp;&nbsp;{images_result}</p>
    """)

    create_report(report_file, test_start, url, report_results)

# --------------------------------------------------
# HTML-Struktur
# --------------------------------------------------
    print()
    print("HTML-Struktur Prüfung")

    html_structure_result = """
    <h3>HTML-Struktur Prüfung</h3>
    """

    #Sprachprüfung
    try:
        lang_names = {"de": "Deutsch","en": "Englisch","fr": "Französisch","es": "Spanisch","it": "Italienisch"}

        lang = re.search(r'<html[^>]*lang=["\'](.*?)["\']', response.text, re.IGNORECASE)           #re.search = sucht nach dem ersten passenden Treffer

        print("  Sprache:")
        if lang:
            language_code = lang.group(1).lower()
            language_name = lang_names.get(language_code, "Unbekannte Sprache")
            print(f"    Lang: PASS - {language_code} = {language_name}")
            language_result = f"Lang: PASS - {language_code} = {language_name}"

        else:
            print("    Lang: FAIL - kein Sprachattribut gefunden")
            language_result = "Lang: FAIL - kein Sprachattribut gefunden"

    except Exception as error:
        print("  HTML/Struktur: FAIL - konnte nicht prüfen:", error)
        language_result = "Lang: FAIL - konnte nicht geprüft werden"

    # &nbsp = 1 Leerzeichen in html
    html_structure_result += f"""
    <h4>Sprache:</h4>
    <p>&nbsp;&nbsp;&nbsp;&nbsp;{language_result}</p>                            
    """

    report_results.append(html_structure_result)
    create_report(report_file, test_start, url, report_results)

    #Grundstruktur <head>,<body>
    try:
        head = re.search(r"<head\b[^>]*>", response.text, re.IGNORECASE)        #\b = Wortgrenze, damit nur das Tag "head" bzw. "body" erkannt wird
        body = re.search(r"<body\b[^>]*>", response.text, re.IGNORECASE)

        print()
        print("Grundstruktur:")

        if head:
            print("  HEAD: PASS - vorhanden")
            head_result = "HEAD: PASS - vorhanden"
        else:
            print("  HEAD: FAIL - nicht vorhanden")
            head_result = "HEAD: FAIL - nicht vorhanden"

        if body:
            print("  BODY: PASS - vorhanden")
            body_result = "BODY: PASS - vorhanden"
        else:
            print("  BODY: FAIL - nicht vorhanden")
            body_result = "BODY: FAIL - nicht vorhanden"

    except Exception as error:
        print("  Grundstruktur: FAIL - konnte nicht geprüft werden:", error)
        head_result = "HEAD: FAIL - konnte nicht geprüft werden"
        body_result = "BODY: FAIL - konnte nicht geprüft werden"

    html_structure_result += f"""
    <h4>Grundstruktur:</h4>
    <p>&nbsp;&nbsp;&nbsp;&nbsp;{head_result}</p>
    <p>&nbsp;&nbsp;&nbsp;&nbsp;{body_result}</p>
    """

    report_results[-1] = html_structure_result
    create_report(report_file, test_start, url, report_results)

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
            h1_result = "H1: FAIL - keine H1 gefunden"
        else:
            print(f"  H1: PASS - {len(headings_by_level['h1'])} gefunden")
            h1_result = f"H1: PASS - {len(headings_by_level['h1'])} gefunden"

        for level in ["h2", "h3", "h4", "h5", "h6"]:
            print(f"    {level.upper()}: INFO - {len(headings_by_level[level])} gefunden")

    except Exception as error:
        print("  HTML/Struktur: FAIL - konnte nicht prüfen:", error)
        h1_result = "H1: FAIL - konnte nicht geprüft werden"

    html_structure_result += f"""
    <h4>Überschriften:</h4>
    <p>&nbsp;&nbsp;&nbsp;&nbsp;{h1_result}</p>
    """

    for level in ["h2", "h3", "h4", "h5", "h6"]:
        html_structure_result += f"""
        <p>&nbsp;&nbsp;&nbsp;&nbsp;{level.upper()}: INFO - {len(headings_by_level[level])} gefunden</p>
        """

    report_results[-1] = html_structure_result
    create_report(report_file, test_start, url, report_results)


    #Meta Informationen
    #Charset prüfen --> damit Zeichen korrekt interpretiert werden
    try:
        charset = re.search(r'<meta[^>]*charset=["\']?([^"\'>\s]+)',response.text,re.IGNORECASE)    #[^"\'>\s]+ = mindestens ein Zeichen als Wert, dadurch wird der Wert zuverlässig ausgelesen

        print()
        print("Meta-Informationen Prüfung")
        print("  Charset:")

        if charset:
            charset_value = charset.group(1).lower()
            print(f"    Charset: PASS - {charset_value}")
            charset_result = f"Charset: PASS - {charset_value}"
        else:
            print("    Charset: FAIL - nicht vorhanden")
            charset_result = "Charset: FAIL - nicht vorhanden"

    except Exception as error:
        print("  Meta-Informationen Charset: FAIL - konnte nicht geprüft werden:", error)
        charset_result = "Charset: FAIL - konnte nicht geprüft werden"

    html_structure_result += f"""
    <h3>Meta-Informationen Prüfung</h3>
    <h4>Charset:</h4>
    <p>&nbsp;&nbsp;&nbsp;&nbsp;{charset_result}</p>
    """

    report_results[-1] = html_structure_result
    create_report(report_file, test_start, url, report_results)

    #viewport prüfen --> für vernünftige Darstellung auf mobilen Geräten
    try:
        viewport = re.search(r'<meta[^>]*name=["\']viewport["\'][^>]*content=["\'](.*?)["\']',response.text,re.IGNORECASE)

        print()
        print("  Viewport:")

        if viewport:
            viewport_value = viewport.group(1).lower()
            print(f"    Viewport: PASS - {viewport_value}")
            viewport_result = f"Viewport: PASS - {viewport_value}"

            if "width=device-width" in viewport_value:              #device-width= Behandle die Breite der Webseite so, als wäre sie so breit wie das Gerät
                print(f"    Mobile Darstellung: PASS - width=device-width")
                mobile_result = "Mobile Darstellung: PASS - width=device-width"
            else:
                print(f"    Mobile Darstellung: FAIL - width=device-width fehlt - {viewport_value}")
                mobile_result = f"Mobile Darstellung: FAIL - width=device-width fehlt - {viewport_value}"

        else:
            print("    Viewport: FAIL - nicht vorhanden")
            mobile_result = "Mobile Darstellung: FAIL - Viewport nicht vorhanden"

    except Exception as error:
        print("  Meta-Informationen Viewport: FAIL - konnte nicht geprüft werden:", error)
        viewport_result = "Viewport: FAIL - konnte nicht geprüft werden"
        mobile_result = "Mobile Darstellung: FAIL - konnte nicht geprüft werden"

    html_structure_result += f"""
    <h4>Viewport:</h4>
    <p>&nbsp;&nbsp;&nbsp;&nbsp;{viewport_result}</p>
    <p>&nbsp;&nbsp;&nbsp;&nbsp;{mobile_result}</p>
    """

    report_results[-1] = html_structure_result
    create_report(report_file, test_start, url, report_results)

    #description = Beschreibung der Seite für Suchmaschinen
    try:
        description = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']',response.text,re.IGNORECASE)

        print()
        print("  Description:")

        if description:
            description_value = description.group(1).strip()

            if description_value:
                print(f"    Description: PASS - {description_value}")
                description_result = f"Description: PASS - {description_value}"
            else:
                print("    Description: FAIL - Beschreibung ist leer")
                description_result = "Description: FAIL - Beschreibung ist leer"

        else:
            print("    Description: FAIL - nicht vorhanden")
            description_result = "Description: FAIL - nicht vorhanden"

    except Exception as error:
        print("  Meta-Informationen description: FAIL - konnte nicht geprüft werden:", error)
        description_result = "Description: FAIL - konnte nicht geprüft werden"

    html_structure_result += f"""
    <h4>Description:</h4>
    <p>&nbsp;&nbsp;&nbsp;&nbsp;{description_result}</p>
    """

    report_results[-1] = html_structure_result
    create_report(report_file, test_start, url, report_results)


    #robots = Anweisungen für Suchmaschinen-Crawler
    try:
        robots = re.search(r'<meta[^>]*name=["\']robots["\'][^>]*content=["\'](.*?)["\']',response.text,re.IGNORECASE)

        print()
        print("  Robots:")

        if robots:
            robots_value = robots.group(1).strip()

            if robots_value:
                print(f"    Robots: PASS - {robots_value}")
                robots_result = f"Robots: PASS - {robots_value}"
            else:
                print("     Robots: FAIL - Wert ist leer")
                robots_result = "Robots: FAIL - Wert ist leer"

        else:
            print("    Robots: FAIL - nicht vorhanden")
            robots_result = "Robots: FAIL - nicht vorhanden"

    except Exception as error:
        print("  Meta-Informationen robots: FAIL - konnte nicht geprüft werden:", error)
        robots_result = "Robots: FAIL - konnte nicht geprüft werden"

    html_structure_result += f"""
    <h4>Robots:</h4>
    <p>&nbsp;&nbsp;&nbsp;&nbsp;{robots_result}</p>
    """

    report_results[-1] = html_structure_result
    create_report(report_file, test_start, url, report_results)

    #og:title, og:image = Social-Media-Vorschauen
    #author = Angabe des Autors sinvolle info ?

# --------------------------------------------------
# Browser Tests
# --------------------------------------------------
#normale Buttons
    #gefundene Formulare/Eingabefelder speichern
    found_forms = []

    #gefundene Formulare auswählbare Felder speichern
    option_forms = []

    #Buttons klicken
    print()
    print("Browser Tests")

    browser_test_result = """
    <h3>Browser Tests</h3>
    """

    #gsesamtstatistik buttons
    all_button_results = {}

    passed_buttons = []
    failed_buttons = []

    # Interaktive DOM Elemente Starterseite
    interactive_elements = []
    passed_interactive_elements = []
    failed_interactive_elements = []

    try:
        with (sync_playwright() as p):
            browser = p.chromium.launch()               #startet einen Chromium-Browser über Python
            page = browser.new_page()                   #page= eine einzelne Browserseite bzw ein tap
            page.goto(url)                              # öffnet die geladene URL im automatisierten Browser
            dom_interactive_count = 0                   #feste DOM-Referenz für den gesamten Browser-Test

            # -------------------------------------------------------------------
            #Formular der Startseite erkennen und speichern
            inputs = page.locator("input, textarea")

            if inputs.count() > 0:
                form_data = {"url": page.url, "button": None, "input_count": inputs.count()}

                if form_data not in found_forms:
                    found_forms.append(form_data)

            #Auswahlbare Felder nach dem Button-Klick erkennen und speichern
            radio_fields = page.locator('input[type="radio"]')       #Radio-Felder = runde Auswahlfelder, meist nur eine Option gleichzeitig auswählbar
            select_fields = page.locator("select")                   #Select-Felder = Dropdown-Auswahl mit mehreren Optionen
            if radio_fields.count() > 0 or select_fields.count() > 0:
                option_data = {"url": page.url,"button": None,"radio_count": radio_fields.count(),"select_count": select_fields.count(),"source": "button"}

                if option_data not in option_forms:
                    option_forms.append(option_data)
            # -------------------------------------------------------------------

            #beginn des tests
            print("Button test sichtbar:")

            # Button-Namen einmal aus der Startseite sammeln
            buttons = page.locator("button")            #.locator() = suche Elemente auf dieser Seite
            filtered_buttons = []

            #nur sichtbare Buttons für den Test
            for index, button in enumerate(buttons.all()):              #enumerate = gibt jedem gefundenen Button eine Nummer für die eindeutige Erkennung (z.B.wird aus menu --> 1. Menü)
                if not button.is_visible():
                    continue

                button_name = button.inner_text().strip()

                if not button_name:
                    button_name = button.get_attribute("aria-label")

                if button_name:
                    filtered_buttons.append((index, button_name))

            #damit es auch bei 0 anzeigt
            print(f"Prüfe sichtbar Buttons... "f"0/{len(filtered_buttons)}",end="")

            #buttons einzeln testen
            for button_index, button_name in filtered_buttons:
                try:
                    page.goto(url)

                    buttons = page.locator("button")
                    current_button = None

                    #liest den sichtbaren Text des aktuellen Buttons aus
                    all_buttons = buttons.all()

                    if button_index >= len(all_buttons):
                        raise Exception("Button nicht gefunden")

                    current_button = all_buttons[button_index]

                    current_name = current_button.inner_text().strip()

                    if not current_name:
                        current_name = current_button.get_attribute("aria-label")        #Falls kein Text vorhanden ist aria-label-Attribut auslesen

                    if current_name != button_name:
                        raise Exception("Button nicht gefunden")                    #raise löst absichtlich einen Fehler aus und übergibt ihn an den passenden except-Block

                    #Wenn der Button nicht sichtbar ist versuchen ein sichtbares Menü zu öffnen
                    if not current_button.is_visible():
                        menu_button = page.get_by_role("button",name=re.compile(r"menü|menu|navigation",re.IGNORECASE))  #sucht nach einem Button mit der Rolle "button" dessen Name Menü, Menu oder Navigation enthält

                        #nur wenn ein passender sichtbarer menü-Button vorhanden ist
                        if menu_button.count() > 0 and menu_button.first.is_visible():
                            menu_button.first.click(timeout=3000,force=True)

                            #button nach dem Öffnen des Menüs erneut suchen
                            buttons = page.locator("button")
                            current_button = None

                            all_buttons = buttons.all()

                            if button_index < len(all_buttons):
                                current_button = all_buttons[button_index]

                                current_name = current_button.inner_text().strip()

                                if not current_name:
                                    current_name = current_button.get_attribute("aria-label")

                                if current_name != button_name:
                                    current_button = None

                    #prüfen, ob der Button sichtbar ist
                    if current_button is None:
                        raise Exception("Button nach Menüöffnung nicht gefunden")

                    if not current_button.is_visible():
                        raise Exception("Button nicht sichtbar")        #raise löst absichtlich einen Fehler aus und übergibt ihn an den passenden except-Block

                    #Button klicken
                    current_button.scroll_into_view_if_needed()  # ausschließen das die Positionierung/der Scrollzustand das Problem verursacht
                    current_button.click(timeout=3000, force=True)          #force=true= button wird auch dann geklickt, wenn ein anderes Element die Klickposition überlagert
                    page.wait_for_timeout(500)

                    # -------------------------------------------------------------------
                    #Formular nach Klick auf normalen Button erkennen und speichern
                    inputs = page.locator("input, textarea")

                    if inputs.count() > 0:
                        form_data = {"url": page.url,"button": button_name,"input_count": inputs.count(),"source": "button"}
                        found_forms.append(form_data)

                    #Auswahlbare Felder nach dem Button-Klick erkennen und speichern
                    radio_fields = page.locator('input[type="radio"]')
                    select_fields = page.locator("select")

                    if radio_fields.count() > 0 or select_fields.count() > 0:
                        option_data = {"url": page.url, "button": button_name, "radio_count": radio_fields.count(),"select_count": select_fields.count(), "source": "button"}

                        if option_data not in option_forms:
                            option_forms.append(option_data)
                    # -------------------------------------------------------------------

                    #neue interaktive Elemente nach dem Button-Klick suchen
                    elements = page.locator('a, [role="button"]:not(button), [aria-expanded]:not(button)')

                    for element in elements.all():

                        if not element.is_visible():
                            continue

                        tag_name = element.evaluate("(element) => element.tagName.toLowerCase()")
                        element_name = element.inner_text().strip()

                        if not element_name:
                            element_name = element.get_attribute("aria-label")

                        if not element_name:
                            continue

                        role = element.get_attribute("role")
                        aria_expanded = element.get_attribute("aria-expanded")
                        interactive_element = (tag_name,element_name,role,aria_expanded)

                        if interactive_element not in interactive_elements:
                            interactive_elements.append(interactive_element)
                            dom_interactive_count += 1

                    passed_buttons.append(button_name)

                except Exception as error:
                    failed_buttons.append((button_name, str(error)))

                #zurück zur startseite
                try:
                    page.goto(url)              #nach jedem Button zurück zur Startseite, wichtig wegen gleicher Bedingungen

                except Exception as nav_error:
                    print(f"      Navigation zurück fehlgeschlagen: {nav_error}")

                print(f"\rButtons: Prüfe Buttons... "f"{len(passed_buttons) + len(failed_buttons)}/{len(filtered_buttons)}",end="")

            print()
            print(f"  Buttons: {len(passed_buttons)} PASS - "f"{len(failed_buttons)} FAIL")

            for button, error in failed_buttons:
                print(f"    FAIL: {button} - {error}")

            buttons_result = (
                f"Buttons: {len(passed_buttons)} PASS - "
                f"{len(failed_buttons)} FAIL"
            )

            browser_test_result += f"""
            <h4>Button test sichtbar:</h4>
            <p>&nbsp;&nbsp;&nbsp;&nbsp;{buttons_result}</p>
            """

            report_results.append(browser_test_result)
            create_report(report_file, test_start, url, report_results)

            #damit sie nicht nochmal als aufklappbare Buttons getestet werden
            visible_button_names = {name for index, name in filtered_buttons}


#aufklappbare Buttons
            expandable_buttons = []
            passed_expandable_buttons = []
            failed_expandable_buttons = []

            new_buttons = []
            passed_new_buttons = []
            failed_new_buttons = []

            #aufklappbare Buttons erkennen
            try:
                print()
                print("Aufklappbare Buttons:")

                buttons = page.locator('button[aria-expanded]')

                for index, button in enumerate(buttons.all()):
                    button_name = button.inner_text().strip()

                    if not button_name:
                        button_name = button.get_attribute("aria-label")

                    if button_name and button_name not in expandable_buttons:
                        expandable_buttons.append(button_name)

                #2 test fals website aufklappbare buttons kein aria label haben
                #zusätzliche Elternbuttons erkennen, die neue Buttons erst nach dem Klick anzeigen
                for button_index, button_name in filtered_buttons:

                    #bereits als aufklappbaren Button erkannt?
                    if button_name in expandable_buttons:
                        continue

                    try:
                        page.goto(url)

                        buttons = page.locator("button")
                        current_button = None

                        for button in buttons.all():

                            current_name = button.inner_text().strip()

                            if not current_name:
                                current_name = button.get_attribute("aria-label")

                            if current_name == button_name:
                                current_button = button
                                break

                        if current_button is None:
                            continue

                        #vorher sichtbare Buttons merken
                        before_buttons = set()

                        for button in page.locator("button:visible").all():

                            name = button.inner_text().strip()

                            if not name:
                                name = button.get_attribute("aria-label")

                            if name:
                                before_buttons.add(name)

                        #elternbutton klicken
                        current_button.click(timeout=3000, force=True)
                        page.wait_for_timeout(1000)

                        #neue Buttons nach dem Klick suchen
                        for sub_button in page.locator("button:visible").all():

                            sub_name = sub_button.inner_text().strip()

                            if not sub_name:
                                sub_name = sub_button.get_attribute("aria-label")

                            if not sub_name:
                                continue

                            if sub_name in before_buttons:
                                continue

                            new_button = (button_name, sub_name)

                            if new_button not in new_buttons:
                                new_buttons.append(new_button)

                        if any(parent == button_name for parent, child in new_buttons):
                            expandable_buttons.append(button_name)

                    except Exception:
                        continue

                print(f"Prüfe Aufklappbare Buttons... "f"0/{len(expandable_buttons)}",end="")

            except Exception as error:
                print("  Aufklappbare Buttons: "f"FAIL - konnte nicht erkannt werden: {error}")


            #aufklappbare Buttons einzeln testen
            try:
                new_buttons = []
                page.goto(url)
                for button_name in expandable_buttons:

                    try:
                        buttons = page.locator("button:visible")
                        current_button = None

                        # aufklappbaren Button wiederfinden
                        for button in buttons.all():
                            current_name = button.inner_text().strip()

                            if not current_name:
                                current_name = button.get_attribute("aria-label")

                            if current_name == button_name:
                                current_button = button
                                break

                        if current_button is None:
                            raise Exception("Aufklappbarer Button nicht gefunden")

                        if not current_button.is_visible():
                            raise Exception("Aufklappbarer Button nicht sichtbar")

                        #sichtbare Buttons vor dem Aufklappen merken
                        before_buttons = set()

                        for button in page.locator("button").all():

                            if not button.is_visible():
                                continue

                            name = button.inner_text().strip()

                            if not name:
                                name = button.get_attribute("aria-label")

                            if name:
                                before_buttons.add(name)

                        #clicken button zuerst
                        current_button.click(timeout=3000, force=True)
                        passed_expandable_buttons.append(button_name)
                        #kurz warten, bis das Menü geöffnet wurde
                        page.wait_for_timeout(1000)

                        #-------------------------------------------------------------------
                        #Formular nach dem Öffnen eines aufklappbaren Buttons erkennen und speichern
                        inputs = page.locator("input, textarea")

                        if inputs.count() > 0:
                            form_data = {"url": page.url, "input_count": inputs.count(), "source": "button"}

                            if form_data not in found_forms:
                                found_forms.append(form_data)

                        #Auswahlbare Felder nach dem Button-Klick erkennen und speichern
                        radio_fields = page.locator('input[type="radio"]')
                        select_fields = page.locator("select")

                        if radio_fields.count() > 0 or select_fields.count() > 0:
                            option_data = {"url": page.url, "button": button_name,"radio_count": radio_fields.count(),"select_count": select_fields.count(), "source": "button"}

                            if option_data not in option_forms:
                                option_forms.append(option_data)
                        #-------------------------------------------------------------------

                        #nur Buttons speichern, die durch genau durch Hauptbutton neu sichtbar wurden
                        for sub_button in page.locator("button:visible").all():

                            sub_name = sub_button.inner_text().strip()

                            if not sub_name:
                                sub_name = sub_button.get_attribute("aria-label")

                            if not sub_name:
                                continue

                            if sub_name in before_buttons:
                                continue

                            #elternbutton + unterbutton zusammen speichern,damit gleiche Namen unterschieden werden
                            new_button = (button_name, sub_name)

                            if new_button not in new_buttons:
                                new_buttons.append(new_button)

                    except Exception as error:
                        failed_expandable_buttons.append((button_name, str(error)))

                    print(f"\rPrüfe Aufklappbare Buttons... "f"{len(passed_expandable_buttons) + len(failed_expandable_buttons)}"f"/{len(expandable_buttons)}",end="")

                print()
                print(f"  Aufklappbare Buttons: "f"{len(passed_expandable_buttons)} PASS - "f"{len(failed_expandable_buttons)} FAIL")

                for button, error in failed_expandable_buttons:
                    print(f"      FAIL: {button} - {error}")

                expandable_buttons_result = (
                    f"Aufklappbare Buttons: "
                    f"{len(passed_expandable_buttons)} PASS - "
                    f"{len(failed_expandable_buttons)} FAIL"
                )

                browser_test_result += f"""
                <h4>Aufklappbare Buttons:</h4>
                <p>&nbsp;&nbsp;&nbsp;&nbsp;{expandable_buttons_result}</p>
                """

                report_results[-1] = browser_test_result
                create_report(report_file, test_start, url, report_results)

                #neue Buttons separat prüfen
                try:
                    print()
                    print("Neue Buttons:")

                    for index, (parent_name, new_button_name) in enumerate(new_buttons, start=1):
                        try:
                            page.goto(url)

                            # Elternbutton suchen
                            buttons = page.locator("button:visible")
                            parent_button = None

                            for button in buttons.all():
                                current_name = button.inner_text().strip()

                                if not current_name:
                                    current_name = button.get_attribute("aria-label")

                                if current_name == parent_name:
                                    parent_button = button
                                    break

                            if parent_button is None:
                                raise Exception("Elternbutton nicht gefunden")

                            #elternmenü buttons öffnen
                            parent_button.click(timeout=3000,force=True)
                            page.wait_for_timeout(1000)

                            #unterbutton suchen
                            current_button = None
                            for button in page.locator("button:visible").all():
                                current_name = button.inner_text().strip()

                                if not current_name:
                                    current_name = button.get_attribute("aria-label")

                                if current_name == new_button_name:
                                    current_button = button
                                    break

                            if current_button is None:
                                raise Exception("Neuer Button nicht gefunden")

                            if not current_button.is_visible():
                                raise Exception("Neuer Button nicht sichtbar")

                            #Unterbutton klicken
                            current_button.click(timeout=3000,force=True)
                            page.wait_for_timeout(500)

                            # -------------------------------------------------------------------
                            #Formular nach dem Öffnen eines aufklappbaren Unterelements erkennen und speichern
                            inputs = page.locator("input, textarea")

                            if inputs.count() > 0:
                                form_data = {"url": page.url,"button": f"{parent_name} - {new_button_name}","input_count": inputs.count(),"source": "button"}

                                if form_data not in found_forms:
                                    found_forms.append(form_data)

                            #Auswahlbare Felder nach dem Button-Klick erkennen und speichern
                            radio_fields = page.locator('input[type="radio"]')
                            select_fields = page.locator("select")

                            if radio_fields.count() > 0 or select_fields.count() > 0:
                                option_data = {"url": page.url, "button": f"{parent_name} - {new_button_name}","radio_count": radio_fields.count(),"select_count": select_fields.count(), "source": "button"}

                                if option_data not in option_forms:
                                    option_forms.append(option_data)
                            # -------------------------------------------------------------------

                            passed_new_buttons.append((parent_name, new_button_name))

                        except Exception as error:
                            failed_new_buttons.append((parent_name,new_button_name,str(error)))

                    print(f"Prüfe neue Buttons... "f"{len(passed_new_buttons) + len(failed_new_buttons)}"f"/{len(new_buttons)}")
                    print(f"  Neue Buttons: "f"{len(passed_new_buttons)} PASS - "f"{len(failed_new_buttons)} FAIL")

                    for parent, button, error in failed_new_buttons:
                        print(f"      FAIL: {parent} -> "f"{button} - {error}")

                    new_buttons_result = (
                        f"Neue Buttons: "
                        f"{len(passed_new_buttons)} PASS - "
                        f"{len(failed_new_buttons)} FAIL"
                    )

                    browser_test_result += f"""
                    <h4>Neue Buttons:</h4>
                    <p>&nbsp;&nbsp;&nbsp;&nbsp;{new_buttons_result}</p>
                    """

                    report_results[-1] = browser_test_result
                    create_report(report_file, test_start, url, report_results)

                except Exception as error:
                    print("  Neue Buttons: "f"FAIL - konnte nicht geprüft werden: {error}")

            except Exception as error:
                print("  Aufklappbare Buttons: "f"FAIL - konnte nicht geprüft werden: {error}")

            #alle gefundenen Buttons zusammenführen gesamt anzeige
            button_total = (len(filtered_buttons)+ len(expandable_buttons)+ len(new_buttons))

            print()
            print("Buttons Gesamtübersicht:")
            print(f"  Normale Buttons: {len(filtered_buttons)}")
            print(f"  Aufklappbare Buttons: {len(expandable_buttons)}")
            print(f"  Neue Buttons: {len(new_buttons)}")
            print(f"  Insgesamt: {button_total}")

            button_total_result = f"""
            <h4>Buttons Gesamtübersicht:</h4>
            <p>&nbsp;&nbsp;&nbsp;&nbsp;Normale Buttons: {len(filtered_buttons)}</p>
            <p>&nbsp;&nbsp;&nbsp;&nbsp;Aufklappbare Buttons: {len(expandable_buttons)}</p>
            <p>&nbsp;&nbsp;&nbsp;&nbsp;Neue Buttons: {len(new_buttons)}</p>
            <p>&nbsp;&nbsp;&nbsp;&nbsp;Insgesamt: {button_total}</p>
            """

            browser_test_result += button_total_result

            report_results[-1] = browser_test_result
            create_report(report_file, test_start, url, report_results)

#Interaktive DOM Elemente
            try:
                print()
                print("Interaktive Elemente:")
                page.goto(url)

                #interaktive HTML-Elemente suchen
                elements = page.locator('a, [role="button"]:not(button), [aria-expanded]:not(button)')

                #gefundene Elemente sammeln
                for element in elements.all():

                    if not element.is_visible():
                        continue

                    tag_name = element.evaluate("(element) => element.tagName.toLowerCase()")

                    element_name = element.inner_text().strip()

                    if not element_name:
                        element_name = element.get_attribute("aria-label")

                    if not element_name:
                        continue

                    role = element.get_attribute("role")
                    aria_expanded = element.get_attribute("aria-expanded")

                    #informationen zum interaktiven Element speichern
                    interactive_element = (tag_name,element_name,role,aria_expanded)

                    if interactive_element not in interactive_elements:
                        interactive_elements.append(interactive_element)
                        dom_interactive_count += 1

                #start der Fortschrittsanzeige
                print(f"Prüfe Interaktive Elemente... "f"0/{len(interactive_elements)}",end="")

                #interaktive Elemente einzeln prüfen
                for tag_name, element_name, role, aria_expanded in interactive_elements:

                    try:
                        if not element_name:
                            raise Exception("Interaktives Element ohne Namen")

                        passed_interactive_elements.append((tag_name, element_name))

                    except Exception as error:
                        failed_interactive_elements.append((tag_name,element_name,str(error)))

                    print(f"\rPrüfe Interaktive Elemente... "f"{len(passed_interactive_elements) + len(failed_interactive_elements)}"f"/{len(interactive_elements)}",end="")

                print()
                print(f"  Interaktive Elemente: "f"{len(passed_interactive_elements)} PASS - "f"{len(failed_interactive_elements)} FAIL")

                #DOM Soll/Ist Vergleich
                interactive_duplicates = (dom_interactive_count - len(interactive_elements))
                print(f"  DOM Referenz: "f"{dom_interactive_count}")
                print(f"  Eindeutig geprüft: "f"{len(interactive_elements)}")
                print(f"  Duplikate: "f"{interactive_duplicates}")

                # fehler anzeigen
                for tag_name, element_name, error in failed_interactive_elements:
                    print(f"    FAIL: {tag_name} | "f"{element_name} - {error}")

            except Exception as error:
                print("  Interaktive Elemente: "f"FAIL - konnte nicht erkannt werden: {error}")

#Interaktive Unterelemente
            interactive_children = []
            passed_interactive_children = []
            failed_interactive_children = []

            try:
                print()
                print("Interaktive Unterelemente:")

                #sofort anzeigen, dass der Test gestartet ist
                print("Prüfe interaktive Unterelemente... 0/0",end="")

                page.goto(url)

                #interaktive Elemente verwenden die als mögliche Eltern für Unterelemente dienen
                expandable_interactive = page.locator('button[aria-expanded], ''a[aria-expanded], ''[role="button"][aria-expanded], ''[aria-haspopup="true"], ''summary')

                interactive_parents = []

                for element in expandable_interactive.all():

                    if not element.is_visible():
                        continue

                    element_name = element.inner_text().strip()

                    if not element_name:
                        element_name = element.get_attribute("aria-label")

                    if not element_name:
                        continue

                    if element_name not in interactive_parents:
                        interactive_parents.append(element_name)

                #eltern-Elemente einzeln öffnen
                page.set_default_timeout(3000)
                for parent_name in interactive_parents:

                    try:
                        page.goto(url)

                        #eltern-Element suchen
                        elements = page.locator('button[aria-expanded]:visible, ''a[aria-expanded]:visible, ''[role="button"][aria-expanded]:visible, ''[aria-haspopup="true"]:visible, ''summary:visible')
                        parent_element = None

                        for element in elements.all():

                            current_name = element.inner_text().strip()

                            if not current_name:
                                current_name = element.get_attribute("aria-label")

                            if current_name == parent_name:
                                parent_element = element
                                break

                        if parent_element is None:
                            raise Exception("Interaktives Eltern-Element nicht gefunden")

                        #vorher sichtbare interaktive Elemente merken
                        before_elements = set()
                        elements = page.locator('button:visible, a:visible, [role="button"]:visible')

                        for index in range(elements.count()):

                            try:
                                element = elements.nth(index)                               #nth = gibt das Element an der jeweiligen Position zurück
                                name = element.inner_text(timeout=3000).strip()

                                if not name:
                                    name = element.get_attribute("aria-label",timeout=3000)

                                if name:
                                    before_elements.add(name)

                            except Exception:
                                continue

                        #eltern-Element öffnen
                        parent_element.click(timeout=3000,force=True)
                        page.wait_for_timeout(1000)

                        # -------------------------------------------------------------------
                        #Formular nach dem Öffnen eines interaktiven Eltern-Elements erkennen und speichern
                        inputs = page.locator("input, textarea")

                        if inputs.count() > 0:
                            form_data = {"url": page.url, "parent": parent_name,"button": None, "input_count": inputs.count()}

                            if form_data not in found_forms:
                                found_forms.append(form_data)

                        #Auswahlbare Felder nach dem Button-Klick erkennen und speichern
                        radio_fields = page.locator('input[type="radio"]')
                        select_fields = page.locator("select")

                        if radio_fields.count() > 0 or select_fields.count() > 0:
                            option_data = {"url": page.url, "parent": parent_name,"button": None,"radio_count": radio_fields.count(),"select_count": select_fields.count(), "source": "button"}

                            if option_data not in option_forms:
                                option_forms.append(option_data)
                        # -------------------------------------------------------------------

                        #neue interaktive Unterelemente suchen
                        children = page.locator('button:visible, a:visible, [role="button"]:visible')           #a:visible = sichtbare Links

                        for index in range(children.count()):

                            try:
                                child = children.nth(index)
                                child_name = child.inner_text(timeout=3000).strip()

                                if not child_name:
                                    child_name = child.get_attribute("aria-label",timeout=3000)

                                if not child_name:
                                    continue

                                if child_name in before_elements:
                                    continue

                                interactive_child = (parent_name,child_name)

                                if interactive_child not in interactive_children:
                                    interactive_children.append(interactive_child)

                            except Exception:
                                continue

                    except Exception as error:
                        failed_interactive_children.append((parent_name,"",str(error)))

                    print(f"\rSuche interaktive Unterelemente... "f"{len(interactive_children)} gefunden", end="")

                print()
                print(f"Prüfe interaktive Unterelemente... "f"0/{len(interactive_children)}", end="")

                interactive_children_checked = 0  #zählt, wie viele Unterelemente tatsächlich geprüft wurden

                #gefundene Unterelemente separat prüfen
                for parent_name, child_name in interactive_children:

                    try:
                        page.goto(url)

                        #eltern-Element erneut suchen
                        elements = page.locator('button[aria-expanded]:visible, ''a[aria-expanded]:visible, ''[role="button"][aria-expanded]:visible, ''[aria-haspopup="true"]:visible, ''summary:visible')

                        parent_element = None
                        for element in elements.all():
                            current_name = element.inner_text().strip()

                            if not current_name:
                                current_name = element.get_attribute("aria-label")

                            if current_name == parent_name:
                                parent_element = element
                                break

                        if parent_element is None:
                            raise Exception("Interaktives Eltern-Element nicht gefunden")

                        # Eltern-Element öffnen
                        parent_element.click(timeout=3000,force=True)
                        page.wait_for_timeout(1000)

                        # -------------------------------------------------------------------
                        #Formular nach dem Öffnen eines interaktiven Unterelements erkennen und speichern
                        inputs = page.locator("input, textarea")


                        if inputs.count() > 0:
                            form_data = {"url": page.url,"parent": parent_name, "button": child_name, "input_count": inputs.count()}

                            if form_data not in found_forms:
                                found_forms.append(form_data)

                        #Auswahlbare Felder nach dem Button-Klick erkennen und speichern
                        radio_fields = page.locator('input[type="radio"]')
                        select_fields = page.locator("select")

                        if radio_fields.count() > 0 or select_fields.count() > 0:
                            option_data = {"url": page.url, "button": parent_name,"radio_count": radio_fields.count(),"select_count": select_fields.count(), "source": "button"}

                            if option_data not in option_forms:
                                option_forms.append(option_data)
                        # -------------------------------------------------------------------

                        #unterelement suchen
                        child_element = None

                        for element in page.locator('button:visible, a:visible, [role="button"]:visible').all():
                            current_name = element.inner_text().strip()

                            if not current_name:
                                current_name = element.get_attribute("aria-label")

                            if current_name == child_name:
                                child_element = element
                                break

                        if child_element is None:
                            raise Exception("Interaktives Unterelement nicht gefunden")

                        if not child_element.is_visible():
                            raise Exception("Interaktives Unterelement nicht sichtbar")

                        child_element.click(timeout=3000,force=True)
                        passed_interactive_children.append((parent_name,child_name))

                    except Exception as error:
                        error_message = str(error).splitlines()[0]
                        failed_interactive_children.append((parent_name, child_name, error_message))

                    interactive_children_checked += 1
                    #genaueres anzeigen was  tatsächlich abgearbeitet ist
                    print(f"\rPrüfe interaktive Unterelemente... "f"{interactive_children_checked}/{len(interactive_children)}",end="")

                print()
                print(f"  Interaktive Unterelemente: "f"{len(passed_interactive_children)} PASS - "f"{len(failed_interactive_children)} FAIL")

                for parent, child, error in failed_interactive_children:
                    print(f"    FAIL: {parent} -> {child} - {error}")

            except Exception as error:
                print("  Interaktive Unterelemente: "f"FAIL - konnte nicht geprüft werden: {error}")

            #Gesamtübersicht interaktive Elemente
            interactive_total = (len(interactive_elements)+len(interactive_children))

            print()
            print("Interaktive Elemente Gesamtübersicht:")
            print(f"  Starterseite: {len(interactive_elements)}")
            print(f"  Unterelemente: {len(interactive_children)}")
            print(f"  Insgesamt: {interactive_total}")

# --------------------------------------------------
# Browser Navigation ziel weiterführende Links auf Zielseiten prüfen und Formulare erkennen
# --------------------------------------------------
            print()
            print("Browser Navigation:")
            form_link_pages = []

            #nur mögliche HTML-Zielseiten für die Browser-Navigation verwenden
            html_links =[link for link in passed_links
                         if not link.lower().endswith((".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico",))]  #".pdf" ?`

            try:
                print(f"Prüfe Zielseiten auf mögliche Formulare... "f"0/{len(html_links)}",end="")
                for link_index, link in enumerate(html_links, start=1):

                    try:
                        page.goto(link,timeout=10000)
                        inputs = page.locator("input, textarea, select")
                        visible_inputs = inputs.locator(":visible")

                        if visible_inputs.count() > 0:
                            form_link_pages.append({"source_url": url,"via_url": link,"target_url": page.url,"input_count": visible_inputs.count()})

                        else:
                            #keine Eingabefelder auf der Zielseite gefunden prüfen ob die Zielseite weitere HTML-Links zu möglichen Formularseiten enthält.
                            page_links_all = page.locator("a[href]").all()
                            collected_hrefs = []
                            for pl in page_links_all:
                                href = pl.get_attribute("href")
                                if href:
                                    collected_hrefs.append(href)

                            current_page_url = page.url  #Basis-URL vor Navigation sichern

                            for target_link in collected_hrefs:
                                if not target_link:
                                    continue

                                try:
                                    target_url = urljoin(current_page_url, target_link)

                                    #zielseite öffnen
                                    try:
                                        page.goto(target_url, timeout=10000)
                                        inputs = page.locator("input, textarea")

                                        #Eingabefelder der Zielseite zählen, damit die Anzahl als Erwartungswert für die spätere Formularprüfung gespeichert werden kann
                                        input_count = inputs.count()

                                        #formular gefunden
                                        if input_count > 0:
                                            form_link_pages.append(
                                                {"source_url": url,"via_url": link,"target_url": target_url,"input_count": input_count})

                                    except Exception as error:
                                        print(f"\n    Fehler bei Zielseite {target_url}: {error}")

                                except Exception as error:
                                    print("FEHLER BEI WEITERER ZIELSEITE:", error)

                    except Exception as error:
                        print(f"\n    Link konnte nicht geöffnet werden: {link}")
                        print(f"    Fehler: {error}")

                    print(f"\rPrüfe Zielseiten auf mögliche Formulare... "f"{link_index}/{len(html_links)}",end="")

                print()

            except Exception as error:
                print("  Browser Navigation: "f"FAIL - konnte Zielseiten nicht prüfen: {error}")


#Formulare anzeige (Knöpfe)
            print()
            print("Formulare über Knöpfe :")
            form_results = []

            try:
                if not found_forms:
                    print("  Keine Formularstellen über Knöpfe gefunden")

                else:
                    print(f"Prüfe Formulare... "f"0/{len(found_forms)}",end="")

                    for form_index, form_data in enumerate(found_forms, start=1):
                        try:
                            page.goto(form_data["url"],timeout=10000)
                            inputs = page.locator("input, textarea")
                            input_count = inputs.count()
                            field_results = []

                            print(f"\rPrüfe Formulare... {form_index}/{len(found_forms)}", end="")

# Formulare ausfüllen (Knöpfe)
                            test_value = "QA Test"       #test text der in die Eingabefelder geschireben wird
                            for index in range(inputs.count()):

                                field = inputs.nth(index)
                                field_type = field.get_attribute("type")

                                #Checkboxen nicht mit Text befüllen
                                if field_type == "checkbox":
                                    continue

                                #Testwert abhängig vom Feldtyp(email)    #test
                                if field_type == "email":
                                    test_value = "qa-test@example.com"
                                else:
                                    test_value = "QA Test"

                                #start
                                try:
                                    field.fill(test_value)  #Testwert in das Eingabefeld schreiben

                                    if field.input_value() != test_value:
                                        raise Exception("Eingabe wurde nicht übernommen")

                                    # PASS-Ergebnis speichern
                                    field_results.append(
                                        {"index": index + 1, "status": "PASS", "message": "beschreibbar"})

                                # FAIL-Ergebnis speichern
                                except Exception as field_error:
                                    field_results.append(
                                        {"index": index + 1, "status": "FAIL", "message": str(field_error)})

                            #Formular absenden und Ergebnis prüfen
                            submit_result = {"status": "FAIL","message": "Formular konnte nicht abgeschickt werden"}

                            try:
                                #Submit-Button des Formulars suchen
                                submit_button = page.locator('button[type="submit"]')

                                if submit_button.count() == 0:
                                    raise Exception("Submit-Button nicht gefunden")

                                submit_button.first.click(timeout=3000)
                                page.wait_for_load_state("domcontentloaded", timeout=10000)
                                success_message = page.get_by_text("Nachricht wurde erfolgreich übermittelt.",exact=True)
#--
                                print("  Aktuelle URL nach Submit:", page.url)
                                print("  Erfolgsmeldung vorhanden:", success_message.count())
#--
                                if success_message.count() == 0:
                                    raise Exception("Erfolgsmeldung nicht gefunden")

                                if not success_message.first.is_visible():
                                    raise Exception("Erfolgsmeldung nicht sichtbar")

                                submit_result = {"status": "PASS","message": "Formular erfolgreich übermittelt"}

                            except Exception as submit_error:
                                submit_result = {"status": "FAIL","message": str(submit_error)}

                            #komplettes Formularergebnis speichern
                            form_results.append(
                                {"form_index": form_index,
                                 "url": form_data["url"],
                                 "button": form_data.get("button"),
                                 "source": "button",
                                 "expected": form_data["input_count"],
                                 "found": input_count,
                                 "fields": field_results,
                                 "submit": submit_result
                                 })

                            print(f"\rPrüfe Formulare... "f"{form_index}/{len(found_forms)}", end="")

                        except Exception as error:
                            print(f"\rPrüfe Formulare... {form_index}/{len(found_forms)} - FAIL: {error}")

                    print()
                    for form_result in form_results:

                        print(f"Formular {form_result['form_index']}:")
                        print(f"  URL: {form_result['url']}")
                        print(f"  Button: {form_result['button']}")
                        print(f"  Eingabefelder erwartet: {form_result['expected']}")
                        print(f"  Eingabefelder gefunden: {form_result['found']}")

                        if form_result["found"] > 0:
                            print("  Eingabefelder Vorhanden: JA")

                        else:
                            print("  Eingabefelder Vorhanden: NEIN")

                        for field_result in form_result["fields"]:
                            print(f"    Feld {field_result['index']}: "f"{field_result['status']} - "f"{field_result['message']}")

                        print(f"  Absenden: "f"{form_result['submit']['status']} - "f"{form_result['submit']['message']}")
                        print()

            except Exception as error:
                print("  Formulare über Knöpfe: "f"FAIL - konnte nicht geprüft werden: {error}")

#Formulare anzeigen (Links)
            print()
            print("Prüfe Formulare (Links):")

            try:
                if not form_link_pages:
                    print("  Keine Formularseiten über Links gefunden")

                else:
                    print(f"Prüfe Formulare Links... "f"0/{len(form_link_pages)}",end="")
                    link_form_results = []

                    for form_index, form_data in enumerate(form_link_pages, start=1):
                        try:
                            page.goto(form_data["target_url"],timeout=10000)
                            inputs = page.locator("input, textarea")
                            input_count = inputs.count()

                            print(f"\rPrüfe Formulare über Links... "f"{form_index}/{len(form_link_pages)}",end="")

#Formulare ausfüllen (Links)
                            field_results = []
                            test_value = "QA Test"

                            for index in range(inputs.count()):

                                field = inputs.nth(index)
                                field_type = field.get_attribute("type")

                                # Checkboxen nicht mit Text befüllen
                                if field_type == "checkbox":
                                    continue

                                #Testwert abhängig vom Feldtyp(email)    #test
                                if field_type == "email":
                                    test_value = "qa-test@example.com"
                                else:
                                    test_value = "QA Test"

                                try:
                                    field.fill(test_value)

                                    if field.input_value() != test_value:
                                        raise Exception("Eingabe wurde nicht übernommen")

                                    field_results.append({"index": index + 1, "status": "PASS", "message": "beschreibbar"})

                                except Exception as field_error:
                                    field_results.append(
                                        {"index": index + 1, "status": "FAIL", "message": str(field_error)})

                            # Formular absenden und Ergebnis prüfen
                            submit_result = {"status": "FAIL","message": "Formular konnte nicht abgeschickt werden"}

                            try:
                                #Submit-Button des Formulars suchen
                                submit_button = page.locator('button[type="submit"]')

                                if submit_button.count() == 0:
                                    raise Exception("Submit-Button nicht gefunden")

                                with page.expect_response(lambda response: response.request.method == "POST",timeout=10000) as response_info:
                                    submit_button.first.click(timeout=3000)

                                response = response_info.value

                                if not 200 <= response.status < 400:
                                    raise Exception(f"Formular-Submit fehlgeschlagen - HTTP {response.status}")

                                submit_result = {"status": "PASS","message": f"Formular erfolgreich übermittelt - HTTP {response.status}"}

                            except Exception as submit_error:
                                submit_result = {"status": "FAIL", "message": str(submit_error)}

                            #komplettes Formularergebnis speichern
                            link_form_results.append(
                                {"form_index": form_index,
                                 "url": form_data["target_url"],
                                 "via_url": form_data.get("via_url", "-"),
                                 "button": None,
                                 "source": "link",
                                 "expected": form_data["input_count"],
                                 "found": input_count,
                                 "fields": field_results,
                                 "submit": submit_result
                                 })

                        except Exception:
                            print(f"\rPrüfe Formulare über Links... "f"{form_index}/{len(form_link_pages)}",end="")
                    print()

                    for form_result in link_form_results:
                        print(f"Formular {form_result['form_index']} (Link):")
                        print(f"  URL:            {form_result['url']}")
                        print(f"  Gefunden über:  {form_result['via_url']}")
                        print(f"  Eingabefelder erwartet: {form_result['expected']}")
                        print(f"  Eingabefelder gefunden: {form_result['found']}")
                        print(f"  Eingabefelder Vorhanden: {'JA' if form_result['found'] > 0 else 'NEIN'}")

                        for field_result in form_result["fields"]:
                            print(f"    Feld {field_result['index']}: {field_result['status']} - {field_result['message']}")

                        print(f"  Absenden: "f"{form_result['submit']['status']} - " f"{form_result['submit']['message']}")
                        print()

            except Exception as error:
                print("  Formulare über Links: "f"FAIL - konnte nicht geprüft werden: {error}")

#Formulare Auswahlbare Inhalte/optionsfelder
            print()
            print("Formulare Auswahlbare Inhalte / Optionsfelder:")

            try:
                if not option_forms:
                    print("  Keine auswählbaren Inhalte gefunden")

                else:
                    print(f"Prüfe Auswahlfelder... 0/{len(option_forms)}", end="")

                    option_results = []

                    for option_index, option_data in enumerate(option_forms, start=1):

                        try:
                            page.goto(option_data["url"], timeout=10000)

                            radio_fields = page.locator('input[type="radio"]')
                            select_fields = page.locator("select")

                            radio_count = radio_fields.count()
                            select_count = select_fields.count()

                            #Select-Felder einzeln prüfen
                            select_results = []

                            for select_index in range(select_count):

                                select = select_fields.nth(select_index)
                                options = select.locator("option")

                                option_count = options.count()
                                selectable_count = 0
                                passed_options = 0
                                failed_options = 0

                                individual_option_results = []
                                for option_index_inner in range(option_count):

                                    option = options.nth(option_index_inner)

                                    if option.is_disabled():
                                        continue

                                    selectable_count += 1

                                    try:
                                        option_value = option.get_attribute("value")

                                        #Option auswählen
                                        select.select_option(index=option_index_inner)

                                        #Prüfen, ob die Auswahl übernommen wurde
                                        selected_value = select.input_value()

                                        if selected_value == option_value:
                                            passed_options += 1
                                            individual_option_results.append({"option_index": option_index_inner + 1,"status": "PASS","message": "auswählbar"})

                                        else:
                                            failed_options += 1
                                            individual_option_results.append({"option_index": option_index_inner + 1,"status": "FAIL","message": "Auswahl wurde nicht übernommen"})

                                    except Exception as error:
                                        failed_options += 1
                                        individual_option_results.append({"option_index": option_index_inner + 1,"status": "FAIL","message": str(error)})

                                select_results.append(
                                    {
                                        "select_index": select_index + 1,
                                        "option_count": option_count,
                                        "selectable_count": selectable_count,
                                        "passed": passed_options,
                                        "failed": failed_options,
                                        "options": individual_option_results
                                    })

                            option_results.append(
                                {
                                    "form_index": option_index,
                                    "url": option_data["url"],
                                    "button": option_data.get("button"),
                                    "source": option_data.get("source"),
                                    "radio_expected": option_data["radio_count"],
                                    "radio_found": radio_count,
                                    "select_expected": option_data["select_count"],
                                    "select_found": select_count,
                                    "select_results": select_results
                                }
                            )

                            print(f"\rPrüfe Auswahlfelder... "f"{option_index}/{len(option_forms)}",end="")

                        except Exception as error:
                            print(f"\rPrüfe Auswahlfelder... "f"{option_index}/{len(option_forms)} - FAIL: {error}",end="")

                    print()

                    for option_result in option_results:
                        print(f"Formular {option_result['form_index']}:")
                        print(f"  URL: {option_result['url']}")
                        print(f"  Button: {option_result['button']}")
                        print(f"  Radio-Felder erwartet: "f"{option_result['radio_expected']}")
                        print(f"  Radio-Felder gefunden: "f"{option_result['radio_found']}")
                        print(f"  Select-Felder erwartet: "f"{option_result['select_expected']}")
                        print(f"  Select-Felder gefunden: "f"{option_result['select_found']}")

                        for select_result in option_result["select_results"]:
                            print()
                            print(f"  Select-Feld {select_result['select_index']}:")
                            print(f"    Optionen gefunden: {select_result['option_count']}")
                            print(f"    Auswahloptionen: {select_result['selectable_count']}")
                            print(f"    Funktionieren: "f"{select_result['passed']} PASS - "f"{select_result['failed']} FAIL")

                            for option_result in select_result["options"]:
                                print(f"      Option {option_result['option_index']}: "f"{option_result['status']} - "f"{option_result['message']}")

            except Exception as error:
                print("  Auswahlfelder: FAIL - "f"konnte nicht geprüft werden: {error}")


#Formulare Gesamtübersicht
            #Formulare aus Buttons und Links für die Gesamtübersicht zusammenführen
            all_form_results = form_results + link_form_results
            total_fields = sum(len(form_result["fields"]) for form_result in all_form_results)

            button_forms = sum(1 for form_result in all_form_results if form_result.get("source") == "button")  #source = gibt an, ob das Formular über einen Button oder einen Link gefunden wurde
            link_forms = sum(1 for form_result in all_form_results if form_result.get("source") == "link")

            passed_fields = sum(sum(1 for field in form_result["fields"] if field["status"] == "PASS") for form_result in all_form_results)
            failed_fields = sum(sum(1 for field in form_result["fields"] if field["status"] == "FAIL") for form_result in all_form_results)

            #Auswahlfelder Gesamtübersicht
            option_forms_total = len(option_results)

            total_selects = sum(option_result["select_found"] for option_result in option_results)
            total_options = sum(select_result["option_count"] for option_result in option_results for select_result in option_result["select_results"])

            passed_options_total = sum(select_result["passed"] for option_result in option_results for select_result in option_result["select_results"])
            failed_options_total = sum(select_result["failed"] for option_result in option_results for select_result in option_result["select_results"])

            # Gesamtzahl aller Formulare
            total_forms = len(all_form_results) + option_forms_total

            print()
            print("Formulare Gesamtübersicht:")
            print(f"  Formulare Gesamt: {total_forms}")
            print(f"  Formulare über Buttons: {button_forms}")
            print(f"  Formulare über Links: {link_forms}")
            print(f"  Formulare mit Auswahlfeldern: {option_forms_total}")

            print()
            print(f"  Eingabefelder: {total_fields}")
            print(f"  Beschreibbar: {passed_fields}")
            print(f"  Nicht beschreibbar: {failed_fields}")

            print()
            print(f"  Select-Felder: {total_selects}")
            print(f"  Auswahloptionen: {total_options}")
            print(f"  Auswählbar: {passed_options_total}")
            print(f"  Nicht auswählbar: {failed_options_total}")

    except Exception as error:
        print("  Browser Tests : FAIL - konnte nicht  vollständig geprüft werden:", error)
