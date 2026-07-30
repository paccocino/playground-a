# Projekt: stotz-design Browser-Startseite

**Ziel:** Minimalistische Browser-Startseite, selbst gehostet.

- Erreichbar unter `https://www.stotz-design.com/browserstartseite/index.html`
- Von Suchmaschinen nicht indexiert (`noindex, nofollow`)
- Farben: `#8db22f`, `#000000`, `#ffffff` – Font: "Open Sans", sans-serif
- Alle Elemente eckig, keine abgerundeten Ecken

**Hintergrund**

- Vollflächiges Hintergrundbild, proportional den ganzen Bildschirm ausfüllend:
  `https://www.stotz-design.com/wp-content/uploads/2020/10/Digital_Campagning_office.jpg`

**Google-Suche**

- Suchleiste oben, sendet an `https://www.google.com/search`

**Favoriten**

- Reihe 1: MOCO (`https://stotz-design.mocoapp.com/projects`), SD CLOUD (`https://stotz-design.cloud/index.php/apps/files/files/123?dir=/01-KUNDEN`)
- Reihe 2: Conmetallmeister, Textation Group, Textation Karriere, Jumbo-Textil, vombaur, Röthel, Attelmann Architekten
- Dezente 1px `#ccc`-Trennlinie zwischen Reihe 1 und Reihe 2
- Favoriten-Block als Ganzes ca. 150px über dem unteren Bildschirmrand fixiert
- Container-Breite max. 1200px
- Kacheln (Favicon-Quadrate): 90×90px, weiß, eckig
- Flacher Schatten unterm Quadrat (nicht dahinter), 75px breit, wirkt wie schwebend
- Hover: Kachel hebt sich 10px, Schatten wird kleiner/blasser
- Beschriftung unter jeder Kachel: schwarz, kein Textschatten

**Favicons**

- MOCO und SD Cloud: feste Bild-URL der jeweiligen Original-Favicons
- Textation Karriere: gleiches Icon wie Textation Group
- Alle übrigen: Google-Favicon-Dienst (`google.com/s2/favicons?sz=64&domain=...`), mit Fallback auf Initialen-Badge falls ein Favicon nicht lädt

**Bonus – eigene Favoriten pflegen**

- Favoriten liegen in separater `favorites.json` (gleicher Ordner wie `index.html`)
- Neuer Eintrag = `{ "name": "...", "url": "...", "icon": "..." }` in die passende Zeile/Reihe einfügen
- Falls `favorites.json` nicht ladbar ist, greift eine im HTML eingebettete Fallback-Liste
