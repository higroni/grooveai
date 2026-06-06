# ZAIKON - Korisnički Scenariji i Use Case-ovi

## Pregled

Ovaj dokument opisuje tri glavna načina korišćenja ZAIKON sistema iz perspektive pravnika, zakonodavaca i drugih stručnjaka koji nisu IT profesionalci. Fokus je na praktičnim scenarijima i korisničkom iskustvu.

---

## Use Case 1: Inteligentna Pretraga i Chatbot Asistent

### 📋 Opis

Korisnik može da pretražuje pravni korpus koristeći prirodan jezik i da postavlja pitanja AI asistentu koji razume kontekst i pruža precizne odgovore sa referencama na izvorne dokumente.

### 👤 Tipični Korisnici

- **Pravnici** - traže relevantne propise za konkretne slučajeve
- **Zakonodavci** - istražuju postojeću regulativu pre pisanja novih propisa
- **Državni službenici** - proveravaju primenu zakona u praksi
- **Studenti prava** - uče i istražuju pravnu materiju

---

### 🎬 Scenario 1.1: Brza Pretraga Propisa

**Kontekst:** Marija je pravnica u ministarstvu šumarstva. Treba joj da pronađe sve propise koji se odnose na zaštitu šuma od požara.

#### Koraci:

**1. Otvaranje Aplikacije**
```
Marija otvara ZAIKON u web pregledaču.
Vidi jednostavan interfejs sa poljem za pretragu i chatbot prozorom.
```

**2. Unos Upita**
```
Marija kuca u polje za pretragu:
"propisi o zaštiti šuma od požara"
```

**3. Rezultati Pretrage**
```
Sistem prikazuje:

┌─────────────────────────────────────────────────┐
│ 🔍 Pronađeno 8 relevantnih dokumenata          │
├─────────────────────────────────────────────────┤
│                                                 │
│ 📄 Zakon o šumama                              │
│    Član 45: Mere zaštite od požara             │
│    Relevantnost: 95%                           │
│    [Prikaži detalje] [Otvori dokument]         │
│                                                 │
│ 📄 Pravilnik o protivpožarnoj zaštiti         │
│    Član 12: Obaveze vlasnika šuma              │
│    Relevantnost: 92%                           │
│    [Prikaži detalje] [Otvori dokument]         │
│                                                 │
│ 📄 Uredba o korišćenju sredstava              │
│    Član 8: Finansiranje protivpožarnih mera    │
│    Relevantnost: 88%                           │
│    [Prikaži detalje] [Otvori dokument]         │
│                                                 │
│ ... još 5 rezultata                            │
└─────────────────────────────────────────────────┘
```

**4. Pregled Detalja**
```
Marija klikne na "Prikaži detalje" za Zakon o šumama.
Sistem prikazuje:

┌─────────────────────────────────────────────────┐
│ Zakon o šumama - Član 45                       │
├─────────────────────────────────────────────────┤
│                                                 │
│ Član 45                                         │
│                                                 │
│ (1) Vlasnik šume dužan je da preduzme mere     │
│ zaštite od požara u skladu sa planom zaštite.  │
│                                                 │
│ (2) Mere zaštite obuhvataju:                   │
│   1) održavanje protivpožarnih puteva          │
│   2) postavljanje protivpožarnih znakova       │
│   3) obezbeđivanje pristupa vatrogasnim        │
│      vozilima                                   │
│                                                 │
│ (3) Ministarstvo vrši nadzor nad primenom      │
│ mera zaštite.                                   │
│                                                 │
│ 📎 Povezani propisi:                           │
│   • Pravilnik o protivpožarnoj zaštiti        │
│   • Uredba o finansiranju mera zaštite        │
│                                                 │
│ [Kopiraj tekst] [Izvezi PDF] [Dodaj u beleške]│
└─────────────────────────────────────────────────┘
```

**Rezultat:** Marija je za 30 sekundi pronašla sve relevantne propise i može da nastavi sa svojim radom.

---

### 🎬 Scenario 1.2: Konverzacija sa AI Asistentom

**Kontekst:** Petar je zakonodavac koji priprema novi pravilnik. Želi da razume kako trenutni propisi regulišu određenu oblast.

#### Koraci:

**1. Pokretanje Chatbot-a**
```
Petar klikne na ikonu chatbot-a u donjem desnom uglu.
Otvara se prozor za konverzaciju.
```

**2. Postavljanje Pitanja**
```
Petar piše:
"Koje su obaveze vlasnika privatnih šuma prema važećim propisima?"
```

**3. AI Odgovor sa Referencama**
```
┌─────────────────────────────────────────────────┐
│ 🤖 ZAIKON Asistent                             │
├─────────────────────────────────────────────────┤
│                                                 │
│ Prema važećim propisima, vlasnici privatnih    │
│ šuma imaju sledeće obaveze:                    │
│                                                 │
│ 1. **Gazdovanje šumom** (Zakon o šumama, čl.  │
│    23): Vlasnik je dužan da gazduje šumom u    │
│    skladu sa osnovom gazdovanja.               │
│    [📄 Vidi član 23]                           │
│                                                 │
│ 2. **Zaštita od požara** (Zakon o šumama, čl. │
│    45): Preduzimanje mera protivpožarne        │
│    zaštite prema planu zaštite.                │
│    [📄 Vidi član 45]                           │
│                                                 │
│ 3. **Evidencija** (Pravilnik o evidenciji, čl.│
│    5): Vođenje evidencije o stanju šume i      │
│    izvršenim radovima.                         │
│    [📄 Vidi član 5]                            │
│                                                 │
│ 4. **Prijavljivanje** (Zakon o šumama, čl. 67)│
│    : Prijava štetočina i bolesti nadležnom     │
│    organu u roku od 3 dana.                    │
│    [📄 Vidi član 67]                           │
│                                                 │
│ Da li želite detaljnije informacije o nekoj od │
│ ovih obaveza?                                   │
└─────────────────────────────────────────────────┘
```

**4. Dodatno Pitanje**
```
Petar pita:
"Šta se dešava ako vlasnik ne ispuni obavezu gazdovanja?"
```

**5. Detaljan Odgovor**
```
┌─────────────────────────────────────────────────┐
│ 🤖 ZAIKON Asistent                             │
├─────────────────────────────────────────────────┤
│                                                 │
│ Ako vlasnik ne ispuni obavezu gazdovanja šumom,│
│ predviđene su sledeće sankcije:                │
│                                                 │
│ **Prekršajne kazne** (Zakon o šumama, čl. 89):│
│                                                 │
│ • Za pravno lice: 500,000 - 1,000,000 dinara   │
│ • Za odgovorno lice: 50,000 - 100,000 dinara   │
│ • Za fizičko lice: 20,000 - 50,000 dinara      │
│   [📄 Vidi član 89]                            │
│                                                 │
│ **Dodatne mere** (Zakon o šumama, čl. 24):     │
│                                                 │
│ • Ministarstvo može naložiti vlasnik da        │
│   preduzme određene radove u roku od 30 dana   │
│ • Ako vlasnik ne postupi, ministarstvo može    │
│   izvršiti radove o trošku vlasnika            │
│   [📄 Vidi član 24]                            │
│                                                 │
│ **Napomena:** Kazne se mogu kombinovati sa     │
│ dodatnim merama.                                │
│                                                 │
│ Da li želite da vidite primere iz prakse?      │
└─────────────────────────────────────────────────┘
```

**Rezultat:** Petar je dobio precizne informacije sa referencama na izvorne propise, bez potrebe da ručno pretražuje desetine dokumenata.

---

### 🎬 Scenario 1.3: Istraživanje Povezanih Propisa

**Kontekst:** Ana je studentkinja prava koja piše seminarski rad o šumskom zakonodavstvu.

#### Koraci:

**1. Početna Pretraga**
```
Ana pretražuje: "šumsko zakonodavstvo Srbija"
```

**2. Vizualizacija Povezanosti**
```
Sistem prikazuje graf povezanih propisa:

        Zakon o šumama (2010)
              │
    ┌─────────┼─────────┐
    │         │         │
Pravilnik   Uredba   Pravilnik
o gazdov.   o sred.  o evidenc.
    │         │         │
    └─────────┼─────────┘
              │
        Strategija razvoja
```

**3. Filtriranje po Tipu**
```
Ana može da filtrira:
☑ Zakoni (1)
☑ Pravilnici (8)
☑ Uredbe (3)
☐ Strategije (1)
☐ Naredbe (2)
```

**4. Izvoz za Seminarski Rad**
```
Ana selektuje relevantne dokumente i klikne "Izvezi bibliografiju"
Sistem generiše:

BIBLIOGRAFIJA

1. Zakon o šumama, "Službeni glasnik RS", br. 30/2010, 
   93/2012, 89/2015

2. Pravilnik o gazdovanju šumama, "Službeni glasnik RS", 
   br. 15/2011

3. Uredba o korišćenju sredstava za održivi razvoj šuma, 
   "Službeni glasnik RS", br. 8/2012

[Kopiraj] [Izvezi Word] [Izvezi BibTeX]
```

**Rezultat:** Ana je brzo prikupila sve potrebne izvore za svoj seminarski rad sa tačnim referencama.

---

### 💡 Ključne Karakteristike Use Case-a 1

**Za Korisnika:**
- ✅ Prirodan jezik - ne treba znati pravnu terminologiju
- ✅ Brzi rezultati - odgovori za sekunde
- ✅ Reference na izvore - uvek sa linkom na originalni tekst
- ✅ Kontekstualno razumevanje - AI razume šta korisnik zapravo pita
- ✅ Povezani propisi - automatski prikazuje relevantne dokumente

**Tehnička Implementacija:**
- Hibridna pretraga (semantička + keyword + graf)
- Embeddings za razumevanje značenja
- Reranking za preciznost
- LLM za generisanje odgovora
- Citation tracking za reference

---

## Use Case 2: Provera Usaglašenosti i Detekcija Konflikata

### 📋 Opis

Korisnik učitava nacrt novog propisa (zakon, pravilnik, uredbu) i sistem automatski detektuje konflikte sa postojećim propisima, pruža detaljne izveštaje i sugeriše kako da se tekst popravi.

### 👤 Tipični Korisnici

- **Zakonodavci** - proveravaju nacrt pre slanja u proceduru
- **Pravni savetnici** - analiziraju usklađenost propisa
- **Ministarstva** - pripremaju podzakonske akte
- **Revizori** - proveravaju postojeće propise

---

### 🎬 Scenario 2.1: Provera Nacrta Pravilnika

**Kontekst:** Jelena radi u ministarstvu i pripremila je nacrt novog Pravilnika o dodeli sredstava za šumarstvo. Pre slanja na dalju proceduru, želi da proveri da li je usklađen sa postojećim propisima.

#### Koraci:

**1. Učitavanje Dokumenta**
```
┌─────────────────────────────────────────────────┐
│ 📤 Učitaj Nacrt Propisa                        │
├─────────────────────────────────────────────────┤
│                                                 │
│  Prevuci dokument ovde ili klikni za izbor     │
│                                                 │
│  Podržani formati: PDF, DOCX, TXT              │
│  Maksimalna veličina: 100 MB                   │
│                                                 │
│  [Izaberi fajl]                                │
└─────────────────────────────────────────────────┘
```

Jelena prevuče fajl "Nacrt_Pravilnika_Dodela_Sredstava.docx"

**2. Izbor Korpusa za Proveru**
```
┌─────────────────────────────────────────────────┐
│ 📚 Izaberi Korpus za Proveru                   │
├─────────────────────────────────────────────────┤
│                                                 │
│ ⦿ Šumarstvo - Kompletna regulativa (45 dok.)   │
│   Poslednje ažurirano: 15.05.2024.             │
│                                                 │
│ ○ Opšta zakonska regulativa (1,250 dok.)       │
│   Poslednje ažurirano: 01.06.2024.             │
│                                                 │
│ ○ Prilagođeni korpus...                        │
│                                                 │
│ [Nastavi]                                       │
└─────────────────────────────────────────────────┘
```

Jelena bira "Šumarstvo - Kompletna regulativa"

**3. Analiza u Toku**
```
┌─────────────────────────────────────────────────┐
│ ⏳ Analiza u toku...                           │
├─────────────────────────────────────────────────┤
│                                                 │
│ ✓ Učitavanje dokumenta                         │
│ ✓ Parsiranje strukture (45 članova)           │
│ ✓ Ekstrakcija normativnih tvrdnji (128)       │
│ ⏳ Pretraga korpusa...                         │
│ ⏳ Detekcija konflikata...                     │
│                                                 │
│ Procenjeno vreme: 2 minuta                     │
│                                                 │
│ [████████░░░░░░░░░░░░] 40%                     │
└─────────────────────────────────────────────────┘
```

**4. Rezultati Analize**
```
┌─────────────────────────────────────────────────┐
│ ✅ Analiza Završena                            │
├─────────────────────────────────────────────────┤
│                                                 │
│ 📊 PREGLED REZULTATA                           │
│                                                 │
│ Analizirano: 45 članova, 128 tvrdnji          │
│ Vreme analize: 1 min 47 sek                    │
│                                                 │
│ 🔴 Kritični konflikti: 3                       │
│ 🟠 Visoki konflikti: 7                         │
│ 🟡 Srednji konflikti: 12                       │
│ 🟢 Niski konflikti: 5                          │
│                                                 │
│ ✓ Bez konflikta: 101 tvrdnji                   │
│                                                 │
│ [Prikaži Detaljni Izveštaj]                   │
│ [Izvezi PDF] [Izvezi Excel]                   │
└─────────────────────────────────────────────────┘
```

**5. Pregled Kritičnih Konflikata**
```
Jelena klikne na "Prikaži Detaljni Izveštaj"

┌─────────────────────────────────────────────────┐
│ 🔴 KRITIČNI KONFLIKTI (3)                      │
├─────────────────────────────────────────────────┤
│                                                 │
│ Konflikt #1: Direktna Kontradikcija            │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                 │
│ 📍 Lokacija: Član 5, stav 1                    │
│                                                 │
│ 📝 Tekst iz nacrta:                            │
│ "Sredstva se dodeljuju u roku od 60 dana od    │
│  podnošenja zahteva."                          │
│                                                 │
│ ⚠️ Konflikt sa:                                │
│ Zakon o šumama, Član 78, stav 2                │
│                                                 │
│ 📝 Tekst iz korpusa:                           │
│ "Ministarstvo je dužno da odluči o zahtevu u   │
│  roku od 30 dana."                             │
│                                                 │
│ 🔍 Tip konflikta: Deadline Conflict            │
│ Ozbiljnost: Kritična                           │
│                                                 │
│ 💡 PREPORUKA:                                  │
│ Uskladite rok sa zakonskom obavezom od 30 dana.│
│ Predloženi tekst:                              │
│ "Sredstva se dodeljuju u roku od 30 dana od    │
│  podnošenja zahteva."                          │
│                                                 │
│ [Prihvati Preporuku] [Ignoriši] [Dodaj Komentar]│
│                                                 │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
└─────────────────────────────────────────────────┘
```

**6. Prihvatanje Preporuke**
```
Jelena klikne "Prihvati Preporuku"

┌─────────────────────────────────────────────────┐
│ ✅ Preporuka Prihvaćena                        │
├─────────────────────────────────────────────────┤
│                                                 │
│ Izmena je dodata u listu promena.              │
│                                                 │
│ Originalni tekst:                              │
│ "...u roku od 60 dana..."                      │
│                                                 │
│ Novi tekst:                                    │
│ "...u roku od 30 dana..."                      │
│                                                 │
│ [Vrati izmenu] [Nastavi sa sledećim konfliktom]│
└─────────────────────────────────────────────────┘
```

**7. Pregled Svih Izmena**
```
Nakon pregleda svih konflikata, Jelena klikne "Pregled Izmena"

┌─────────────────────────────────────────────────┐
│ 📋 PREGLED SVIH IZMENA                         │
├─────────────────────────────────────────────────┤
│                                                 │
│ Prihvaćeno izmena: 8                           │
│ Ignorisano konflikata: 2                       │
│ Komentara dodato: 3                            │
│                                                 │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                 │
│ Izmena #1 - Član 5, stav 1                     │
│ Tip: Deadline Conflict                         │
│ Staro: "...u roku od 60 dana..."               │
│ Novo: "...u roku od 30 dana..."                │
│                                                 │
│ Izmena #2 - Član 12, stav 3                    │
│ Tip: Obligation Conflict                       │
│ Staro: "...može podneti..."                    │
│ Novo: "...dužan je da podnese..."              │
│                                                 │
│ ... još 6 izmena                               │
│                                                 │
│ [Izvezi Izmenjeni Dokument]                    │
│ [Izvezi Izveštaj o Izmenama]                   │
│ [Pošalji na Email]                             │
└─────────────────────────────────────────────────┘
```

**8. Izvoz Izmenjenog Dokumenta**
```
Jelena klikne "Izvezi Izmenjeni Dokument"

Sistem generiše:
1. Izmenjeni_Nacrt_Pravilnika.docx - sa svim prihvaćenim izmenama
2. Izvestaj_o_Konfliktima.pdf - detaljan izveštaj
3. Tabela_Izmena.xlsx - tabelarni pregled svih izmena
```

**Rezultat:** Jelena je za 15 minuta proverila nacrt, identifikovala sve konflikte, prihvatila preporuke i dobila izmenjeni dokument spreman za dalju proceduru.

---

### 🎬 Scenario 2.2: Analiza Postojećeg Propisa

**Kontekst:** Marko je pravni savetnik koji treba da proveri da li je postojeći Pravilnik o gazdovanju šumama iz 2015. godine još uvek usklađen sa novim Zakonom o šumama iz 2020.

#### Koraci:

**1. Izbor Dokumenta za Proveru**
```
┌─────────────────────────────────────────────────┐
│ 📂 Izaberi Dokument iz Korpusa                 │
├─────────────────────────────────────────────────┤
│                                                 │
│ 🔍 Pretraži: [gazdovanje šumama          ]     │
│                                                 │
│ Rezultati:                                      │
│                                                 │
│ ☐ Pravilnik o gazdovanju šumama (2015)         │
│   45 članova, 128 tvrdnji                      │
│   [Izaberi za proveru]                         │
│                                                 │
│ ☐ Pravilnik o osnovi gazdovanja (2018)         │
│   32 člana, 89 tvrdnji                         │
│   [Izaberi za proveru]                         │
│                                                 │
└─────────────────────────────────────────────────┘
```

**2. Izbor Referentnog Perioda**
```
┌─────────────────────────────────────────────────┐
│ 📅 Proveri Usklađenost sa Propisima Posle:    │
├─────────────────────────────────────────────────┤
│                                                 │
│ Datum donošenja dokumenta: 15.03.2015.         │
│                                                 │
│ Proveri konflikte sa propisima donetim posle:  │
│ [15.03.2015.                    ] [▼]          │
│                                                 │
│ ℹ️ Sistem će proveriti usklađenost sa svim    │
│    propisima donetim nakon ovog datuma.        │
│                                                 │
│ [Pokreni Analizu]                              │
└─────────────────────────────────────────────────┘
```

**3. Rezultati Analize**
```
┌─────────────────────────────────────────────────┐
│ ⚠️ PRONAĐENI KONFLIKTI SA NOVIM PROPISIMA     │
├─────────────────────────────────────────────────┤
│                                                 │
│ Analizirano: 45 članova                        │
│ Novi propisi u korpusu: 12                     │
│                                                 │
│ 🔴 Kritični konflikti: 5                       │
│ 🟠 Visoki konflikti: 8                         │
│ 🟡 Srednji konflikti: 15                       │
│                                                 │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                 │
│ 📊 KONFLIKTI PO NOVIM PROPISIMA:               │
│                                                 │
│ • Zakon o šumama (2020) - 18 konflikata        │
│ • Uredba o sredstvima (2021) - 7 konflikata    │
│ • Pravilnik o evidenciji (2022) - 3 konflikta  │
│                                                 │
│ 💡 PREPORUKA:                                  │
│ Pravilnik zahteva hitnu reviziju zbog          │
│ značajnih promena u matičnom zakonu.           │
│                                                 │
│ [Generiši Predlog Izmena]                      │
│ [Izvezi Izveštaj za Ministarstvo]             │
└─────────────────────────────────────────────────┘
```

**4. Generisanje Predloga Izmena**
```
Marko klikne "Generiši Predlog Izmena"

┌─────────────────────────────────────────────────┐
│ 📝 PREDLOG IZMENA PRAVILNIKA                   │
├─────────────────────────────────────────────────┤
│                                                 │
│ PRAVILNIK O IZMENAMA I DOPUNAMA PRAVILNIKA     │
│ O GAZDOVANJU ŠUMAMA                            │
│                                                 │
│ Član 1                                          │
│ U Pravilniku o gazdovanju šumama ("Službeni    │
│ glasnik RS", br. 15/2015), u članu 5 stav 1    │
│ reči "u roku od 60 dana" zamenjuju se rečima   │
│ "u roku od 30 dana".                           │
│                                                 │
│ Obrazloženje: Usklađivanje sa Zakonom o šumama │
│ ("Službeni glasnik RS", br. 30/2020), član 78. │
│                                                 │
│ Član 2                                          │
│ U članu 12 stav 3 reči "može podneti" zamenjuju│
│ se rečima "dužan je da podnese".               │
│                                                 │
│ Obrazloženje: Usklađivanje sa Zakonom o šumama │
│ ("Službeni glasnik RS", br. 30/2020), član 45. │
│                                                 │
│ ... još 26 članova                             │
│                                                 │
│ [Izvezi Word] [Izvezi PDF] [Pošalji na Email] │
└─────────────────────────────────────────────────┘
```

**Rezultat:** Marko je dobio kompletan predlog izmena pravilnika sa obrazloženjima, spreman za dalju proceduru.

---

### 🎬 Scenario 2.3: Kontinuirana Provera Tokom Pisanja

**Kontekst:** Jovana piše novi pravilnik i želi da u realnom vremenu vidi da li tekst koji piše ima konflikte sa postojećim propisima.

#### Koraci:

**1. Aktiviranje Live Mode-a**
```
┌─────────────────────────────────────────────────┐
│ ✍️ EDITOR SA LIVE PROVEROM                     │
├─────────────────────────────────────────────────┤
│                                                 │
│ [Live Provera: ✓ Uključena]                    │
│                                                 │
│ Član 5                                          │
│                                                 │
│ (1) Vlasnik šume dužan je da podnese zahtev    │
│ za dodelu sredstava u roku od 90 dana.         │
│                          ⚠️ ───────────────┐   │
│                                             │   │
│ (2) Uz zahtev se prilaže:                   │   │
│   1) dokaz o vlasništvu                     │   │
│   2) plan gazdovanja                        │   │
│                                             │   │
│ ┌───────────────────────────────────────────┘   │
│ │ ⚠️ POTENCIJALNI KONFLIKT                      │
│ │                                               │
│ │ Rok od 90 dana je u konfliktu sa:            │
│ │ Zakon o šumama, član 78: "...u roku od 30    │
│ │ dana..."                                      │
│ │                                               │
│ │ [Vidi Detalje] [Ignoriši] [Izmeni]          │
│ └───────────────────────────────────────────────│
│                                                 │
│ [Sačuvaj] [Izvezi] [Podešavanja]               │
└─────────────────────────────────────────────────┘
```

**2. Brza Izmena**
```
Jovana klikne "Izmeni" i sistem automatski predlaže:

"...u roku od 30 dana."

Jovana prihvata i nastavlja sa pisanjem.
```

**3. Statistika u Realnom Vremenu**
```
U desnom panelu:

┌─────────────────────────┐
│ 📊 STATISTIKA           │
├─────────────────────────┤
│                         │
│ Napisano: 12 članova    │
│ Tvrdnji: 34             │
│                         │
│ Konflikti:              │
│ 🔴 Kritični: 0          │
│ 🟠 Visoki: 1            │
│ 🟡 Srednji: 3           │
│                         │
│ Poslednja provera:      │
│ Pre 5 sekundi           │
│                         │
│ [Osvježi]               │
└─────────────────────────┘
```

**Rezultat:** Jovana piše pravilnik i odmah vidi konflikte, što joj omogućava da ih reši pre nego što završi dokument.

---

### 💡 Ključne Karakteristike Use Case-a 2

**Za Korisnika:**
- ✅ Automatska detekcija - sistem pronalazi konflikte bez ručnog rada
- ✅ Jasne preporuke - konkretni predlozi kako popraviti tekst
- ✅ Prioritizacija - kritični konflikti se ističu
- ✅ Izvoz rezultata - Word, PDF, Excel formati
- ✅ Live provera - provera u realnom vremenu tokom pisanja

**Tehnička Implementacija:**
- 127 tipova konflikata
- Slot-based matching
- Severity scoring
- Automated suggestions
- Real-time analysis

---

## Poređenje Use Case-ova

| Aspekt | Use Case 1: Pretraga & Chatbot | Use Case 2: Provera Usaglašenosti |
|--------|--------------------------------|-----------------------------------|
| **Cilj** | Pronalaženje informacija | Detekcija konflikata |
| **Input** | Pitanje/upit | Nacrt dokumenta |
| **Output** | Odgovori sa referencama | Izveštaj o konfliktima + preporuke |
| **Vreme** | Sekunde | Minuti |
| **Interakcija** | Konverzaciona | Analitička |
| **Rezultat** | Znanje | Akcioni plan |

---

## Korisnički Interfejs - Ključni Elementi

### 1. Dashboard (Početna Strana)

```
┌─────────────────────────────────────────────────────────────┐
│ ZAIKON - AI Asistent za Pravnu Regulativu                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  🔍 Pretraži korpus...                          [🤖 Chatbot]│
│  ┌────────────────────────────────────────────────────────┐ │
│  │                                                        │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌──────────────────────┐  ┌──────────────────────┐        │
│  │ 📚 Pretraga Korpusa  │  │ ✓ Provera Nacrta     │        │
│  │                      │  │                      │        │
│  │ Pretražite 1,250     │  │ Učitajte nacrt i     │        │
│  │ pravnih dokumenata   │  │ proverite konflikte  │        │
│  │                      │  │                      │        │
│  │ [Otvori]             │  │ [Otvori]             │        │
│  └──────────────────────┘  └──────────────────────┘        │
│                                                              │
│  📊 NEDAVNE AKTIVNOSTI                                      │
│  • Provera nacrta: Pravilnik o dodeli... (Pre 2 sata)      │
│  • Pretraga: "zaštita šuma" (Pre 1 dan)                    │
│  • Analiza: Uredba o sredstvima (Pre 3 dana)               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 2. Chatbot Interfejs

```
┌─────────────────────────────────────┐
│ 🤖 ZAIKON Asistent                 │
├─────────────────────────────────────┤
│                                     │
│ Korisnik:                           │
│ Koje su obaveze vlasnika šuma?     │
│                                     │
│ ─────────────────────────────────── │
│                                     │
│ Asistent:                           │
│ Prema Zakonu o šumama, vlasnici     │
│ imaju sledeće obaveze:             │
│ 1. Gazdovanje (čl. 23)             │
│ 2. Zaštita (čl. 45)                │
│ ...                                 │
│                                     │
│ ─────────────────────────────────── │
│                                     │
│ [Unesite pitanje...          ] [→] │
│                                     │
│ 💡 Predlozi:                       │
│ • Šta je osnova gazdovanja?        │
│ • Kako se prijavljuju štetočine?  │
└─────────────────────────────────────┘
```

### 3. Provera Nacrta - Rezultati

```
┌─────────────────────────────────────────────────────────────┐
│ Analiza: Nacrt_Pravilnika_Dodela_Sredstava.docx             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ [Pregled] [Konflikti] [Izmene] [Izvoz]                     │
│                                                              │
│ 🔴 KRITIČNI KONFLIKTI (3)                                   │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                              │
│ #1 Član 5, stav 1 - Deadline Conflict                      │
│ Nacrt: "...u roku od 60 dana..."                           │
│ Korpus: Zakon o šumama, čl. 78 "...u roku od 30 dana..."   │
│ [Vidi Detalje] [Prihvati Preporuku] [Ignoriši]            │
│                                                              │
│ #2 Član 12, stav 3 - Obligation Conflict                   │
│ Nacrt: "...može podneti..."                                │
│ Korpus: Zakon o šumama, čl. 45 "...dužan je..."            │
│ [Vidi Detalje] [Prihvati Preporuku] [Ignoriši]            │
│                                                              │
│ #3 Član 18, stav 2 - Authority Conflict                    │
│ Nacrt: "...ministar donosi..."                             │
│ Korpus: Zakon o šumama, čl. 92 "...vlada donosi..."        │
│ [Vidi Detalje] [Prihvati Preporuku] [Ignoriši]            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Tipične Greške i Kako ih Sistem Rešava

### Greška 1: Korisnik Ne Zna Tačan Pravni Termin

**Problem:** Korisnik traži "pravila za sečenje drveća" umesto "uslovi za sečenje šuma"

**Rešenje:** 
- Sistem razume sinonime i prirodan jezik
- Automatski mapira na pravne termine
- Prikazuje rezultate sa oba termina

### Greška 2: Korisnik Propusti Konflikt

**Problem:** Korisnik ne primeti da rok u nacrtu nije usklađen sa zakonom

**Rešenje:**
- Sistem automatski detektuje sve konflikte
- Ističe kritične konflikte crvenom bojom
- Prikazuje tačnu lokaciju u tekstu

### Greška 3: Korisnik Ne Zna Kako da Popravi Tekst

**Problem:** Korisnik vidi konflikt ali ne zna kako da ga reši

**Rešenje:**
- Sistem daje konkretne preporuke
- Prikazuje tačan tekst koji treba koristiti
- Objašnjava zašto je izmena potrebna

---

## Benefiti za Različite Korisnike

### Za Zakonodavce
- ⏱️ **Ušteda vremena**: 80% brža priprema nacrta
- ✅ **Kvalitet**: Manje grešaka i konflikata
- 📊 **Transparentnost**: Jasna dokumentacija svih izmena

### Za Pravnike
- 🔍 **Brza pretraga**: Pronalaženje relevantnih propisa za sekunde
- 💡 **Kontekst**: AI razume šta korisnik zapravo pita
- 📚 **Kompletnost**: Automatski prikazuje povezane propise

### Za Ministarstva
- 🎯 **Usklađenost**: Automatska provera sa svim relevantnim propisima
- 📝 **Dokumentacija**: Kompletni izveštaji za dalju proceduru
- 🔄 **Kontinuitet**: Praćenje izmena u regulativi

### Za Studente
- 📖 **Učenje**: Lak pristup pravnoj materiji
- 🔗 **Povezanost**: Razumevanje odnosa između propisa
- 📄 **Reference**: Automatsko generisanje bibliografije

---

## Zaključak

ZAIKON sistem omogućava korisnicima koji nisu IT stručnjaci da:

1. **Brzo pronalaze** relevantne propise koristeći prirodan jezik
2. **Razumeju** kompleksnu regulativu kroz konverzaciju sa AI asistentom
3. **Automatski detektuju** konflikte u nacrtima propisa
4. **Dobiju konkretne preporuke** kako da poprave tekst
5. **Uštede vreme** i smanje greške u pripremi pravnih dokumenata

Sistem je dizajniran da bude **intuitivan**, **brz** i **precizan**, omogućavajući pravnicima da se fokusiraju na suštinu svog posla umesto na tehničke detalje pretrage i analize.