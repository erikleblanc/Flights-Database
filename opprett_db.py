import sqlite3
import os

print("Current working directory:", os.getcwd()) # Hvor er vi?

def opprett_database(db_fil="flydb.sqlite"):
    # Åpne / opprett SQLite-database:
    conn = sqlite3.connect(db_fil)
    cur = conn.cursor()

    # Aktiver FK-håndheving i SQLite:
    cur.execute("PRAGMA foreign_keys = ON;")

    # -- Sletter tabeller i riktig rekkefølge --
    cur.execute("DROP TABLE IF EXISTS Bagasje;")
    cur.execute("DROP TABLE IF EXISTS Billett;")
    cur.execute("DROP TABLE IF EXISTS Bestilling;")
    cur.execute("DROP TABLE IF EXISTS Flyvning;")
    cur.execute("DROP TABLE IF EXISTS Flyrute;")
    cur.execute("DROP TABLE IF EXISTS Flyplass;")
    cur.execute("DROP TABLE IF EXISTS Fly;")
    cur.execute("DROP TABLE IF EXISTS Flytype;")
    cur.execute("DROP TABLE IF EXISTS Flyprodusent;")
    cur.execute("DROP TABLE IF EXISTS Flyselskap;")
    cur.execute("DROP TABLE IF EXISTS Kunde;")

    # -- Opprett tabeller, please husk riktig rekkefølge hvis dere endrer --

    # 1) Flyselskap
    cur.execute("""
    CREATE TABLE Flyselskap (
        flyselskapskode  TEXT PRIMARY KEY,
        navn             TEXT NOT NULL
    );
    """)

    # 2) Flyprodusent
    cur.execute("""
    CREATE TABLE Flyprodusent (
        produsentnavn  TEXT PRIMARY KEY,
        nasjonalitet   TEXT,
        stiftelsesaar  INTEGER
    );
    """)

    # 3) Flytype
    cur.execute("""
    CREATE TABLE Flytype (
        flytype_navn     TEXT PRIMARY KEY,
        produsentnavn    TEXT NOT NULL,
        produksjonsstart INTEGER NOT NULL,
        produksjonslutt  INTEGER,
        setekonfig       TEXT,
        FOREIGN KEY (produsentnavn)
          REFERENCES Flyprodusent(produsentnavn)
          ON DELETE RESTRICT
          ON UPDATE CASCADE
    );
    """)

    # 4) Fly
    cur.execute("""
    CREATE TABLE Fly (
        registreringsnummer   TEXT PRIMARY KEY,
        serienummer           INTEGER NOT NULL,
        navn                  TEXT,
        aar_drift             INTEGER,
        seter                 INTEGER,
        flyselskapskode       TEXT NOT NULL,
        flytype_navn          TEXT NOT NULL,
        UNIQUE (serienummer, flyselskapskode),

        FOREIGN KEY (flyselskapskode)
          REFERENCES Flyselskap(flyselskapskode)
          ON DELETE RESTRICT
          ON UPDATE CASCADE,

        FOREIGN KEY (flytype_navn)
          REFERENCES Flytype(flytype_navn)
          ON DELETE RESTRICT
          ON UPDATE CASCADE
    );
    """)

    # 5) Flyplass
    cur.execute("""
    CREATE TABLE Flyplass (
        flyplasskode  TEXT PRIMARY KEY,
        navn          TEXT NOT NULL
    );
    """)

    # 6) Flyrute
    cur.execute("""
    CREATE TABLE Flyrute (
        flyrutenummer    TEXT PRIMARY KEY,
        flyselskapskode  TEXT NOT NULL,
        flytype_navn     TEXT NOT NULL,
        ukedagskode      TEXT,
        planlagt_avgang  TEXT,
        planlagt_ankomst TEXT,
        oppstartsdato    TEXT,
        sluttdato        TEXT,

        FOREIGN KEY (flyselskapskode)
          REFERENCES Flyselskap(flyselskapskode)
          ON DELETE RESTRICT
          ON UPDATE CASCADE,

        FOREIGN KEY (flytype_navn)
          REFERENCES Flytype(flytype_navn)
          ON DELETE RESTRICT
          ON UPDATE CASCADE
    );
    """)

    # 7) Flyvning
    cur.execute("""
    CREATE TABLE Flyvning (
        flyrutenummer       TEXT NOT NULL,
        lopenummer          INTEGER NOT NULL,
        dato                TEXT NOT NULL,  -- YYYY-MM-DD
        status              TEXT NOT NULL DEFAULT 'planned',
        registreringsnummer TEXT,           -- referanse til Fly
        faktisk_avgang      TEXT,
        faktisk_ankomst     TEXT,
        PRIMARY KEY (flyrutenummer, lopenummer),  -- sammensatt PK

        FOREIGN KEY (flyrutenummer)
            REFERENCES Flyrute(flyrutenummer)
            ON DELETE RESTRICT
            ON UPDATE CASCADE,

        FOREIGN KEY (registreringsnummer)
            REFERENCES Fly(registreringsnummer)
            ON DELETE SET NULL
            ON UPDATE CASCADE
    );
    """)

    # 8) Kunde
    cur.execute("""
    CREATE TABLE Kunde (
        kundenr          INTEGER PRIMARY KEY AUTOINCREMENT,
        navn             TEXT NOT NULL,
        telefon          TEXT,
        epost            TEXT,
        nasjonalitet     TEXT,
        flyselskapkode_loyal TEXT,

        FOREIGN KEY (flyselskapkode_loyal)
          REFERENCES Flyselskap(flyselskapskode)
          ON DELETE SET NULL
          ON UPDATE CASCADE
    );
    """)

    # 9) Bestilling
    cur.execute("""
    CREATE TABLE Bestilling (
        bestilling_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        kundenr         INTEGER NOT NULL,
        bestillingsdato TEXT NOT NULL,
        totalpris       REAL,
        type_reise      TEXT,

        FOREIGN KEY (kundenr)
          REFERENCES Kunde(kundenr)
          ON DELETE CASCADE
          ON UPDATE CASCADE
    );
    """)

    # 10) Billett
    # Fikk billett til å peke på de to kolonnene i Flyvning som utgjør PK.
    cur.execute("""
    CREATE TABLE Billett (
        billett_id       INTEGER PRIMARY KEY AUTOINCREMENT,
        bestilling_id    INTEGER NOT NULL,
        flyrutenummer    TEXT NOT NULL,
        flyvning_lopenr  INTEGER NOT NULL,
        billettkategori  TEXT,
        pris_charged     REAL,
        sete             TEXT,
        
        FOREIGN KEY (bestilling_id)
          REFERENCES Bestilling(bestilling_id)
          ON DELETE CASCADE
          ON UPDATE CASCADE,

        FOREIGN KEY (flyrutenummer, flyvning_lopenr)
          REFERENCES Flyvning(flyrutenummer, lopenummer)
          ON DELETE RESTRICT
          ON UPDATE CASCADE
    );
    """)

    # 11) Bagasje
    cur.execute("""
    CREATE TABLE Bagasje (
        bagasje_id   INTEGER PRIMARY KEY AUTOINCREMENT,
        billett_id   INTEGER NOT NULL,
        vekt         REAL,
        innsjekk_tid TEXT NOT NULL,

        FOREIGN KEY (billett_id)
          REFERENCES Billett(billett_id)
          ON DELETE CASCADE
          ON UPDATE CASCADE
    );
    """)

    # ============= TRIGGER  =============
    cur.execute("""
    CREATE TRIGGER ensure_planned_flyvning -- Kun tillate billettkjøp for planlagt flyvning
    BEFORE INSERT ON Billett
    FOR EACH ROW
    BEGIN
        SELECT CASE
            WHEN (
                SELECT status
                FROM Flyvning
                WHERE flyrutenummer = NEW.flyrutenummer
                  AND lopenummer    = NEW.flyvning_lopenr
            ) != 'planned'
            THEN
                RAISE(ABORT, 'Kan ikke selge billett: Flyvning er ikke planned.')
        END;
    END;
    """)

    # -- Ferdigsnakka --
    conn.commit()
    conn.close()

if __name__ == "__main__":
    opprett_database()
    print("Database opprettet med tabeller i flydb.sqlite.")
