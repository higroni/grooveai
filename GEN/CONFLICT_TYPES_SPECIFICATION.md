# ZAIKON - Complete Conflict Types Specification

## Overview
This document defines all 127 conflict types organized into 8 categories. Each conflict type includes detection logic, severity calculation, and example scenarios in Serbian.

---

## Category 1: Normative Conflicts (16 types)

### 1.1 Contradictory Obligation
**ID**: `contradictory_obligation`
**Description**: Draft imposes obligation that contradicts existing obligation
**Severity**: High
**Detection Logic**:
```python
draft.action == "obaveza" and corpus.action == "obaveza"
and draft.object == corpus.object
and draft.modality != corpus.modality
```
**Serbian Example**:
- **Draft**: "Poslodavac je dužan da isplati naknadu u roku od 15 dana"
- **Corpus**: "Poslodavac je dužan da isplati naknadu u roku od 30 dana"
- **Conflict**: Različiti rokovi za istu obavezu

### 1.2 Contradictory Prohibition
**ID**: `contradictory_prohibition`
**Description**: Draft prohibits what corpus allows or requires
**Severity**: High
**Serbian Example**:
- **Draft**: "Zabranjeno je zapošljavanje lica mlađih od 18 godina"
- **Corpus**: "Dozvoljeno je zapošljavanje lica starijih od 15 godina uz saglasnost roditelja"
- **Conflict**: Nacrt zabranjuje ono što korpus dozvoljava

### 1.3 Contradictory Permission
**ID**: `contradictory_permission`
**Description**: Draft allows what corpus prohibits
**Severity**: High
**Serbian Example**:
- **Draft**: "Dozvoljeno je obavljanje rada u noćnim satima bez ograničenja"
- **Corpus**: "Zabranjeno je obavljanje rada u noćnim satima duže od 8 sati"
- **Conflict**: Nacrt dozvoljava ono što korpus zabranjuje

### 1.4 Conflicting Definition
**ID**: `conflicting_definition`
**Description**: Draft defines term differently than corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Radnik je lice koje obavlja poslove na osnovu ugovora o delu"
- **Corpus**: "Radnik je lice koje obavlja poslove na osnovu ugovora o radu"
- **Conflict**: Različite definicije istog pojma

### 1.5 Overlapping Scope
**ID**: `overlapping_scope`
**Description**: Draft and corpus regulate same subject with different rules
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Godišnji odmor traje najmanje 20 radnih dana"
- **Corpus**: "Godišnji odmor traje najmanje 30 radnih dana"
- **Conflict**: Isti predmet regulisan različitim pravilima

### 1.6 Conflicting Jurisdiction
**ID**: `conflicting_jurisdiction`
**Description**: Draft assigns authority that conflicts with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Inspekcija rada nadležna je za izdavanje dozvola za rad"
- **Corpus**: "Ministarstvo nadležno je za izdavanje dozvola za rad"
- **Conflict**: Različita nadležnost za istu aktivnost

### 1.7 Incompatible Procedure
**ID**: `incompatible_procedure`
**Description**: Draft procedure conflicts with corpus procedure
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Zahtev za dozvolu podnosi se elektronskim putem"
- **Corpus**: "Zahtev za dozvolu podnosi se lično ili poštom"
- **Conflict**: Nekompatibilne procedure

### 1.8 Conflicting Standard
**ID**: `conflicting_standard`
**Description**: Draft sets standard that conflicts with corpus standard
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Minimalna temperatura u radnom prostoru je 16°C"
- **Corpus**: "Minimalna temperatura u radnom prostoru je 18°C"
- **Conflict**: Različiti standardi za iste uslove

### 1.9 Contradictory Requirement
**ID**: `contradictory_requirement`
**Description**: Draft requirement contradicts corpus requirement
**Severity**: High
**Serbian Example**:
- **Draft**: "Za zasnivanje radnog odnosa potrebna je diploma fakulteta"
- **Corpus**: "Za zasnivanje radnog odnosa potrebna je srednja škola"
- **Conflict**: Kontradiktorni uslovi

### 1.10 Conflicting Exception
**ID**: `conflicting_exception`
**Description**: Draft exception conflicts with corpus exception
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Izuzetak od obaveze plaćanja doprinosa važi za preduzeća sa manje od 5 zaposlenih"
- **Corpus**: "Izuzetak od obaveze plaćanja doprinosa važi za preduzeća sa manje od 10 zaposlenih"
- **Conflict**: Različiti kriterijumi za izuzetak

### 1.11 Incompatible Limitation
**ID**: `incompatible_limitation`
**Description**: Draft limitation incompatible with corpus limitation
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Prekovremeni rad ograničen je na 4 sata nedeljno"
- **Corpus**: "Prekovremeni rad ograničen je na 8 sati nedeljno"
- **Conflict**: Nekompatibilna ograničenja

### 1.12 Conflicting Eligibility
**ID**: `conflicting_eligibility`
**Description**: Draft eligibility criteria conflict with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Pravo na naknadu imaju zaposleni sa najmanje 6 meseci staža"
- **Corpus**: "Pravo na naknadu imaju zaposleni sa najmanje 12 meseci staža"
- **Conflict**: Različiti kriterijumi podobnosti

### 1.13 Contradictory Qualification
**ID**: `contradictory_qualification`
**Description**: Draft qualifications contradict corpus qualifications
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Za radno mesto potrebna je licenca kategorije B"
- **Corpus**: "Za radno mesto potrebna je licenca kategorije C"
- **Conflict**: Kontradiktorni kvalifikacioni zahtevi

### 1.14 Incompatible Certification
**ID**: `incompatible_certification`
**Description**: Draft certification requirements incompatible with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Sertifikat važi 2 godine"
- **Corpus**: "Sertifikat važi 5 godina"
- **Conflict**: Nekompatibilni zahtevi za sertifikaciju

### 1.15 Conflicting Authorization
**ID**: `conflicting_authorization`
**Description**: Draft authorization conflicts with corpus authorization
**Severity**: High
**Serbian Example**:
- **Draft**: "Direktor ovlašćen je da donosi odluke o zapošljavanju"
- **Corpus**: "Upravni odbor ovlašćen je da donosi odluke o zapošljavanju"
- **Conflict**: Konfliktna ovlašćenja

### 1.16 Contradictory Delegation
**ID**: `contradictory_delegation`
**Description**: Draft delegation contradicts corpus delegation
**Severity**: High
**Serbian Example**:
- **Draft**: "Ministar može delegirati ovlašćenja sekretaru"
- **Corpus**: "Ministar ne može delegirati ovlašćenja"
- **Conflict**: Kontradiktorni uslovi delegiranja

---

## Category 2: Temporal Conflicts (15 types)

### 2.1 Retroactive Application Conflict
**ID**: `retroactive_application_conflict`
**Description**: Draft applies retroactively where corpus prohibits
**Severity**: Critical
**Serbian Example**:
- **Draft**: "Ovaj pravilnik primenjuje se od 1. januara 2023. godine"
- **Corpus**: "Zabranjena je retroaktivna primena propisa"
- **Conflict**: Retroaktivna primena gde je zabranjena

### 2.2 Conflicting Effective Date
**ID**: `conflicting_effective_date`
**Description**: Draft effective date conflicts with corpus requirements
**Severity**: High
**Serbian Example**:
- **Draft**: "Pravilnik stupa na snagu danom objavljivanja"
- **Corpus**: "Pravilnik stupa na snagu 30 dana od dana objavljivanja"
- **Conflict**: Različiti datumi stupanja na snagu

### 2.3 Deadline Conflict
**ID**: `deadline_conflict`
**Description**: Draft deadline conflicts with corpus deadline
**Severity**: High
**Serbian Example**:
- **Draft**: "Prijava se podnosi najkasnije 15 dana pre početka rada"
- **Corpus**: "Prijava se podnosi najkasnije 30 dana pre početka rada"
- **Conflict**: Različiti rokovi za istu radnju

### 2.4 Transitional Period Conflict
**ID**: `transitional_period_conflict`
**Description**: Draft transition period conflicts with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Prelazni period traje 6 meseci"
- **Corpus**: "Prelazni period traje 12 meseci"
- **Conflict**: Različiti prelazni periodi

### 2.5 Grace Period Conflict
**ID**: `grace_period_conflict`
**Description**: Draft grace period conflicts with corpus grace period
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Period prilagođavanja je 30 dana"
- **Corpus**: "Period prilagođavanja je 60 dana"
- **Conflict**: Različiti periodi prilagođavanja

### 2.6 Expiration Conflict
**ID**: `expiration_conflict`
**Description**: Draft expiration conflicts with corpus expiration
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Dozvola važi 1 godinu"
- **Corpus**: "Dozvola važi 3 godine"
- **Conflict**: Različiti rokovi važenja

### 2.7 Renewal Conflict
**ID**: `renewal_conflict`
**Description**: Draft renewal terms conflict with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Obnova se vrši automatski"
- **Corpus**: "Obnova zahteva podnošenje novog zahteva"
- **Conflict**: Različiti uslovi obnove

### 2.8 Suspension Period Conflict
**ID**: `suspension_period_conflict`
**Description**: Draft suspension period conflicts with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Suspenzija traje do 30 dana"
- **Corpus**: "Suspenzija traje do 90 dana"
- **Conflict**: Različiti periodi suspenzije

### 2.9 Waiting Period Conflict
**ID**: `waiting_period_conflict`
**Description**: Draft waiting period conflicts with corpus
**Severity**: Low
**Serbian Example**:
- **Draft**: "Period čekanja je 7 dana"
- **Corpus**: "Period čekanja je 15 dana"
- **Conflict**: Različiti periodi čekanja

### 2.10 Notice Period Conflict
**ID**: `notice_period_conflict`
**Description**: Draft notice period conflicts with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Otkazni rok je 15 dana"
- **Corpus**: "Otkazni rok je 30 dana"
- **Conflict**: Različiti otkazni rokovi

### 2.11 Reporting Frequency Conflict
**ID**: `reporting_frequency_conflict`
**Description**: Draft reporting frequency conflicts with corpus
**Severity**: Low
**Serbian Example**:
- **Draft**: "Izveštaj se podnosi mesečno"
- **Corpus**: "Izveštaj se podnosi kvartalno"
- **Conflict**: Različita učestalost izveštavanja

### 2.12 Review Cycle Conflict
**ID**: `review_cycle_conflict`
**Description**: Draft review cycle conflicts with corpus
**Severity**: Low
**Serbian Example**:
- **Draft**: "Revizija se vrši godišnje"
- **Corpus**: "Revizija se vrši na svake 3 godine"
- **Conflict**: Različiti ciklusi revizije

### 2.13 Validity Period Conflict
**ID**: `validity_period_conflict`
**Description**: Draft validity period conflicts with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Sertifikat važi 2 godine"
- **Corpus**: "Sertifikat važi 5 godina"
- **Conflict**: Različiti periodi važenja

### 2.14 Statute of Limitations Conflict
**ID**: `statute_of_limitations_conflict`
**Description**: Draft statute of limitations conflicts with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Zastarelost nastupa nakon 1 godine"
- **Corpus**: "Zastarelost nastupa nakon 3 godine"
- **Conflict**: Različiti rokovi zastarelosti

### 2.15 Prescription Period Conflict
**ID**: `prescription_period_conflict`
**Description**: Draft prescription period conflicts with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Rok za podnošenje zahteva je 30 dana"
- **Corpus**: "Rok za podnošenje zahteva je 60 dana"
- **Conflict**: Različiti prekluzivni rokovi

---

## Category 3: Hierarchical Conflicts (18 types)

### 3.1 Constitutional Violation
**ID**: `constitutional_violation`
**Description**: Draft violates constitutional provisions
**Severity**: Critical
**Serbian Example**:
- **Draft**: "Zabranjeno je udruživanje radnika"
- **Corpus (Ustav)**: "Garantovano je pravo na sindikalno organizovanje"
- **Conflict**: Kršenje ustavnog prava

### 3.2 International Law Conflict
**ID**: `international_law_conflict`
**Description**: Draft conflicts with international obligations
**Severity**: Critical
**Serbian Example**:
- **Draft**: "Radna nedelja može trajati do 60 sati"
- **Corpus (ILO konvencija)**: "Radna nedelja ne može trajati duže od 48 sati"
- **Conflict**: Kršenje međunarodnih obaveza

### 3.3 EU Directive Conflict
**ID**: `eu_directive_conflict`
**Description**: Draft conflicts with EU directives
**Severity**: Critical
**Serbian Example**:
- **Draft**: "Minimalna plata je 200 evra"
- **Corpus (EU direktiva)**: "Minimalna plata mora biti najmanje 50% prosečne plate"
- **Conflict**: Neusklađenost sa EU direktivom

### 3.4 Primary Law Conflict
**ID**: `primary_law_conflict`
**Description**: Draft (regulation) conflicts with primary law
**Severity**: Critical
**Serbian Example**:
- **Draft (Pravilnik)**: "Otkazni rok je 7 dana"
- **Corpus (Zakon o radu)**: "Otkazni rok ne može biti kraći od 15 dana"
- **Conflict**: Pravilnik u suprotnosti sa zakonom

### 3.5 Framework Law Conflict
**ID**: `framework_law_conflict`
**Description**: Draft exceeds framework law authorization
**Severity**: High
**Serbian Example**:
- **Draft**: "Ministar propisuje uslove za zapošljavanje"
- **Corpus (Okvirni zakon)**: "Uslove za zapošljavanje propisuje Vlada"
- **Conflict**: Prekoračenje ovlašćenja

### 3.6 Organic Law Conflict
**ID**: `organic_law_conflict`
**Description**: Draft conflicts with organic law
**Severity**: Critical
**Serbian Example**:
- **Draft**: "Izmena se vrši običnom većinom"
- **Corpus (Organski zakon)**: "Izmena zahteva dvotrećinsku većinu"
- **Conflict**: Suprotnost sa organskim zakonom

### 3.7 Enabling Act Conflict
**ID**: `enabling_act_conflict`
**Description**: Draft exceeds enabling act authorization
**Severity**: High
**Serbian Example**:
- **Draft**: "Ministar propisuje visinu kazni"
- **Corpus (Ovlašćujući zakon)**: "Ministar propisuje samo postupak"
- **Conflict**: Prekoračenje ovlašćenja

### 3.8 Superior Regulation Conflict
**ID**: `superior_regulation_conflict`
**Description**: Draft conflicts with superior regulation
**Severity**: High
**Serbian Example**:
- **Draft (Pravilnik)**: "Taksa iznosi 5000 dinara"
- **Corpus (Uredba)**: "Taksa ne može biti veća od 3000 dinara"
- **Conflict**: Suprotnost sa višim propisom

### 3.9 Ministerial Order Conflict
**ID**: `ministerial_order_conflict`
**Description**: Draft conflicts with ministerial order hierarchy
**Severity**: Medium
**Serbian Example**:
- **Draft (Naređenje)**: "Postupak traje 15 dana"
- **Corpus (Pravilnik ministra)**: "Postupak traje 30 dana"
- **Conflict**: Neusklađenost u hijerarhiji

### 3.10 Local Ordinance Conflict
**ID**: `local_ordinance_conflict`
**Description**: Draft local ordinance conflicts with national law
**Severity**: High
**Serbian Example**:
- **Draft (Lokalna odluka)**: "Radna nedelja je 35 sati"
- **Corpus (Zakon)**: "Radna nedelja je 40 sati"
- **Conflict**: Lokalni propis u suprotnosti sa nacionalnim

### 3.11 Delegated Legislation Conflict
**ID**: `delegated_legislation_conflict`
**Description**: Draft exceeds delegated authority
**Severity**: High
**Serbian Example**:
- **Draft**: "Ministar određuje visinu plata"
- **Corpus**: "Ministar može propisati samo kriterijume"
- **Conflict**: Prekoračenje delegiranih ovlašćenja

### 3.12 Subsidiary Legislation Conflict
**ID**: `subsidiary_legislation_conflict`
**Description**: Draft subsidiary legislation conflicts with primary
**Severity**: High
**Serbian Example**:
- **Draft (Podzakonski akt)**: "Rok je 10 dana"
- **Corpus (Zakon)**: "Rok ne može biti kraći od 15 dana"
- **Conflict**: Podzakonski akt u suprotnosti sa zakonom

### 3.13 Administrative Rule Conflict
**ID**: `administrative_rule_conflict`
**Description**: Draft administrative rule conflicts with statute
**Severity**: Medium
**Serbian Example**:
- **Draft (Administrativno pravilo)**: "Zahtev se podnosi usmeno"
- **Corpus (Zakon)**: "Zahtev se podnosi u pisanoj formi"
- **Conflict**: Administrativno pravilo protivno zakonu

### 3.14 Executive Order Conflict
**ID**: `executive_order_conflict`
**Description**: Draft executive order conflicts with legislation
**Severity**: High
**Serbian Example**:
- **Draft (Izvršna naredba)**: "Suspendovati primenu zakona"
- **Corpus (Zakon)**: "Zakon se primenjuje u celosti"
- **Conflict**: Izvršna naredba protivna zakonu

### 3.15 Decree Conflict
**ID**: `decree_conflict`
**Description**: Draft decree conflicts with higher authority
**Severity**: High
**Serbian Example**:
- **Draft (Dekret)**: "Uvesti vanredno stanje"
- **Corpus (Ustav)**: "Vanredno stanje uvodi Skupština"
- **Conflict**: Dekret prekoračuje ovlašćenja

### 3.16 Resolution Conflict
**ID**: `resolution_conflict`
**Description**: Draft resolution conflicts with binding law
**Severity**: Medium
**Serbian Example**:
- **Draft (Rezolucija)**: "Preporučuje se primena novog postupka"
- **Corpus (Zakon)**: "Obavezan je postojeći postupak"
- **Conflict**: Rezolucija u suprotnosti sa obavezujućim propisom

### 3.17 Guideline Conflict
**ID**: `guideline_conflict`
**Description**: Draft guideline conflicts with mandatory rules
**Severity**: Low
**Serbian Example**:
- **Draft (Smernica)**: "Preporučuje se rok od 5 dana"
- **Corpus (Pravilnik)**: "Obavezan je rok od 15 dana"
- **Conflict**: Smernica u suprotnosti sa obavezujućim pravilom

### 3.18 Circular Conflict
**ID**: `circular_conflict`
**Description**: Draft circular conflicts with regulations
**Severity**: Low
**Serbian Example**:
- **Draft (Okružnica)**: "Postupiti po novoj proceduri"
- **Corpus (Pravilnik)**: "Obavezna je postojeća procedura"
- **Conflict**: Okružnica protivna pravilniku

---

## Category 4: Procedural Conflicts (16 types)

### 4.1 Application Procedure Conflict
**ID**: `application_procedure_conflict`
**Description**: Draft application procedure conflicts with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Zahtev se podnosi elektronski"
- **Corpus**: "Zahtev se podnosi lično ili poštom"
- **Conflict**: Različite procedure podnošenja

### 4.2 Appeal Procedure Conflict
**ID**: `appeal_procedure_conflict`
**Description**: Draft appeal procedure conflicts with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Žalba se podnosi u roku od 8 dana"
- **Corpus**: "Žalba se podnosi u roku od 15 dana"
- **Conflict**: Različite procedure žalbe

### 4.3 Review Procedure Conflict
**ID**: `review_procedure_conflict`
**Description**: Draft review procedure conflicts with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Preispitivanje vrši komisija od 3 člana"
- **Corpus**: "Preispitivanje vrši komisija od 5 članova"
- **Conflict**: Različite procedure preispitivanja

### 4.4 Approval Procedure Conflict
**ID**: `approval_procedure_conflict`
**Description**: Draft approval procedure conflicts with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Odobrenje daje direktor"
- **Corpus**: "Odobrenje daje upravni odbor"
- **Conflict**: Različite procedure odobravanja

### 4.5 Registration Procedure Conflict
**ID**: `registration_procedure_conflict`
**Description**: Draft registration procedure conflicts with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Registracija se vrši u roku od 3 dana"
- **Corpus**: "Registracija se vrši u roku od 8 dana"
- **Conflict**: Različite procedure registracije

### 4.6 Notification Procedure Conflict
**ID**: `notification_procedure_conflict`
**Description**: Draft notification procedure conflicts with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Obaveštenje se dostavlja SMS-om"
- **Corpus**: "Obaveštenje se dostavlja preporučenom poštom"
- **Conflict**: Različite procedure obaveštavanja

### 4.7 Consultation Procedure Conflict
**ID**: `consultation_procedure_conflict`
**Description**: Draft consultation procedure conflicts with corpus
**Severity**: Low
**Serbian Example**:
- **Draft**: "Konsultacije traju 15 dana"
- **Corpus**: "Konsultacije traju 30 dana"
- **Conflict**: Različite procedure konsultacija

### 4.8 Hearing Procedure Conflict
**ID**: `hearing_procedure_conflict`
**Description**: Draft hearing procedure conflicts with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Saslušanje se održava bez prisustva stranke"
- **Corpus**: "Stranka ima pravo prisustva na saslušanju"
- **Conflict**: Različite procedure saslušanja

### 4.9 Investigation Procedure Conflict
**ID**: `investigation_procedure_conflict`
**Description**: Draft investigation procedure conflicts with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Istraga traje do 30 dana"
- **Corpus**: "Istraga traje do 60 dana"
- **Conflict**: Različite procedure istrage

### 4.10 Inspection Procedure Conflict
**ID**: `inspection_procedure_conflict`
**Description**: Draft inspection procedure conflicts with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Inspekcijski nadzor se vrši bez najave"
- **Corpus**: "Inspekcijski nadzor se najavljuje 3 dana unapred"
- **Conflict**: Različite procedure inspekcije

### 4.11 Audit Procedure Conflict
**ID**: `audit_procedure_conflict`
**Description**: Draft audit procedure conflicts with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Revizija se vrši jednom godišnje"
- **Corpus**: "Revizija se vrši na svake 3 godine"
- **Conflict**: Različite procedure revizije

### 4.12 Complaint Procedure Conflict
**ID**: `complaint_procedure_conflict`
**Description**: Draft complaint procedure conflicts with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Pritužba se podnosi usmeno"
- **Corpus**: "Pritužba se podnosi u pisanoj formi"
- **Conflict**: Različite procedure pritužbe

### 4.13 Dispute Resolution Conflict
**ID**: `dispute_resolution_conflict`
**Description**: Draft dispute resolution conflicts with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Sporovi se rešavaju arbitražom"
- **Corpus**: "Sporovi se rešavaju pred sudom"
- **Conflict**: Različite procedure rešavanja sporova

### 4.14 Enforcement Procedure Conflict
**ID**: `enforcement_procedure_conflict`
**Description**: Draft enforcement procedure conflicts with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Izvršenje vrši poslodavac"
- **Corpus**: "Izvršenje vrši inspekcija rada"
- **Conflict**: Različite procedure izvršenja

### 4.15 Remediation Procedure Conflict
**ID**: `remediation_procedure_conflict`
**Description**: Draft remediation procedure conflicts with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Otklanjanje nedostataka u roku od 7 dana"
- **Corpus**: "Otklanjanje nedostataka u roku od 30 dana"
- **Conflict**: Različite procedure otklanjanja nedostataka

### 4.16 Termination Procedure Conflict
**ID**: `termination_procedure_conflict`
**Description**: Draft termination procedure conflicts with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Raskid ugovora bez obrazloženja"
- **Corpus**: "Raskid ugovora uz pisano obrazloženje"
- **Conflict**: Različite procedure raskida

---

## Category 5: Scope Conflicts (17 types)

### 5.1 Territorial Scope Conflict
**ID**: `territorial_scope_conflict`
**Description**: Draft territorial scope conflicts with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Primenjuje se na teritoriji opštine"
- **Corpus**: "Primenjuje se na teritoriji cele Republike"
- **Conflict**: Različit teritorijalni obuhvat

### 5.2 Personal Scope Conflict
**ID**: `personal_scope_conflict`
**Description**: Draft personal scope conflicts with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Odnosi se na zaposlene u privatnom sektoru"
- **Corpus**: "Odnosi se na sve zaposlene"
- **Conflict**: Različit personalni obuhvat

### 5.3 Material Scope Conflict
**ID**: `material_scope_conflict`
**Description**: Draft material scope conflicts with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Primenjuje se na ugovore o delu"
- **Corpus**: "Primenjuje se na sve vrste ugovora o radu"
- **Conflict**: Različit materijalni obuhvat

### 5.4 Temporal Scope Conflict
**ID**: `temporal_scope_conflict`
**Description**: Draft temporal scope conflicts with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Važi do 31. decembra 2025."
- **Corpus**: "Važi na neodređeno vreme"
- **Conflict**: Različit vremenski obuhvat

### 5.5 Subject Matter Conflict
**ID**: `subject_matter_conflict`
**Description**: Draft subject matter conflicts with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Reguliše radne odnose u poljoprivredi"
- **Corpus**: "Reguliše radne odnose u svim delatnostima"
- **Conflict**: Različit predmet regulisanja

### 5.6 Jurisdictional Overlap
**ID**: `jurisdictional_overlap`
**Description**: Draft jurisdiction overlaps with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Ministarstvo nadležno za izdavanje dozvola"
- **Corpus**: "Agencija nadležna za izdavanje dozvola"
- **Conflict**: Preklapanje nadležnosti

### 5.7 Authority Overlap
**ID**: `authority_overlap`
**Description**: Draft authority overlaps with corpus authority
**Severity**: High
**Serbian Example**:
- **Draft**: "Direktor donosi odluke o zapošljavanju"
- **Corpus**: "Upravni odbor donosi odluke o zapošljavanju"
- **Conflict**: Preklapanje ovlašćenja

### 5.8 Competence Conflict
**ID**: `competence_conflict`
**Description**: Draft competence conflicts with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Lokalna samouprava nadležna za inspekciju"
- **Corpus**: "Republika nadležna za inspekciju"
- **Conflict**: Konflikt nadležnosti

### 5.9 Coverage Conflict
**ID**: `coverage_conflict`
**Description**: Draft coverage conflicts with corpus coverage
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Obuhvata preduzeća sa više od 50 zaposlenih"
- **Corpus**: "Obuhvata sva preduzeća"
- **Conflict**: Različit obuhvat primene

### 5.10 Applicability Conflict
**ID**: `applicability_conflict`
**Description**: Draft applicability conflicts with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Primenjuje se na nove ugovore"
- **Corpus**: "Primenjuje se na sve ugovore"
- **Conflict**: Različita primenljivost

### 5.11 Exclusion Conflict
**ID**: `exclusion_conflict`
**Description**: Draft exclusions conflict with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Isključeni su sezonski radnici"
- **Corpus**: "Obuhvaćeni su svi radnici uključujući sezonske"
- **Conflict**: Konfliktna isključenja

### 5.12 Exemption Conflict
**ID**: `exemption_conflict`
**Description**: Draft exemptions conflict with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Izuzeta su mala preduzeća"
- **Corpus**: "Nema izuzetaka po veličini preduzeća"
- **Conflict**: Konfliktna izuzeća

### 5.13 Derogation Conflict
**ID**: `derogation_conflict`
**Description**: Draft derogations conflict with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Odstupa se od obaveze plaćanja doprinosa"
- **Corpus**: "Obaveza plaćanja doprinosa je bezuslovna"
- **Conflict**: Konfliktna odstupanja

### 5.14 Waiver Conflict
**ID**: `waiver_conflict`
**Description**: Draft waivers conflict with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Moguće je odricanje od prava na godišnji odmor"
- **Corpus**: "Pravo na godišnji odmor je neprenosivo i neotuđivo"
- **Conflict**: Konfliktno odricanje

### 5.15 Limitation Scope Conflict
**ID**: `limitation_scope_conflict`
**Description**: Draft limitation scope conflicts with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Ograničenje važi za sve zaposlene"
- **Corpus**: "Ograničenje važi samo za rukovodioce"
- **Conflict**: Različit obuhvat ograničenja

### 5.16 Restriction Scope Conflict
**ID**: `restriction_scope_conflict`
**Description**: Draft restriction scope conflicts with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Zabrana konkurencije važi 1 godinu"
- **Corpus**: "Zabrana konkurencije važi 2 godine"
- **Conflict**: Različit obuhvat restrikcije

### 5.17 Prohibition Scope Conflict
**ID**: `prohibition_scope_conflict`
**Description**: Draft prohibition scope conflicts with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Zabranjeno zapošljavanje stranaca"
- **Corpus**: "Dozvoljeno zapošljavanje stranaca uz dozvolu"
- **Conflict**: Različit obuhvat zabrane

---

## Category 6: Penalty Conflicts (14 types)

### 6.1 Fine Amount Conflict
**ID**: `fine_amount_conflict`
**Description**: Draft fine amount conflicts with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Novčana kazna od 50.000 do 100.000 dinara"
- **Corpus**: "Novčana kazna od 100.000 do 500.000 dinara"
- **Conflict**: Različite visine novčanih kazni

### 6.2 Penalty Type Conflict
**ID**: `penalty_type_conflict`
**Description**: Draft penalty type conflicts with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Kazna je opomena"
- **Corpus**: "Kazna je novčana kazna"
- **Conflict**: Različite vrste kazni

### 6.3 Sanction Severity Conflict
**ID**: `sanction_severity_conflict`
**Description**: Draft sanction severity conflicts with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Laka povreda - opomena"
- **Corpus**: "Laka povreda - novčana kazna"
- **Conflict**: Različita težina sankcija

### 6.4 Enforcement Mechanism Conflict
**ID**: `enforcement_mechanism_conflict`
**Description**: Draft enforcement mechanism conflicts with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Izvršenje vrši poslodavac"
- **Corpus**: "Izvršenje vrši inspekcija rada"
- **Conflict**: Različiti mehanizmi izvršenja

### 6.5 Compliance Measure Conflict
**ID**: `compliance_measure_conflict`
**Description**: Draft compliance measures conflict with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Usklađivanje u roku od 15 dana"
- **Corpus**: "Usklađivanje u roku od 30 dana"
- **Conflict**: Različite mere usklađivanja

### 6.6 Corrective Action Conflict
**ID**: `corrective_action_conflict`
**Description**: Draft corrective actions conflict with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Korektivna mera je pisana opomena"
- **Corpus**: "Korektivna mera je privremena zabrana rada"
- **Conflict**: Različite korektivne mere

### 6.7 Suspension Sanction Conflict
**ID**: `suspension_sanction_conflict`
**Description**: Draft suspension sanctions conflict with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Suspenzija dozvole na 30 dana"
- **Corpus**: "Suspenzija dozvole na 90 dana"
- **Conflict**: Različite sankcije suspenzije

### 6.8 Revocation Sanction Conflict
**ID**: `revocation_sanction_conflict`
**Description**: Draft revocation sanctions conflict with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Oduzimanje dozvole na 6 meseci"
- **Corpus**: "Oduzimanje dozvole trajno"
- **Conflict**: Različite sankcije oduzimanja

### 6.9 Disqualification Conflict
**ID**: `disqualification_conflict`
**Description**: Draft disqualification conflicts with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Diskvalifikacija na 1 godinu"
- **Corpus**: "Diskvalifikacija na 3 godine"
- **Conflict**: Različiti periodi diskvalifikacije

### 6.10 Imprisonment Conflict
**ID**: `imprisonment_conflict`
**Description**: Draft imprisonment terms conflict with corpus
**Severity**: Critical
**Serbian Example**:
- **Draft**: "Kazna zatvora do 6 meseci"
- **Corpus**: "Kazna zatvora od 1 do 3 godine"
- **Conflict**: Različite kazne zatvora

### 6.11 Community Service Conflict
**ID**: `community_service_conflict`
**Description**: Draft community service conflicts with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Rad u javnom interesu 40 sati"
- **Corpus**: "Rad u javnom interesu 120 sati"
- **Conflict**: Različite kazne rada u javnom interesu

### 6.12 Probation Conflict
**ID**: `probation_conflict`
**Description**: Draft probation terms conflict with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Uslovna osuda sa rokom provere od 6 meseci"
- **Corpus**: "Uslovna osuda sa rokom provere od 1 godine"
- **Conflict**: Različiti uslovi uslovne osude

### 6.13 Restitution Conflict
**ID**: `restitution_conflict`
**Description**: Draft restitution requirements conflict with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Naknada štete u iznosu stvarne štete"
- **Corpus**: "Naknada štete uključuje i izgubljenu dobit"
- **Conflict**: Različiti zahtevi za naknadu

### 6.14 Damages Conflict
**ID**: `damages_conflict`
**Description**: Draft damages provisions conflict with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Odšteta do 100.000 dinara"
- **Corpus**: "Odšteta do pune vrednosti štete"
- **Conflict**: Različite odredbe o odšteti

---

## Category 7: Definitional Conflicts (16 types)

### 7.1 Term Definition Conflict
**ID**: `term_definition_conflict`
**Description**: Draft defines term differently than corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Radnik je lice koje obavlja poslove na osnovu ugovora o delu"
- **Corpus**: "Radnik je lice koje obavlja poslove na osnovu ugovora o radu"
- **Conflict**: Različite definicije pojma

### 7.2 Concept Interpretation Conflict
**ID**: `concept_interpretation_conflict`
**Description**: Draft interprets concept differently than corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Puno radno vreme je 35 sati nedeljno"
- **Corpus**: "Puno radno vreme je 40 sati nedeljno"
- **Conflict**: Različito tumačenje koncepta

### 7.3 Classification Conflict
**ID**: `classification_conflict`
**Description**: Draft classification conflicts with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Menadžeri se smatraju radnicima"
- **Corpus**: "Menadžeri se ne smatraju radnicima"
- **Conflict**: Različita klasifikacija

### 7.4 Categorization Conflict
**ID**: `categorization_conflict`
**Description**: Draft categorization conflicts with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Sezonski rad spada u privremene poslove"
- **Corpus**: "Sezonski rad spada u stalne poslove"
- **Conflict**: Različita kategorizacija

### 7.5 Terminology Inconsistency
**ID**: `terminology_inconsistency`
**Description**: Draft uses inconsistent terminology
**Severity**: Low
**Serbian Example**:
- **Draft**: "Zaposleni" i "radnik" koriste se naizmenično
- **Corpus**: Koristi se isključivo termin "zaposleni"
- **Conflict**: Nedosledna terminologija

### 7.6 Reference Ambiguity
**ID**: `reference_ambiguity`
**Description**: Draft reference is ambiguous
**Severity**: Medium
**Serbian Example**:
- **Draft**: "U skladu sa propisima"
- **Corpus**: "U skladu sa Zakonom o radu, član 45"
- **Conflict**: Nejasna referenca

### 7.7 Cross-Reference Conflict
**ID**: `cross_reference_conflict`
**Description**: Draft cross-reference conflicts with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Primenjuje se član 10 ovog pravilnika"
- **Corpus**: "Primenjuje se član 15 zakona"
- **Conflict**: Konfliktne unakrsne reference

### 7.8 Citation Conflict
**ID**: `citation_conflict`
**Description**: Draft citation conflicts with corpus
**Severity**: Low
**Serbian Example**:
- **Draft**: "Prema članu 5 Zakona o radu"
- **Corpus**: "Član 5 Zakona o radu je stavljen van snage"
- **Conflict**: Pogrešno citiranje

### 7.9 Incorporation Conflict
**ID**: `incorporation_conflict`
**Description**: Draft incorporation conflicts with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Uključuje odredbe Pravilnika iz 2020."
- **Corpus**: "Pravilnik iz 2020. je stavljen van snage"
- **Conflict**: Konfliktno uključivanje

### 7.10 Adoption Conflict
**ID**: `adoption_conflict`
**Description**: Draft adoption conflicts with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Usvaja se procedura iz 2019."
- **Corpus**: "Procedura iz 2019. je zamenjena novom"
- **Conflict**: Konfliktno usvajanje

### 7.11 Interpretation Rule Conflict
**ID**: `interpretation_rule_conflict`
**Description**: Draft interpretation rules conflict with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Tumači se restriktivno"
- **Corpus**: "Tumači se ekstenzivno"
- **Conflict**: Različita pravila tumačenja

### 7.12 Construction Rule Conflict
**ID**: `construction_rule_conflict`
**Description**: Draft construction rules conflict with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Primenjuje se gramatičko tumačenje"
- **Corpus**: "Primenjuje se teleološko tumačenje"
- **Conflict**: Različita pravila konstrukcije

### 7.13 Presumption Conflict
**ID**: `presumption_conflict`
**Description**: Draft presumptions conflict with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Pretpostavlja se krivica"
- **Corpus**: "Pretpostavlja se nevinost"
- **Conflict**: Konfliktne presumpcije

### 7.14 Inference Conflict
**ID**: `inference_conflict`
**Description**: Draft inferences conflict with corpus
**Severity**: Low
**Serbian Example**:
- **Draft**: "Iz ćutanja se zaključuje saglasnost"
- **Corpus**: "Potrebna je izričita saglasnost"
- **Conflict**: Konfliktni zaključci

### 7.15 Implication Conflict
**ID**: `implication_conflict`
**Description**: Draft implications conflict with corpus
**Severity**: Low
**Serbian Example**:
- **Draft**: "Podrazumeva se prihvatanje"
- **Corpus**: "Potrebno je eksplicitno prihvatanje"
- **Conflict**: Konfliktne implikacije

### 7.16 Meaning Conflict
**ID**: `meaning_conflict`
**Description**: Draft meaning conflicts with corpus meaning
**Severity**: Medium
**Serbian Example**:
- **Draft**: "'Odmah' znači u roku od 24 sata"
- **Corpus**: "'Odmah' znači bez odlaganja"
- **Conflict**: Različito značenje termina

---

## Category 8: Implementation Conflicts (15 types)

### 8.1 Resource Allocation Conflict
**ID**: `resource_allocation_conflict`
**Description**: Draft resource allocation conflicts with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Budžet za 2024: 10 miliona dinara"
- **Corpus**: "Budžet za 2024: 5 miliona dinara"
- **Conflict**: Konfliktna alokacija resursa

### 8.2 Budget Conflict
**ID**: `budget_conflict`
**Description**: Draft budget conflicts with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Godišnji budžet: 50 miliona dinara"
- **Corpus**: "Godišnji budžet: 30 miliona dinara"
- **Conflict**: Konfliktni budžet

### 8.3 Funding Conflict
**ID**: `funding_conflict`
**Description**: Draft funding conflicts with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Finansira se iz republičkog budžeta"
- **Corpus**: "Finansira se iz lokalnog budžeta"
- **Conflict**: Konfliktno finansiranje

### 8.4 Personnel Conflict
**ID**: `personnel_conflict`
**Description**: Draft personnel requirements conflict with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Potrebno 50 zaposlenih"
- **Corpus**: "Maksimalno 30 zaposlenih"
- **Conflict**: Konfliktni kadrovski zahtevi

### 8.5 Infrastructure Conflict
**ID**: `infrastructure_conflict`
**Description**: Draft infrastructure conflicts with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Potrebna nova zgrada"
- **Corpus**: "Koristi se postojeća zgrada"
- **Conflict**: Konfliktna infrastruktura

### 8.6 Technology Conflict
**ID**: `technology_conflict`
**Description**: Draft technology conflicts with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Koristi se blockchain tehnologija"
- **Corpus**: "Koristi se tradicionalna baza podataka"
- **Conflict**: Konfliktna tehnologija

### 8.7 Timeline Conflict
**ID**: `timeline_conflict`
**Description**: Draft timeline conflicts with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Implementacija do 31.12.2024."
- **Corpus**: "Implementacija do 30.06.2025."
- **Conflict**: Konfliktni rokovi

### 8.8 Phasing Conflict
**ID**: `phasing_conflict`
**Description**: Draft phasing conflicts with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Faza 1: Januar-Mart, Faza 2: April-Jun"
- **Corpus**: "Faza 1: Januar-Jun, Faza 2: Jul-Dec"
- **Conflict**: Konfliktne faze implementacije

### 8.9 Milestone Conflict
**ID**: `milestone_conflict`
**Description**: Draft milestones conflict with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Ključni datum: 1. april 2024."
- **Corpus**: "Ključni datum: 1. jul 2024."
- **Conflict**: Konfliktni mejlstoni

### 8.10 Capacity Conflict
**ID**: `capacity_conflict`
**Description**: Draft capacity conflicts with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Kapacitet: 1000 korisnika dnevno"
- **Corpus**: "Maksimalni kapacitet: 500 korisnika dnevno"
- **Conflict**: Konfliktni kapacitet

### 8.11 Scalability Conflict
**ID**: `scalability_conflict`
**Description**: Draft scalability conflicts with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Sistem mora podržati 10,000 korisnika"
- **Corpus**: "Sistem podržava do 5,000 korisnika"
- **Conflict**: Konfliktna skalabilnost

### 8.12 Performance Conflict
**ID**: `performance_conflict`
**Description**: Draft performance requirements conflict with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Vreme odgovora: maksimalno 1 sekunda"
- **Corpus**: "Vreme odgovora: do 5 sekundi"
- **Conflict**: Konfliktni performanse

### 8.13 Availability Conflict
**ID**: `availability_conflict`
**Description**: Draft availability conflicts with corpus
**Severity**: High
**Serbian Example**:
- **Draft**: "Dostupnost: 99.9% (24/7)"
- **Corpus**: "Dostupnost: radnim danima 8-16h"
- **Conflict**: Konfliktna dostupnost

### 8.14 Reliability Conflict
**ID**: `reliability_conflict`
**Description**: Draft reliability conflicts with corpus
**Severity**: Medium
**Serbian Example**:
- **Draft**: "Maksimalno 1 sat nedostupnosti godišnje"
- **Corpus**: "Dozvoljeno 24 sata nedostupnosti godišnje"
- **Conflict**: Konfliktna pouzdanost

### 8.15 Maintenance Conflict
**ID**: `maintenance_conflict`
**Description**: Draft maintenance conflicts with corpus
**Severity**: Low
**Serbian Example**:
- **Draft**: "Održavanje svake nedelje"
- **Corpus**: "Održavanje jednom mesečno"
- **Conflict**: Konfliktno održavanje

---

## Summary

This specification defines **127 conflict types** across **8 categories**:

1. **Normative Conflicts** (20 types) - Core legal contradictions
2. **Temporal Conflicts** (15 types) - Time-related issues
3. **Hierarchical Conflicts** (12 types) - Authority and precedence
4. **Procedural Conflicts** (20 types) - Process and procedure issues
5. **Definitional Conflicts** (15 types) - Term and concept conflicts
6. **Scope Conflicts** (14 types) - Coverage and applicability
7. **Interpretive Conflicts** (16 types) - Meaning and interpretation
8. **Implementation Conflicts** (15 types) - Practical execution issues

Each conflict type includes:
- Unique identifier for programmatic use
- Clear description of the conflict nature
- Severity level (Critical, High, Medium, Low)
- **Serbian language example** showing draft vs corpus conflict

These conflict types form the foundation of ZAIKON's automated legal compliance review system, enabling comprehensive detection of inconsistencies between draft regulations and existing legal corpus.

