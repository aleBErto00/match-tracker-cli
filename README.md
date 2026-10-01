# Match Tracker CLI

Un'applicazione a riga di comando sviluppata in Python per la registrazione, l'archiviazione e l'analisi statistica delle partite sportive. Il sistema permette di tracciare risultati, calcolare metriche di rendimento e consultare lo storico dei match in modo rapido e strutturato.

---

## Funzionalita

- Registrazione Match: Inserimento guidato dei dati relativi a squadre, punteggio, data e note della partita.
- Analisi Statistica: Calcolo automatico di indicatori di prestazione (media gol, tasso di vittoria, risultati utili).
- Consultazione e Filtri: Ricerca nello storico per squadra, intervallo temporale o esito della partita.
- Persistenza Dati: Gestione della memorizzazione locale per conservare i dati tra diverse sessioni.

---

## Architettura del Progetto

Il codice e strutturato secondo il principio di separazione delle responsabilita:

```text
├── functions.py    Modulo logico contenente funzioni di calcolo, validazione e persistenza
├── main.py         Punto di ingresso dell'applicazione e gestione del menu interattivo
├── .gitignore      Regole di esclusione di file di cache e configurazioni
└── README.md       Documentazione del progetto