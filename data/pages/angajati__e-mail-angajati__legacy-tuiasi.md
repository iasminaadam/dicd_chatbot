---
title: "Legacy (@tuiasi.ro)"
url: "https://dicd.tuiasi.ro/ro/angajati/e-mail-angajati/legacy-tuiasi/"
---

# Legacy (@tuiasi.ro)

Acest tutorial este realizat pentru adresele de e-mail cu domeniul **@tuiasi.ro**. În prezent nu se mai creează astfel de e-mailuri, deoarece noile adrese personale vor fi de forma **@academic.tuiasi.ro**, **@staff.tuiasi.ro** și **@student.tuiasi.ro**, iar cele de grup vor fi de forma **@groups.tuiasi.ro**.

Utilizatorii rețelei **TUIASI** cu casuțele poștale pe serverul **TUIASI** (mail.tuiasi.ro) au la dispoziție trei metode pentru conectare:

- Prin interfața **[webmail](https://www.webmail.tuiasi.ro)**;
- Folosind un client(program) dedicat de poștă electronică (thunderbird, outlook express, etc.) de pe un calculator personal;
- Folosind un echipament mobil (telefon, tabletă) cu acces la internet, prin aplicația de citit poșta electronică specifică acelui echipament

**Nu recomandăm accesarea căsuței poștale prin intefața webmail de pe echipamente mobile dacă folosiți un abonament mobil de date, pentru că interfața webmail nu este optimizată din punct de vedere al traficului de date pentru folosirea pe dispozitive mobile și vă poate consuma relativ rapid traficul disponibil. În cazul accesului printr-o conexiune wireless nu este nici o problemă.**

**SSCD recomandă:**

- conectarea la serverul de mail prin **IMAP** (o parte din avantaje sunt prezentate mai jos)
- configurarea programului de poștă electronică (thunderbird, outlook, etc.), daca folosiți, în așa fel încât **să lase o copie a mesajelor pe server**, pentru ca mesajele primite să vă fie accesibile și de pe telefonul mobil, webmail, etc.

Setări pentru un client dedicat de poștă electronică

Incoming server: **mail.tuiasi.ro**

- protocol **IMAP**, portul **993** – conexiune securizata cu **SSL/TLS**

sau

- protocol **POP3**, portul **995** – conexiune securizata cu **SSL/TLS**

Outgoing server: **mail.tuiasi.ro**

- protocol **SMTP**, portul **587** – conexiune securizata cu **STARTTLS** sau **TLS** sau **SSL** (pt Outlook Express cu ****SSL**** iar pentru Outlook 2000+ cu **TLS**)

Pentru ambele setări (incoming/outgoing) este necesară și autentificarea plain text (normal password) cu **numele de utilizator si parola de acces** la casuța poștală. De regulă, programele de poștă electronică vor folosi în mod automat aceeași parolă introdusă pentru citirea mesajelor (conectarea prin IMAP sau POP3) și pentru trimiterea mesajelor (conectarea prin SMTP).

IMAP vs POP3

Pentru a alege între POP3 și IMAP sunt câteva chestiuni de considerat:

- **IMAP** este un protocol mai nou, permite aplicațiilor client să caute în mesaje direct pe server (foloseste puterea de procesare a acestuia și nu necesită copierea tuturor mesajelor local). Permite structurarea mesajelor în directoare/subdirectoare pe server și sincronizarea acestora pe orice aplicație de citire a poștei electronice. Permite etichetarea mesajelor pe server ca fiind citite/necititite/importante și permite primirea de notificări de tip PUSH la primirea de mesaje noi prin IMAP IDLE – în cazul conectării cu un echipament mobil.
- **POP3** permite folosirea unui singur director pentru mesaje pe server, iar orice directoare/subdirectoare create în aplicația de citire a poștei rămân locale și nu vor fi recunoscute la conectarea cu un alt dispozitiv (gen webmail, telefon mobil, sau de la un alt calculator). În plus, un client POP3 va trebui să copie toate mesajele local pentru a putea să caute după un anumit mesaj**.**

Configurare diferite programe de poștă electronică

- [Android Mail](https://dicd.tuiasi.ro/informatii-utile/instrucțiuni-de-conectare-cu-programe-de-poștă-electronică/clienți-mobil/android-mail/)
- [AquaMail](https://dicd.tuiasi.ro/informatii-utile/instrucțiuni-de-conectare-cu-programe-de-poștă-electronică/clienți-mobil/aquamail/)
- [eM Client](https://dicd.tuiasi.ro/informatii-utile/instrucțiuni-de-conectare-cu-programe-de-poștă-electronică/clienți-desktop/em-client/)
- [GMail](https://dicd.tuiasi.ro/informatii-utile/instrucțiuni-de-conectare-cu-programe-de-poștă-electronică/clienți-mobil/gmail/)
- [K-9 Mail](https://dicd.tuiasi.ro/informatii-utile/instrucțiuni-de-conectare-cu-programe-de-poștă-electronică/clienți-mobil/k-9-mail/)
- [MailBird](https://dicd.tuiasi.ro/informatii-utile/instrucțiuni-de-conectare-cu-programe-de-poștă-electronică/clienți-desktop/mailbird/)
- [Mozilla Thunderbird](https://dicd.tuiasi.ro/informatii-utile/instrucțiuni-de-conectare-cu-programe-de-poștă-electronică/clienți-desktop/mozilla-thunderbird/)
- [Windows Live Mail](https://dicd.tuiasi.ro/informatii-utile/instrucțiuni-de-conectare-cu-programe-de-poștă-electronică/clienți-desktop/windows-live-mail-2009/)

Instrucțiuni pentru redirecționare și răspuns automat la mesaje

Pentru redirecționarea automată a mesajelor de tip e-mail sau intrare în mod concediu si trimiterea de răspunsuri automate pe perioada acestuia, pașii ce trebuie urmați sunt următorii:

**Pas 1**. Din interfața [**webmail**](https://webmail.tuiasi.ro) alegeți “**Opțiuni**“ (Fig. 1).

**Pas 2**. Alegeți opțiunea “**Auto Response: Reply or Forward**“ (Fig. 2).

**Pas 3.** Redirecționare mesaje (Fig. 3)

- Bifați căsuța pentru “**Forward**“
- Completați adresa de e-mail către care se va face redirecționarea mesajelor
- Dacă doriți ca o copie a fiecărui mesaj să ramană si pe server, bifați căsuța “**Keep a copy here**“
- Salvați modificările cu “**Finish**“.

**Pas 3.** Activare mod concediu (Fig. 4)

- Debifați opțiunea pentru redirecționare dacă este activată și bifați opțiunea pentru trimiterea de răspunsuri automate: “**Reply**“.
- Alegeți un subiect pentru mesajul ce va fi trimis ca răspuns tuturor celor ce vă scriu pe durata concediului, sau dacă lasați campul subject gol mesajele vor avea subiectul implicit de forma “RE: <subiectul mesajului original>”
- Alegeti un conținut pentru mesajul ce urmează să fie trimis, sau modificați mesajul implicit
- Dacă aveați deja activat modul concediu și doar faceți modificări, aveți posibilitatea să resetați baza de date cu destinatarii care au primit un mesaj deja dacă bifați opțiunea “**Empty reply cache**“
- Finalizați operațiunea apăsând “**Finish**“

- ![Fig. 1 Opțiuni](https://dicd.tuiasi.ro/wp-content/uploads/2021/09/1-12.png)

  Fig. 1 Opțiuni
- ![Fig. 2 Auto Response](https://dicd.tuiasi.ro/wp-content/uploads/2021/09/2-12.png)

  Fig. 2 Auto Response
- ![Fig. 3 Redirecționare mesaje](https://dicd.tuiasi.ro/wp-content/uploads/2021/09/3-11.png)

  Fig. 3 Redirecționare mesaje
- ![Fig. 4 Activare mod concediu](https://dicd.tuiasi.ro/wp-content/uploads/2021/09/4-7.png)

  Fig. 4 Activare mod concediu
