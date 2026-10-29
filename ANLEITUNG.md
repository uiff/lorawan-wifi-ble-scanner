# Bau- & Bedienungsanleitung: 3-in-1 LoRaWAN / WiFi / BLE Finder (Rev. 5 – 2-Farben-Edition)

**Projekt, Firmware & IoT-Lösungen auf [www.iotueli.ch](https://www.iotueli.ch)**  
**Druckfertiges PDF-Handbuch (4 Seiten A4):** [`Bauanleitung_LoRaWAN_Finder.pdf`](file:///c:/Users/uiff/Documents/coding/ESP_LoraWan_Finder/Bauanleitung_LoRaWAN_Finder.pdf)

---

## 1. Gehäuse-Übersicht (Rev. 5 mit Zweifarb-Logo & Kabel-Durchgang)

| Draufsicht (2-Farben-Deckel) | Fertig montiertes Gerät | Explosionszeichnung |
| :---: | :---: | :---: |
| ![Draufsicht Rev. 5](docs/anleitung/img/top_check_v5.png) | ![Gesamtansicht](docs/anleitung/img/01_gesamt.png) | ![Explosionsansicht](docs/anleitung/img/02_explosion.png) |
| **Abb. 1:** Deckel mit bündigem **IoTUeli-Logo** & Tasten-Symbolen (`66 × 86 × 23.2 mm`) | **Abb. 2:** Fertig montierter 3-in-1 Finder mit 868-MHz-SMA-Antenne | **Abb. 3:** Explosionsansicht aller Baugruppen & 3D-Druckteile |

### Wichtigste Neuerungen im Gehäuse Rev. 5:
1. **Zweifarbiger Deckel für Bambu Studio (AMS):** Oberhalb des OLED-Displays ist das **IoTUeli-Logo** (`42 mm` breit) zusammen mit den Tasten-Symbolen (`‹  ●  ›`) als `0.60 mm` tiefes, bündiges Zweifarb-Inlay integriert.
2. **Freier Raum über den ESP32-Lötstellen im Deckel:** Auf der Innenseite des Deckels wurden die Kunststoff-Stege über den ESP32-Stiftleisten entfernt (`5.4 mm` freier Raum nach oben), sodass von oben angelötete Drähte nirgends anstoßen.
3. **26 mm breiter Kabel-Durchgang unter dem ESP32:** Im Unterteil (`Gehaeuse_Unten`) befindet sich mittig ein durchgehender `26 mm` breiter Durchgang, durch den die Drähte direkt unter dem ESP32 zu den 3 Tastern und nach oben geführt werden können.
4. **Vergrößertes Antennenfach (+8 mm) & Koax-Tunnel:** Das Gehäuse wurde im oberen Bereich um `+8 mm` auf `66 × 86 × 23.2 mm` erweitert und mit einem abgesetzten Koax-Tunnel vor der SMA-Buchse versehen, damit die SMA-Einbaubuchse und das U.FL-Antennenkabel spannungsfrei Platz finden.

---

## 2. Stückliste (BOM) & 3D-Druckdateien

### Benötigte Hardware-Komponenten
| Anz. | Bauteil | Details / Einbaumaße |
| :---: | :--- | :--- |
| **1×** | **Heltec WiFi LoRa 32 V2** | ESP32 (WiFi + BLE) + SX1276 (868 MHz) + 0.96" OLED (`52.0 × 25.33 mm`) |
| **1×** | **SMA-Buchse + Antenne** | U.FL/IPEX auf SMA-Einbaubuchse (`18 mm` Innentiefe) + 868 MHz Antenne |
| **3×** | **Kurzhubtaster 6×6 mm** | 4-Pin Taster, Körper `6 × 6 × 2.9 mm` + Knopf `Ø 3.5 × 1.5 mm` (`4.4 mm` Gesamthöhe) |
| **4×** | **M3 Einschmelzgewinde** | `Ø 4.0 mm` Außendurchmesser, Länge `4–6 mm` (Sackloch `7 mm` tief) |
| **4×** | **M3 × 8 mm Schrauben** | Zylinderkopf / Innensechskant (bündig versenkt im Gehäusedeckel) |
| **1×** | **1S LiPo-Akku + Schalter** | Optional: 3.7 V LiPo (JST 1.25 mm) + Mini-Schiebeschalter SS12D00 |

### 3D-Druckdateien (in [`cad/export/`](file:///c:/Users/uiff/Documents/coding/ESP_LoraWan_Finder/cad/export))
| Datei | Beschreibung & Farbzuweisung |
| :--- | :--- |
| [`LoraWanFinder_BambuLab_Platte.3mf`](file:///c:/Users/uiff/Documents/coding/ESP_LoraWan_Finder/cad/export/LoraWanFinder_BambuLab_Platte.3mf) | **Zweifarbige Bambu-Studio-Platte** (alle Teile druckfertig orientiert, 0 % Stützstruktur, Extruder 1 & 2 vorkonfiguriert) |
| [`Gehaeuse_Unten.stl`](file:///c:/Users/uiff/Documents/coding/ESP_LoraWan_Finder/cad/export/Gehaeuse_Unten.stl) | **Farbe 1:** Unterteil mit `26 mm` Kabel-Durchgang & vergrößertem Antennenraum |
| [`Gehaeuse_Oben.stl`](file:///c:/Users/uiff/Documents/coding/ESP_LoraWan_Finder/cad/export/Gehaeuse_Oben.stl) | **Farbe 1:** Deckel-Hauptkörper (ohne störende Innenstege über den Pins) |
| [`Logo_und_Tasten_Farbe2.stl`](file:///c:/Users/uiff/Documents/coding/ESP_LoraWan_Finder/cad/export/Logo_und_Tasten_Farbe2.stl) | **Farbe 2:** Bündiges `0.60 mm` Inlay für **IoTUeli-Logo** & Tasten-Symbole `‹  ●  ›` |
| [`Taster_Kappe.stl`](file:///c:/Users/uiff/Documents/coding/ESP_LoraWan_Finder/cad/export/Taster_Kappe.stl) | **Farbe 2:** `3×` drucken – Unterseite 100 % flach/bündig für vollen Tastenhub |

> [!TIP]
> **Zweifarbiger Druck in Bambu Studio (AMS):** Öffne einfach [`LoraWanFinder_BambuLab_Platte.3mf`](file:///c:/Users/uiff/Documents/coding/ESP_LoraWan_Finder/cad/export/LoraWanFinder_BambuLab_Platte.3mf). Der Deckel (`Gehaeuse_Oben`) liegt mit der Sichtseite nach unten auf dem Druckbett und besteht bereits aus zwei Teilkörpern: `Deckel_Hauptkoerper` (**Filament 1**, z. B. Anthrazit/Schwarz) und `IoTUeli_Logo_und_Tasten` (**Filament 2**, z. B. Cyan/Weiß). Da das Inlay exakt `0.60 mm` hoch ist (3 Schichten à `0.20 mm`), sind nur in den ersten 3 Schichten Farbwechsel nötig – komplett ohne Stützstruktur (**Support: AUS**).

---

## 3. Elektrisches Anschluss-Schema & Taster-Pinbelegung (4-Pin Taster)

### Welche der 4 Taster-Pins werden benötigt?

Ein quadratischer `6 × 6 mm` Kurzhubtaster besitzt **4 Beinchen (Pins)**, wovon pro Taster **nur 2 Pins benötigt** werden:

```
       ANSCHLUSS: GND                              FREI LASSEN
              │                                          │
              ▼                                          ▼
          ┌───────┐  ┌────────────────────────────┐  ┌───────┐
          │ PIN 1 ├──┤  Intern verbunden (1 ↔ 2)  ├──┤ PIN 2 │
          └───────┘  │                            │  └───────┘
                     │         ╭────────╮         │
                     │         │ TASTER │         │
                     │         ╰────────╯         │
          ┌───────┐  │                            │  ┌───────┐
          │ PIN 3 ├──┤  Intern verbunden (3 ↔ 4)  ├──┤ PIN 4 │
          └───────┘  └────────────────────────────┘  └───────┘
              ▲                                          ▲
              │                                          │
         FREI LASSEN                              GPIO 12 / 13 / 32
```

* **Warum hat der Taster 4 Beinchen?** Im Inneren des Tasters sind jeweils **zwei gegenüberliegende Beinchen dauerhaft miteinander verbunden** (`Pin 1 ↔ Pin 2` oben und `Pin 3 ↔ Pin 4` unten). Erst beim Drücken des Knopfes werden die obere und untere Schiene verbunden.
* **Welche Pins werden angeschlossen?** Du benötigst pro Taster **nur 2 Pins**. Die anderen **2 Pins (`Pin 2` und `Pin 3`) bleiben einfach frei**.
* **Der 100 %-sichere Diagonal-Trick:** Löte die zwei Drähte immer an **zwei diagonal gegenüberliegende Beinchen**:
  * **Pin 1 (oben links)** -> **`GND`** (gemeinsame Masse für alle 3 Taster)
  * **Pin 4 (unten rechts)** -> **`GPIO 12`** (Taster Links `‹`), **`GPIO 13`** (Taster Mitte `●`), **`GPIO 32`** (Taster Rechts `›`)
  * *Vorteil:* Bei diagonalem Anschluss funktioniert der Taster garantiert immer – selbst wenn er um 90° gedreht eingesetzt wurde.

---

## 4. Schritt-für-Schritt Montageanleitung

1. **Schritt 1 – Gehäuse-Unterteil vorbereiten:**
   * Die **4× M3-Einschmelzgewinde (`Ø 4.0 mm`)** mit dem Lötkolben (`200–210 °C`) bündig in die vier Eck-Dome des Unterteils (`Gehaeuse_Unten`) einschmelzen.
2. **Schritt 2 – Taster, SMA-Antenne & optionale Stromversorgung:**
   * Die **3× 6×6 mm Taster** von oben in die drei quadratischen Aufnahmen drücken und diagonal an **Pin 1 (`GND`)** sowie **Pin 4 (`GPIO 12`, `GPIO 13`, `GPIO 32`)** verdrahten.
   * Die **SMA-Einbaubuchse** von innen durch die Rückwand stecken (verdrehsicherer Sechskant + ausgesparter Koax-Tunnel) und außen festziehen.
3. **Schritt 3 – Heltec WiFi LoRa 32 V2 einlegen:**
   * Die angelöteten Drähte in den **26 mm breiten Durchgang unter dem ESP32** legen.
   * Den goldenen **U.FL/IPEX-Antennenstecker** auf die Buchse des Heltec V2 klipsen und die Platine in die Halterung legen (Micro-USB schließt links bündig ab).
4. **Schritt 4 – Tasterkappen & Zweifarb-Deckel verschrauben:**
   * Die 3 gedruckten **Tasterkappen** (`Taster_Kappe.stl`) von innen in den Deckel (`Gehaeuse_Oben`) einsetzen, Deckel aufsetzen und mit **4× M3 × 8 mm Schrauben** verschrauben.

---

## 5. Gebrauchserklärung & Bedienungsanleitung (3-in-1 Firmware)

Nach dem Einschalten zeigt das Gerät für 2.5 Sekunden das **IoTUeli.ch**-Startlogo. Danach steuerst du alle **5 Seiten** mit den **3 Tastern** (ohne komplizierten Langdruck):

| Taster | Symbol am Deckel | GPIO | Funktion (auf allen 5 Seiten identisch!) |
| :--- | :---: | :---: | :--- |
| **Taster LINKS** | `[ ‹ ]` | `GPIO 12` | **Eine Seite zurückblättern** (`1/5` -> `5/5` -> `4/5` -> `3/5` -> `2/5` -> `1/5`) |
| **Taster RECHTS** | `[ › ]` | `GPIO 32` | **Eine Seite weiterblättern** (`1/5` -> `2/5` -> `3/5` -> `4/5` -> `5/5`) |
| **Taster MITTE** | `[ ● ]` | `GPIO 13` | **Aktion starten:** Führt immer genau den Befehl aus, der **unten in der Mitte in `[...]`** steht. |

### Die 5 Bildschirm-Seiten im Überblick

| Seite | Titel auf dem OLED | Was wird angezeigt? | Aktion mit Taste MITTE `[ ● ]` |
| :---: | :--- | :--- | :--- |
| **1/5** | `1/5 LORA-CHECK` | **Letztes echtes 868 MHz LoRa-Paket in Prozent (`0–100 %`)**, **`dBm`** und Alter (`vor 2s`) inkl. Urteil (`RUHE`, `SCHWACH`, `GUT (OK)`, `SEHR GUT!`) | `[NEU MESSEN]`: Startet eine 3-Sekunden-Messung über alle Hauptkanäle |
| **2/5** | `2/5 LORA (n)` | **Liste von bis zu 10 gefundenen LoRaWAN-Netzen & Sendern** anhand von `DevAddr` / `DevEUI` (`SWISSCOM`, `TTN/DRAG`, `DRAGINO`, `HELIUM`, `LORIOT`, `PRIVAT`) + `dBm` & `%` | `[NAECHSTES LORA]`: Blättert durch alle empfangenen LoRaWAN-Netze/Sender |
| **3/5** | `3/5 LORA-TEST` | **Aktiver Gateway-Sende-Test** für dein eigenes Dragino- oder TTN-Gateway | `[SENDEN!]`: Sendet 3 LoRaWAN-Testpakete (Adresse `2601CAFE`) auf `868.1 / 868.3 / 868.5 MHz` und horcht auf Gateway-Antwort |
| **4/5** | `4/5 WIFI (n)` | **2.4 GHz WLAN-Scanner:** Anzahl gefundener WLANs, WLAN-Name (SSID) & Signalbewertung in `%` | `[NAECHSTES WLAN]`: Blättert durch alle WLANs (`1:`, `2:`, `3:` …) und scannt am Ende neu |
| **5/5** | `5/5 BLE (n)` | **Bluetooth-BLE-Scanner:** Anzahl aktiver BLE-Geräte, Gerätename bzw. MAC-Adresse & Signalbewertung | `[NAECHSTES BLE]`: Blättert durch alle BLE-Geräte und scannt am Ende neu |

### Signal-Bewertung & Praxis-Tipp für Dragino / Swisscom LoRaWAN

| Anzeige-Urteil | LoRa 868 MHz | WLAN / BLE | Bedeutung für den Einsatz |
| :--- | :--- | :--- | :--- |
| **`SEHR GUT!`** | ab `-75 dBm` (`65–100 %`) | ab `-67 dBm` | **Optimal:** Minimaler Batterieverbrauch (`SF7`), hohe Reserve. |
| **`GUT (OK)`** | `-76 .. -100 dBm` (`20–65 %`) | `-68 .. -78 dBm` | **Ausreichend:** Zuverlässiger Normalbetrieb im Gebäude/Freien. |
| **`SCHWACH`** | `-101 .. -115 dBm` (`5–20 %`) | `-79 .. -88 dBm` | **Knapp:** LoRa klappt nur mit `SF10–SF12`; Antenne besser positionieren. |
| **`RUHE / 0%`** | unter `-115 dBm` (`0 %`) | – | Aktuell sendet kein Gerät (normales Grundrauschen). |
