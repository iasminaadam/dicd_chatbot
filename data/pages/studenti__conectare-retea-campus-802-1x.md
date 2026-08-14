---
title: "Conectare rețea campus 802.1X"
url: "https://dicd.tuiasi.ro/ro/studenti/conectare-retea-campus-802-1x/"
---

# Conectare rețea campus 802.1X

Dacă întâmpinați probleme la realizarea conexiunii sau alte probleme de natură fizică (priză defectă, cablu defect), puteți deschide un tichet prin intermediul **[sistemului de tichete](https://www.support.campus.tuiasi.ro/)**.

Pentru conectare, fiecare student va folosi **contul personal instituțional** (cel utilizat pentru accesul la Gmail, Meet, Teams etc.) și parola aferentă acestuia.
Pentru prima utilizare, trebuie să creăm o conexiune de tip 802.1X. La viitoarele conectări nu va mai fi nevoie să repetați pașii de creare a conexiunii, deoarece veți putea folosi conexiunea creată inițial.

## Creare conexiune de tip 802.1X

### (Pentru WINDOWS 10) Verificați dacă pe computer rulează un serviciu numit „Wired AutoConfig”

Pasul 1: Faceți click dreapta pe **Start**, apoi faceți click pe elementul **Computer** **Management**. (Fig. 1)

Pasul 2: Alegeți **Servicii și aplicații** -> **Servicii**. (Fig. 2)

Pasul 3: Găsiți elementul **Wired AutoConfig**. (Fig. 3)

Pasul 4: Faceți click dreapta pe serviciul **Wired AutoConfig** și selectați **Proprietăți.** Setați Tip de pornire: **Automat**. Puteți porni serviciul imediat din această fereastră apăsând Start (cu excepția cazului în care rulează deja). (Fig. 4)

Pasul 5: Închideți caseta de dialog apăsând OK. (Fig. 5)

**După verificarea funcționării acestui serviciu continuați cu pașii din secțiunea „Windows”.**

- ![Fig.1 Computer-Management](https://dicd.tuiasi.ro/wp-content/uploads/2025/07/VirtualBox_windows-10_17_07_2025_14_21_31.png)

  Fig.1 Computer-Management
- ![Fig.2 Servicii-si-aplicatii-Servicii](https://dicd.tuiasi.ro/wp-content/uploads/2025/07/Servicii-si-aplicatii-Servicii.png)

  Fig.2 Servicii-si-aplicatii-Servicii
- ![Fig. 3 Wired-AutoConfig-Properties](https://dicd.tuiasi.ro/wp-content/uploads/2025/07/Wired-AutoConfig-Properties-1024x485.png)

  Fig. 3 Wired-AutoConfig-Properties
- ![Fig 4. Wired-AutoConfig-Automatic](https://dicd.tuiasi.ro/wp-content/uploads/2025/07/Wired-AutoConfig-Automatic-1024x484.png)

  Fig 4. Wired-AutoConfig-Automatic
- ![Fig. 5 Wired-AutoConfig-OK-Settings](https://dicd.tuiasi.ro/wp-content/uploads/2025/07/Wired-AutoConfig-OK-Settings-1024x485.png)

  Fig. 5 Wired-AutoConfig-OK-Settings

### Windows

Pentru a realiza **Pasul 1**, presupunem ca aveți conexiunea la internet prin alte mijloace (WIFI, LTE, HotSpot etc.). Alternativ, puteți transfera programul de instalare pe dispozitiv folosind un stick USB.

**Pasul 1: Accesați site-ul de configurare Eduroam**. Deschideți un browser și accesați cat.eduroam.org. Selectați „Gheorghe Asachi” Technical University of Iași, apoi din lista alegeți ‘campus-wired’. (Fig. 1), (Fig. 2),(Fig. 3).

**Pasul 2:** **Descărcați programul de configurare**. Apăsați pe butonul ‘eduroam®’ pentru a descărca installer-ul pentru Windows. După descărcare, fișierul ar trebui să apară în folderul Downloads. (Fig. 4).

**Pasul 3: Rulați programul de configurare**. Deschideți fișierul descărcat cu dublu-click. Dacă apare un mesaj ca în imagine, confirmați prin tasta ‘Yes’ pentru a configura accesul pe interfața cablată. (Fig. 5).

**Pasul 4: Urmați pașii installer-ului**. Introduceți datele dumneavoastră de autentificare când se cer (adresa de e-mail instituțională TUIASI și parola contului). După configurare conexiunea ar trebui să fie funcțională. (Fig. 6), (Fig. 7), (Fig. 8), (Fig. 9).

- ![Fig. 1 cat.eduroam.org](https://dicd.tuiasi.ro/wp-content/uploads/2025/07/cat.eduroam.org_-1024x505.png)

  Fig. 1 cat.eduroam.org
- ![Fig. 2 Selectare-Universitate](https://dicd.tuiasi.ro/wp-content/uploads/2025/07/Selectare-Universitate.png)

  Fig. 2 Selectare-Universitate
- ![Fig. 3 Site-Eduroam](https://dicd.tuiasi.ro/wp-content/uploads/2025/07/Site-Eduroam-1024x733.png)

  Fig. 3 Site-Eduroam
- ![Fig. 4 Descarcare-Aplicatie](https://dicd.tuiasi.ro/wp-content/uploads/2025/07/descarcare-aplicatie-1024x209.png)

  Fig. 4 Descarcare-Aplicatie
- ![Fig. 5 Rulare-Progam](https://dicd.tuiasi.ro/wp-content/uploads/2025/07/Rulare-progam-1-1024x577.png)

  Fig. 5 Rulare-Progam
- ![Fig. 6 Installer](https://dicd.tuiasi.ro/wp-content/uploads/2025/07/F6-Installer.png)

  Fig. 6 Installer
- ![Fig. 7 Installer](https://dicd.tuiasi.ro/wp-content/uploads/2025/07/F7-Installer.png)

  Fig. 7 Installer
- ![Fig. 8 Installer](https://dicd.tuiasi.ro/wp-content/uploads/2025/07/F8-Installer.png)

  Fig. 8 Installer
- ![Fig. 9 Installer](https://dicd.tuiasi.ro/wp-content/uploads/2025/07/F9-installer.png)

  Fig. 9 Installer

### Linux

Pentru a realiza **Pasul 1**, presupunem că aveți conexiunea la internet prin alte mijloace (WIFI, LTE, HotSpot etc.). Alternativ, puteți transfera programul de instalare pe dispozitiv folosind un stick USB.

Înainte de a urma pașii de mai jos, trebuie să ne asigurăm că avem conectat cablul în dispozitivul pe care vreți să-l conectați la internet.

**Pasul 1:** **Accesați site-ul de configurare Eduroam**. Deschideți un browser și accesați cat.eduroam.org. Selectați „Gheorghe Asachi” Technical University of Iasi, apoi din lista alegeți ‘campus-wired’ (Fig. 1), (Fig. 2), (Fig. 3)

**Pasul 2: Descărcați programul de configurare**. Apăsați pe butonul ‘eduroam®’ pentru a descarca installer-ul pentru LINUX. După descarcare, fișierul Python cu extensia .py ar trebui să apară în folderul Downloads. (Fig. 4)

**Pasul 3:** **Ruleaza programul de configurare**. Pentru a rula este necesara comanda *python3 eduroam-linux-TUIASI-campus.py*. (Fig. 5)

**Pasul 4:Urmați pașii installer-ului**. Introduceți datele dumneavoastră de autentificare când se cer (adresa de e-mail instituțională TUIASI și parola contului). După configurare conexiunea ar trebui să fie funcțională. (Fig. 6), (Fig. 7), (Fig. 8), (Fig. 9).

- ![Fig. 1 cat.eduroam.org](https://dicd.tuiasi.ro/wp-content/uploads/2025/07/cat.eduroam.org_-1024x505.png)

  Fig. 1 cat.eduroam.org
- ![Fig. 2 Selectare-Universitate](https://dicd.tuiasi.ro/wp-content/uploads/2025/07/Selectare-Universitate.png)

  Fig. 2 Selectare-Universitate
- ![Fig. 3 Site-Eduroam](https://dicd.tuiasi.ro/wp-content/uploads/2025/07/Site-Eduroam-1024x733.png)

  Fig. 3 Site-Eduroam
- ![Fig 4. Descarcare-Script](https://dicd.tuiasi.ro/wp-content/uploads/2025/07/Descarcare-Script.png)

  Fig 4. Descarcare-Script
- ![Fig 5. Rulare-script](https://dicd.tuiasi.ro/wp-content/uploads/2025/07/rulare-script.png)

  Fig 5. Rulare-script
- ![Fig. 6 Information](https://dicd.tuiasi.ro/wp-content/uploads/2025/07/information.png)

  Fig. 6 Information
- ![Fig. 7 Information](https://dicd.tuiasi.ro/wp-content/uploads/2025/07/information-2.png)

  Fig. 7 Information
- ![Fig 8. Credentials](https://dicd.tuiasi.ro/wp-content/uploads/2025/07/credentials-2.png)

  Fig 8. Credentials
- ![Fig. 9 Success](https://dicd.tuiasi.ro/wp-content/uploads/2025/07/succes.png)

  Fig. 9 Success
