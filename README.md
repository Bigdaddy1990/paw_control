# 🐕 Paw Control - Die ultimative Home Assistant Integration für Hundebesitzer

<div align="center">

[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/BigDaddy1990/paw_control.svg?style=for-the-badge)](https://github.com/BigDaddy1990/paw_control/releases)
[![License](https://img.shields.io/github/license/BigDaddy1990/paw_control.svg?style=for-the-badge)](LICENSE)
[![Downloads](https://img.shields.io/github/downloads/BigDaddy1990/paw_control/total.svg?style=for-the-badge)](https://github.com/BigDaddy1990/paw_control/releases)

**🐶 Die smarteste Home Assistant Integration für Hundebesitzer**

Verwalten Sie Fütterung, GPS-Tracking, Gesundheit und Training Ihres Hundes - alles in einer Integration!

[🚀 Installation](#-installation) •
[✨ Features](#-features) •
[📖 Dokumentation](#-dokumentation) •
[🤝 Community](#-community) •
[💝 Unterstützung](#-unterstützung)

[![Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/bigdaddy1990)
</div>

---

## 🎯 **Was ist Paw Control?**

**Paw Control** ist die **erste umfassende** Home Assistant Integration für Hundebesitzer mit modernster GPS-Technologie. Mit über **100 automatisch erstellten Entities**, **25+ Services** und **intelligentente Automatisierungen** haben Sie die komplette Kontrolle über das Wohlbefinden Ihres vierbeinigen Freundes.

### 🏆 **Warum Paw Control wählen?**

<table>
<tr>
<td align="center">
<strong>🔒 100% Lokal</strong><br>
Keine Cloud, alle Daten bleiben bei Ihnen
</td>
<td align="center">
<strong>🛰️ GPS-Tracking</strong><br>
Automatische Spaziergang-Erkennung
</td>
<td align="center">
<strong>⚡ Plug & Play</strong><br>
Ein-Klick Installation via HACS
</td>
<td align="center">
<strong>🎯 Komplett</strong><br>
Alles was Sie brauchen in einer Integration
</td>
</tr>
</table>

---

## ✨ **Features**

### 🛰️ **Intelligentes GPS-Tracking**
- 🗺️ **Automatische Spaziergang-Erkennung** basierend auf GPS-Position
- 📏 **Live-Distanz & Geschwindigkeit** Messung während Spaziergängen
- 🎯 **Geofencing** mit konfigurierbaren Sicherheitszonen
- 📱 **Kompatibel mit GPS-Trackern** (Tractive, Smartphone, DIY)
- 🏠 **Automatisches Start/Stop** beim Verlassen/Betreten der Wohnzone

### 🍽️ **Intelligentes Fütterungsmanagement**
- ⏰ **Automatische Erinnerungen** für alle Mahlzeiten
- 📊 **Futtermenge-Tracking** mit verschiedenen Futterarten
- 🏆 **Fütterungsstreaks** zur Motivation
- 📈 **Gewichtsverlauf** mit grafischen Darstellungen
- 🥗 **Allergie-Management** und Futterpräferenzen

### 🏥 **Umfassende Gesundheitsüberwachung**
- ⚖️ **Gewichtsverlauf** mit Trend-Analyse
- 🌡️ **Vitalwerte-Monitoring** (Temperatur, Puls)
- 💊 **Medikamenten-Tracker** mit Erinnerungen
- 💉 **Impfkalender** mit automatischen Benachrichtigungen
- 🏥 **Tierarzttermine** und Gesundheitshistorie

### 🎾 **Training & Aktivitäten**
- 🎓 **Trainingsessions** mit Fortschritts-Tracking
- ⭐ **Bewertungssystem** für alle Aktivitäten
- 🎮 **Spielzeit-Management** mit verschiedenen Spielarten
- 📊 **Aktivitätslevel-Monitoring** mit GPS-basierten Empfehlungen
- 🏃 **Kalorienverbrauch** basierend auf GPS-Daten

### 🤖 **Intelligente Automatisierung**
- 🔔 **GPS-basierte Benachrichtigungen** (Hund verlässt Zone, kommt nach Hause)
- 📅 **Automatische Terminplanung** basierend auf Aktivitätsmustern
- 🌤️ **Wetter-Integration** für optimale Spaziergang-Zeiten
- 👥 **Besuchermodus** für Hundesitter mit GPS-Freigabe
- 🚨 **Notfall-Modus** mit sofortiger GPS-Lokalisierung

---

## 🚀 **Installation**

### **Methode 1: HACS (Empfohlen) ⭐**

1. **HACS öffnen** in Home Assistant
2. **Integrationen** → **⋮** → **Benutzerdefinierte Repositories**
3. **Repository hinzufügen**:
   ```
   URL: https://github.com/BigDaddy1990/paw_control
   Kategorie: Integration
   ```
4. **"Paw Control"** suchen und **installieren**
5. **Home Assistant neu starten**
6. **Integration hinzufügen**: `Einstellungen` → `Geräte & Dienste` → `Integration hinzufügen` → `"Paw Control"`

---

## 💝 **Unterstützung**

### **🦴 Spenden Sie Hundekekse! 🦴**

Paw Control ist kostenlos und Open Source. Wenn es Ihnen und Ihrem Hund hilft, freuen wir uns über Ihre Unterstützung!

<div align="center">

[![Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/bigdaddy1990)

**🏠 Spenden Sie eine Hundehütte oder ein Paket Hundekekse! 🍪**

*Ihre Spende hilft bei der Entwicklung neuer Features und der Wartung des Projekts*

💝 **Was Ihre Spende bewirkt:**
- 🚀 Neue GPS-Tracker Integrationen
- 📱 Mobile App Entwicklung
- 🤖 KI-basierte Gesundheitsempfehlungen
- 🌍 Weitere Sprachen und Länder
- 🔧 24/7 Support und Updates

</div>

---

## ❓ **FAQ**

<details>
<summary><strong>🛰️ Funktioniert es mit meinem GPS-Tracker?</strong></summary>

Ja! Paw Control unterstützt **alle GPS-Quellen**:
- **Smartphone** mit Home Assistant App (empfohlen für Besitzer)
- **Tractive** GPS-Collar (Native HA-Integration)
- **Webhooks** für beliebige GPS-Tracker
- **MQTT** für IoT-Geräte
- **DIY-Tracker** (ESP32, Arduino)

</details>

<details>
<summary><strong>🏠 Wie funktioniert die automatische Spaziergang-Erkennung?</strong></summary>

Paw Control überwacht kontinuierlich die GPS-Position:
- **Start**: Automatisch wenn Hund >100m von Zuhause entfernt
- **Tracking**: Live-Route, Distanz, Geschwindigkeit
- **Ende**: Automatisch bei Rückkehr in die Sicherheitszone
- **Statistiken**: Sofortige Berechnung von Dauer, Distanz, Kalorien

Alles ohne manuelles Starten/Stoppen!

</details>

<details>
<summary><strong>🔋 Wie lange hält der Akku meines GPS-Trackers?</strong></summary>

Paw Control überwacht automatisch den **Akku-Status** Ihres GPS-Trackers:
- **Live-Monitoring** des Akku-Levels
- **Automatische Warnungen** bei niedrigem Akku
- **Energiespar-Modi** wenn aktiviert
- **Akku-Trends** zur optimalen Lade-Planung

Typische Laufzeiten: Tractive (3-5 Tage), Smartphone (ganzer Tag)

</details>

<details>
<summary><strong>📱 Brauche ich eine separate App?</strong></summary>

**Nein!** Alles funktioniert direkt in Home Assistant:
- **Web-Dashboard** für Desktop und Mobile
- **Home Assistant App** für unterwegs

Keine zusätzlichen Apps oder Accounts erforderlich!

</details>

<details>
<summary><strong>🐕 Kann ich mehrere Hunde verwalten?</strong></summary>

Ja! Paw Control unterstützt **unbegrenzt viele Hunde**:
- Jeder Hund hat seine **eigenen Entities** und **GPS-Tracking**
- **Getrennte Dashboards** für jeden Hund
- **Vergleichs-Statistiken** zwischen den Hunden
- **Familienansicht** mit allen Hunden auf einer Seite

</details>

---

## 📞 **Kontakt & Support**

### **🆘 Probleme oder Fragen?**

1. **📖 Dokumentation** - Prüfen Sie zuerst unsere [ausführliche Dokumentation](docs/)
2. **🔍 FAQ** - Schauen Sie in die häufig gestellten Fragen (siehe oben)
3. **🐛 GitHub Issues** - [Melden Sie Bugs oder Probleme](https://github.com/BigDaddy1990/paw_control/issues)
4. **💬 Community** - [Diskutieren Sie mit anderen Nutzern](https://github.com/BigDaddy1990/paw_control/discussions)

## 🤝 **Community**

### **💬 Support & Diskussion**

- 🐛 **[Bug Reports](https://github.com/BigDaddy1990/paw_control/issues)** - Fehler melden
- 💡 **[Feature Requests](https://github.com/BigDaddy1990/paw_control/discussions)** - Neue Ideen vorschlagen
- ❓ **[Q&A Forum](https://github.com/BigDaddy1990/paw_control/discussions/categories/q-a)** - Fragen stellen
- 📢 **[Ankündigungen](https://github.com/BigDaddy1990/paw_control/discussions/categories/announcements)** - Neuigkeiten erfahren


### **🤝 Mitmachen**

Möchten Sie beitragen? Großartig! Siehe unseren **[Contributing Guide](CONTRIBUTING.md)** für Details.

**Was Sie beitragen können:**
- 🐛 **Bug Fixes** - Helfen Sie dabei, Fehler zu finden und zu beheben
- ✨ **GPS-Features** - Neue GPS-Tracker Integrationen entwickeln
- 📖 **Dokumentation** - Verbessern Sie Guides und Tutorials
- 🌍 **Übersetzungen** - Helfen Sie bei der Internationalisierung
- 🧪 **Testing** - Testen Sie neue Features und geben Sie Feedback

---

## 📄 **Lizenz**

```
MIT License

Copyright (c) 2025 Paw Control Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

**[📜 Vollständige Lizenz ansehen](LICENSE)**

---

<div align="center">

## 🐶 **Made with ❤️ for Dog Lovers**

**Paw Control** - *Weil jeder Hund das Beste verdient hat!*

[![Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/bigdaddy1990)

*🦴 Spenden Sie Hundekekse für die Entwicklung! 🦴*

---

[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/BigDaddy1990/paw_control.svg?style=for-the-badge)](https://github.com/BigDaddy1990/paw_control/releases)
[![License](https://img.shields.io/github/license/BigDaddy1990/paw_control.svg?style=for-the-badge)](LICENSE)

**⭐ Geben Sie uns einen Stern, wenn Ihnen Paw Control gefällt! ⭐**

</div>
