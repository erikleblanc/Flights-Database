# Flights-Database

## Restriksjoner som uttrykkes i databasen

### Primærnøkler / unike kombinasjoner

Vi bruker PRIMARY KEY for entiteter som Flyselskap(flyselskapskode), Flytype(flytype_navn), etc.
For Fly, har vi en primærnøkkel på registreringsnummer, samt en unik kombinasjon (serienummer, flyselskapskode).
For Flyvning, er (flyrutenummer, lopenummer) en sammensatt primærnøkkel.

### Fremmednøkler

Fly.flyselskapskode -> Flyselskap(flyselskapskode), som sikrer at alle fly faktisk eies av et gyldig flyselskap.
Billett refererer til (flyrutenummer, flyvning_lopenr) i Flyvning, slik at en billett må peke på en gyldig flyvning.
ON DELETE og ON UPDATE‐regler (f.eks. RESTRICT, CASCADE, SET NULL) spesifiserer hvordan databasen håndterer sletting/oppdatering av rader i relaterte tabeller.

### Trigger for spesifikk forretningsregel

En BEFORE INSERT‐trigger på Billett som avviser oppretting dersom flyvningen ikke er 'planned'.
Dette håndhever regelen om at “Billettsalg kun er lov hvis status = 'planned'”.

## Restriksjoner som ikke er fullt uttrykt i databasen

### Ikke overskride flyets setekapasitet

Hvis et fly har 80 seter, må du sjekke hvor mange billetter (evt. seter) er allerede solgt til en bestemt flyvning, og nekte salg hvis alt er fullt.
Dette krever enten (A) en trigger som summerer antall billetter ved INSERT, eller (B) logikk i applikasjonen som teller solgte billetter før man oppretter en ny.
I praksis er det ofte enklere å gjøre dette i applikasjonslaget.

### En rute ikke fløyet mer enn én gang per dag

Hvis man vil hindre at (flyrutenummer, dato) dukker opp to ganger med forskjellig løpenummer, kunne man laget en UNIQUE(flyrutenummer, dato)‐constraint. Men hvis løpenummer skal kunne differensiere flere avganger samme dag, passer det dårlig.
I mange tilfeller styres dette i programlogikk: “Ved innlegging av en ny flyvning, sjekk om det allerede finnes en Flyvning med samme (rute, dato). Hvis det ikke skal være lov, avvis.”

### Dato-/tidsregler

Man kan si “sluttdato i Flyrute må være lik eller etter oppstartsdato”, eller “faktisk_avgang kan ikke være før datoens planlagte start.” Slike ting krever ofte en CHECK‐constraint med ganske omstendelig håndtering av datotyper, eller en trigger.
Når dato ofte lagres som TEXT i SQLite, er dette spesielt vanskelig å håndheve.

### InnsjekketBagasje vs. Bagasje

Diagrammet kaller entiteten «InnsjekketBagasje (Registreringsnr, Vekt, Innleveringstid)».
I koden heter tabellen bare Bagasje med bagasje_id som PK.
