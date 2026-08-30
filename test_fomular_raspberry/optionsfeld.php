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

    <h2>Optionsfeld</h2>

 <label for="farbe">Wähle eine Farbe:</label>

<select id="farbe" name="farbe">
    <option value="rot">Rot</option>
    <option value="blau">Blau</option>
    <option value="gruen">Grün</option>
    <option value="gelb">Gelb</option>
</select>

    <button type="button" class="zurueck"
            onclick="window.location.href='index.html'">
        Zurück zur Startseite
    </button>

</div>

</body>
</html>