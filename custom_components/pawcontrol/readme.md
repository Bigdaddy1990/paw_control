# Paw Control

**Die modulare Home Assistant Integration für Hunde(-Haushalte) mit Gassi, Gesundheit, GPS, Push und automatisch generierbarem Dashboard.**

---

## Features

- **Modular:** Wähle bei der Einrichtung, welche Funktionen du nutzen möchtest (Gassi, GPS, Push, Health, Dashboard).
- **Opt-in/Opt-out:** Jedes Modul ist jederzeit aktivierbar oder abschaltbar (auch nach dem Setup über Optionen).
- **Helper, Sensoren und Automationen werden automatisch bei Aktivierung erzeugt oder bei Deaktivierung entfernt.**
- **Fehlerresistent:** Kein Modul und kein Helper verschwindet durch Updates.
- **Blueprints & Mushroom-Karten für Lovelace direkt dabei.**
- **Optional: Automatisch generiertes Dashboard als YAML (Sensor).**

---

## Installation

1. Entpacke `custom_components/pawcontrol` in dein Home Assistant `custom_components`-Verzeichnis.
2. Starte Home Assistant neu.
3. Füge die Integration über die UI hinzu („Paw Control“).
4. Wähle bei der Einrichtung aus, welche Module du nutzen möchtest.
5. Später kannst du über die Optionen der Integration jedes Modul aktivieren/deaktivieren.

---

## Beispielkarten (für Lovelace/Mushroom)

Kopiere diese YAML direkt in dein Dashboard:

### Letztes Gassi

```yaml
type: custom:mushroom-entity-card
entity: sensor.hund1_last_walk
name: Letztes Gassi
icon: mdi:walk
