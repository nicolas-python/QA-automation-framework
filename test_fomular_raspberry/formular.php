<!-- PHP = serverseitige Programmiersprache
PHP-Code wird auf dem Webserver ausgeführt bevor die Antwort an den Browser gesendet wird
Die Datei verwendet deshalb die Endung .php, da sie auf dem Raspberry Pi über einen PHP-fähigen Webserver ausgeführt wird -->


<!-- HTML → beschreibt den Inhalt und Aufbau der Webseite -->
<!-- CSS  → beschreibt das Aussehen -->
<!-- PHP  → wird auf dem Server ausgeführt und kann Daten verarbeiten -->

<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kontaktformular</title>

    <link rel="stylesheet" href="formular_style.css">
</head>

<body>

<!-- Formular-Testbereich für den QA-Automation-Tester -->
<div class="formular">

    <h2>Kontaktformular</h2>

    <form action="#" method="post">

        <!-- Pflichtfeld: Name -->
        <label for="name">Name *</label>                        <!-- * und required = Pflichtfeld -->
        <input type="text" id="name" name="name"
               placeholder="Vor- und Nachname" required>        <!-- required = Feld muss vor dem Absenden ausgefüllt werden -->

        <!-- Pflichtfeld: Adresse -->
        <label for="adresse">Adresse *</label>
        <input type="text" id="adresse" name="adresse"
               placeholder="Straße und Hausnummer" required>

        <!-- Pflichtfeld: PLZ -->
        <label for="plz">PLZ *</label>
        <input type="text" id="plz" name="plz"
               placeholder="z. B. 71032" required>

        <!-- Pflichtfeld: Ort -->
        <label for="ort">Ort *</label>
        <input type="text" id="ort" name="ort"
               placeholder="Ort" required>

        <!-- TeleNummer -->
        <label for="telefon">Telefonnummer</label>
        <input type="tel" id="telefon" name="telefon"
               placeholder="z. B. 0711 123456">

        <!-- Pflichtfeld: Email -->
        <label for="email">E-Mail-Adresse *</label>
        <input type="email" id="email" name="email"
               placeholder="name@beispiel.de" required>

        <!-- Pflichtfeld: Betreff  -->
        <label for="betreff">Betreff *</label>
        <input type="text" id="betreff" name="betreff"
               placeholder="Betreff eingeben" required>

        <!-- Pflichtfeld: Nachricht -->
        <label for="nachricht">Nachricht *</label>
        <textarea id="nachricht" name="nachricht"
                  placeholder="Ihre Nachricht..." required></textarea>

        <button type="submit">Nachricht senden</button>

    </form>

    <button type="button" class="zurueck"
            onclick="window.location.href='index.html'">
        Zurück zur Startseite
    </button>

</div>

</body>
</html>