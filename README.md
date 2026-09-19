# QA Automation Framework

Ein selbst entwickeltes Python-Framework zur automatisierten Prüfung von Websites.
Das Framework führt verschiedene HTTP-, HTML- und Browser-Tests durch und überprüft dabei sowohl technische Eigenschaften als auch die Funktionalität einer Website.

## Funktionen
### HTTP- und Website-Tests

- HTTPS-Prüfung
- SSL/TLS-Prüfung
- Domain-Prüfung
- HTTP-Statuscode
- Ladezeit
- Title-Prüfung
- Content-Prüfung
- Broken Links
- Bilder und Dateien
- HTML-Struktur
- Sprache
- HEAD und BODY
- Überschriften
- Charset
- Viewport
- Mobile Darstellung
- Meta Description
- Robots

### Browser-Tests

Für die Browser-Tests wird Playwright verwendet.

- Buttons erkennen und testen
- aufklappbare Buttons testen
- neu erscheinende Buttons testen
- interaktive Elemente testen
- interaktive Unterelemente testen
- Navigation zu Zielseiten prüfen
- Formulare über Buttons erkennen
- Formulare über Links erkennen
- Eingabefelder prüfen
- Eingabefelder auf Beschreibbarkeit prüfen
- Formulare absenden
- Select-Felder prüfen
- Auswahloptionen testen

## HTML-Testbericht

Während des Testlaufs wird automatisch ein HTML-Testbericht erstellt.
Die Testergebnisse werden von Python in HTML-Code eingesetzt und anschließend in der Datei qa_test_report.html gespeichert.
Der erzeugte Bericht kann anschließend im Browser geöffnet werden und zeigt den aktuellen Teststand und die Testergebnisse übersichtlich an.

Die Datei qa_test_report.html kann in einem beliebigen Browser geöffnet werden:
qa_test_report.html auswählen → Rechtsklick → Öffnen mit → gewünschten Browser auswählen.

<!-- Screenshot des HTML-Testberichts -->

## Verwendete Technologien

- Python
  - webbrowser
  - Tkinter
  - time
  - ssl
  - socket
  - os
- Requests
- Playwright
- HTML
- CSS
- JavaScript
- PHP

## Installation

1. Repository klonen und in das Projektverzeichnis wechseln.
2. Anschließend die benötigten Python-Pakete installieren: ```bash pip install -r requirements.txt ```
   Benötigte Playwright-Browser installieren: ```bash playwright install```
3. Framework starten: ```bash python main.py```

## Verwendung
Die zu prüfende URL kann in das obere Eingabefeld eingetragen werden. 
Über die vorhandenen Buttons erfolgt die weitere Bedienung des Frameworks.
Nach dem Testlauf wird automatisch der HTML-Testbericht erstellt.
Der Testbericht kann anschließend über den dafür vorgesehenen Button geöffnet werden.

## Projektstruktur
### Zentrale Dateien

- main.py – Startpunkt des Frameworks
- gui.py – grafische Benutzeroberfläche
- test_runner.py – Durchführung der automatisierten Tests und Erstellung des Testberichts
- url_manager.py – Laden, Speichern und Löschen der zu prüfenden URLs
- url_list.txt – gespeicherte URLs
- qa_test_report.html – automatisch erzeugter HTML-Testbericht
- qa_test_report.css – Gestaltung des HTML-Testberichts
- requirements.txt – benötigte Python-Abhängigkeiten
- docs/cheatsheet.txt – hilfreiche Notizen und Befehle

## Testseite

Für die Entwicklung und zum Testen des Frameworks wurde eine eigene Testseite erstellt.
Diese enthält unter anderem:

- verschiedene Buttons
- Untermenüs
- interaktive Elemente
- Formulare
- Eingabefelder
- Select-Felder
- Auswahloptionen
- verschiedene Links und Zielseiten

Dadurch können die Browser- und Funktionstests mit kontrollierten Testfällen entwickelt und überprüft werden.

<!-- Screenshot der Testseite  -->

## Testbericht Druck/PDF

Die Testergebnisse werden automatisch aus dem vorhandenen Testbericht übernommen und für den Druck bzw. die PDF-Ausgabe vorbereitet.
Der Druck-/PDF-Export befindet sich aktuell noch in der Weiterentwicklung. Dabei wird insbesondere die automatische Aufteilung der Inhalte auf mehrere PDF-Seiten optimiert, 
damit zusammengehörige Testbereiche möglichst nicht unnötig voneinander getrennt werden.