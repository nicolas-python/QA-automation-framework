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
        print("  HTML/Struktur: FAIL - konnte nicht prüfen:", error)


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
        else:
            print("    Charset: FAIL - nicht vorhanden")

    except Exception as error:
        print("  Meta-Informationen Charset: FAIL - konnte nicht geprüft werden:", error)


    #viewport prüfen --> für vernünftige Darstellung auf mobilen Geräten
    try:
        viewport = re.search(r'<meta[^>]*name=["\']viewport["\'][^>]*content=["\'](.*?)["\']',response.text,re.IGNORECASE)

        print()
        print("  Viewport:")

        if viewport:
            viewport_value = viewport.group(1).lower()
            print(f"    Viewport: PASS - {viewport_value}")

            if "width=device-width" in viewport_value:              #device-width= Behandle die Breite der Webseite so, als wäre sie so breit wie das Gerät
                print(f"    Mobile Darstellung: PASS - width=device-width")
            else:
                print(f"    Mobile Darstellung: FAIL - width=device-width fehlt - {viewport_value}")

        else:
            print("    Viewport: FAIL - nicht vorhanden")

    except Exception as error:
        print("  Meta-Informationen Viewport: FAIL - konnte nicht geprüft werden:", error)


    #description = Beschreibung der Seite für Suchmaschinen
    try:
        description = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']',response.text,re.IGNORECASE)

        print()
        print("  Description:")

        if description:
            description_value = description.group(1).strip()

            if description_value:
                print(f"    Description: PASS - {description_value}")
            else:
                print("    Description: FAIL - Beschreibung ist leer")

        else:
            print("    Description: FAIL - nicht vorhanden")


    except Exception as error:
        print("  Meta-Informationen description: FAIL - konnte nicht geprüft werden:", error)


    #robots = Anweisungen für Suchmaschinen-Crawler
    try:
        robots = re.search(r'<meta[^>]*name=["\']robots["\'][^>]*content=["\'](.*?)["\']',response.text,re.IGNORECASE)

        print()
        print("  Robots:")

        if robots:
            robots_value = robots.group(1).strip()

            if robots_value:
                print(f"    Robots: PASS - {robots_value}")
            else:
                print("     Robots: FAIL - Wert ist leer")

        else:
            print("    Robots: FAIL - nicht vorhanden")

    except Exception as error:
        print("  Meta-Informationen robots: FAIL - konnte nicht geprüft werden:", error)

    #og:title, og:image = Social-Media-Vorschauen
    #author = Angabe des Autors sinvolle info ?

# --------------------------------------------------
# Browser Tests
# --------------------------------------------------
#normale Buttons
    #gefundene Formulare/Eingabefelder speichern
    found_forms = []

    #Buttons klicken
    print()
    print("Browser Tests")

    #sesamtstatistik buttons
    all_button_results = {}

    passed_buttons = []
    failed_buttons = []

    # Interaktive DOM Elemente Starterseite
    interactive_elements = []
    passed_interactive_elements = []
    failed_interactive_elements = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()               #startet einen Chromium-Browser über Python
            page = browser.new_page()                   #page= eine einzelne Browserseite bzw ein tap
            page.goto(url)                              # öffnet die geladene URL im automatisierten Browser
            dom_interactive_count = 0                   #feste DOM-Referenz für den gesamten Browser-Test

            # -------------------------------------------------------------------
            # Formular / Eingabefelder nach dem Öffnen des Unterelements suchen
            inputs = page.locator("input, textarea, select")

            if inputs.count() > 0:
                form_data = {"url": page.url, "button": None, "input_count": inputs.count()}

                if form_data not in found_forms:
                    found_forms.append(form_data)
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

                    inputs = page.locator("input, textarea, select")

                    if inputs.count() > 0:
                        form_data = {"url": page.url,"button": button_name,"input_count": inputs.count()}
                        found_forms.append(form_data)

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

#---2 test fals website aufklappbare buttons kein aria label haben
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
#---
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
                        # Formular / Eingabefelder nach dem Öffnen des Unterelements suchen
                        inputs = page.locator("input, textarea, select")

                        if inputs.count() > 0:
                            form_data = {"url": page.url, "input_count": inputs.count()}

                            if form_data not in found_forms:
                                found_forms.append(form_data)
                        # -------------------------------------------------------------------

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
                            # Formular / Eingabefelder nach dem Öffnen des Unterelements suchen
                            inputs = page.locator("input, textarea, select")

                            if inputs.count() > 0:
                                form_data = {"url": page.url, "button": None, "input_count": inputs.count()}

                                if form_data not in found_forms:
                                    found_forms.append(form_data)
                            # -------------------------------------------------------------------

                            passed_new_buttons.append((parent_name, new_button_name))

                        except Exception as error:

                            failed_new_buttons.append((parent_name,new_button_name,str(error)))

                    print(f"Prüfe neue Buttons... "f"{len(passed_new_buttons) + len(failed_new_buttons)}"f"/{len(new_buttons)}")

                    print(f"  Neue Buttons: "f"{len(passed_new_buttons)} PASS - "f"{len(failed_new_buttons)} FAIL")

                    for parent, button, error in failed_new_buttons:
                        print(f"      FAIL: {parent} -> "f"{button} - {error}")

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
                        # Formular / Eingabefelder nach dem Öffnen des Unterelements suchen
                        inputs = page.locator("input, textarea, select")

                        if inputs.count() > 0:
                            form_data = {"url": page.url, "parent": parent_name,"button": None, "input_count": inputs.count()}

                            if form_data not in found_forms:
                                found_forms.append(form_data)
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

                #prüfen, ob überhaupt Unterelemente gefunden wurden
                if not interactive_children:
                    print()
                    print("  Interaktive Unterelemente: ""0 PASS - 0 FAIL")

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
                        # Formular / Eingabefelder nach dem Öffnen des Unterelements suchen
                        inputs = page.locator("input, textarea, select")

                        if inputs.count() > 0:
                            form_data = {"url": page.url,"parent": parent_name, "button": child_name, "input_count": inputs.count()}

                            if form_data not in found_forms:
                                found_forms.append(form_data)
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


#Formulare anzeige
            print()
            print("Formulare:")


            try:
                if not found_forms:
                    print()
                    print("  Keine Formularstellen gefunden")

                else:
                    for form_index, form_data in enumerate(found_forms, start=1):
                        print(f"Prüfe Formulare... "f"0/{len(found_forms)}",end="")

                    try:
                        page.goto(form_data["url"],timeout=10000)

                        print(f"\rPrüfe Formulare... "f"{form_index}/{len(found_forms)}",end="")
                        print()

                        print(f"Formular {form_index}:")
                        print(f"  URL: {form_data['url']}")
                        print(f"  Button: {form_data.get('button')}")
                        print(f"  Eingabefelder erwartet: {form_data['input_count']}")

                        #eingabefelder suchen
                        inputs = page.locator("input, textarea, select")
                        print(f"  Eingabefelder gefunden: "f"{inputs.count()}")

                        input_count = inputs.count()

                        print(f"  Eingabefelder: {input_count}")

                        if input_count > 0:
                            print("  Eingabefelder Vorhanden: JA")
                        else:
                            print("  Eingabefelder Vorhanden: NEIN")

#Formulare ausfüllen
                        test_value = "QA Test"                  #test text der in die Eingabefelder geschireben wird

                        try:
                            for index in range(inputs.count()):
                                field = inputs.nth(index)

                                field_type = field.get_attribute("type")

                                #Checkboxen nicht mit Text befüllen
                                if field_type == "checkbox":
                                    continue

                                #start
                                field.fill(test_value)

                                if field.input_value() == test_value:
                                    continue

                                raise Exception("Eingabe wurde nicht übernommen")

                            print("  Eingabefelder beschreibbar: JA")

                        except Exception as error:
                            print(f"  Eingabefelder beschreibbar: NEIN - {error}")

                    except Exception as error:
                        print(f"\rPrüfe Formulare... "f"{form_index}/{len(found_forms)} "f"- FAIL: {error}")

                    print()

            except Exception as error:
                print("  Formulare: "f"FAIL - konnte nicht geprüft werden: {error}")

    except Exception as error:
        print("  Browser Tests : FAIL - konnte nicht  vollständig geprüft werden:", error)

    #Login testen


