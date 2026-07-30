# Projekt: stotz-design Browser-Startseite

**Ziel:** Minimalistische Browser-Startseite, selbst gehostet.

- Erreichbar unter `https://www.stotz-design.com/browserstartseite/index.html`
- Von Suchmaschinen nicht indexiert (`noindex, nofollow`)
- Farben: `#8db22f`, `#000000`, `#ffffff` – Font: "Open Sans", sans-serif
- Alle Elemente eckig, keine abgerundeten Ecken

**Hintergrund**

- Vollflächiges Hintergrundbild, proportional den ganzen Bildschirm ausfüllend:
  `https://www.stotz-design.com/wp-content/uploads/2020/10/Digital_Campagning_office.jpg`

**Layout**

- 3 gleich hohe Sektionen übereinander (je 1/3 Bildschirmhöhe), Inhalt jeweils vertikal zentriert:
  1. Kalender
  2. Google-Suche
  3. Favoriten
- Kalender und Suchleiste jeweils 600px breit

**Kalender**

- Zeigt aktuellen Monat, aktueller Tag grün hervorgehoben
- Mit Kalenderwochen (KW-Spalte, Mo–So)
- Hintergrund 60% Weiß (transparent), bei Hover Animation zu 100% Weiß
- Navigation: Pfeile links/rechts neben dem Kalender, nur bei Hover sichtbar, Monat vor/zurück begrenzt auf ±12 Monate

**Google-Suche**

- Suchleiste, sendet an `https://www.google.com/search`

**Favoriten**

Eigene Favoriten:

	- Reihe 1:
		- https://stotz-design.mocoapp.com/projects (MOCO)
		- https://stotz-design.cloud/index.php/apps/files/files/123?dir=/01-KUNDEN (SD CLOUD)
	
	- Reihe 2:
		- https://www.conmetallmeister.de/
		- https://www.textation-group.com/ (Textation Group)
		- https://karriere.textation-group.com/ (Textation Group: Karriereseite)
		- https://www.jumbo-textil.de/
		- https://vombaur.de/
		- https://roethel.com/
		- https://attelmann-architekten.de/
		- https://app.qr-code-generator.com/

Darstellung:

- Kacheln (Favicon-Quadrate): 90×90px, weiß, eckig
- Flacher Schatten unterm Quadrat (nicht dahinter), 75px breit, wirkt wie schwebend
- Hover: Kachel hebt sich 10px, Schatten wird kleiner/blasser
- Beschriftung unter jeder Kachel: schwarz, kein Textschatten
- Dezente 1px `#ccc`-Trennlinie zwischen Reihe 1 und Reihe 2

**Favoriten verwalten (im Browser)**

- Kleines `[+]`-Icon am Ende jeder Reihe → Popup mit Titel + URL zum Hinzufügen
- Hover-Menü (⋮, oben rechts an der Kachel) pro Favorit: Ändern / Löschen
- Alle Kacheln per Drag & Drop neu sortierbar (auch reihenübergreifend)
- Änderungen (hinzufügen/ändern/löschen/Reihenfolge) werden in `localStorage` gespeichert – bleiben im jeweiligen Browser erhalten, gelten aber nur lokal
- Button „Favoriten sichern“ lädt den aktuellen Stand als `favorites.json` herunter, zum manuellen Hochladen per FTP

**Favicons**

- MOCO, SD Cloud, QR Code Generator: feste Bild-URL des jeweiligen Original-Favicons
- Textation Karriere: gleiches Icon wie Textation Group
- Alle übrigen: Google-Favicon-Dienst (`google.com/s2/favicons?sz=64&domain=...`), mit Fallback auf Initialen-Badge falls ein Favicon nicht lädt
- Beim manuellen Hinzufügen über das Popup wird das Icon automatisch über den Google-Favicon-Dienst ermittelt

**Technik**

- Favoriten liegen in separater `favorites.json` (gleicher Ordner wie `index.html`), wird per `fetch()` geladen
- Ist `favorites.json` nicht ladbar, greift eine im HTML eingebettete Fallback-Liste
- `localStorage`-Stand hat Vorrang vor `favorites.json`, sobald einmal etwas über die Oberfläche geändert wurde
