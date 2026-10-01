from datetime import date
import functions as utils

def ramo_scrittura(archivio):
    print("\nIncolla le partite.")
    print("Quando hai terminato di incollare, digita 'FINE' e premi INVIO:\n")
    righe = []
    while True:
        try:
            riga = input()
        except EOFError:
            break
        if riga.strip().upper() == "FINE":
            break
        righe.append(riga)

    if righe:
        salvate = utils.inserisci_blocco_partite(archivio, "\n".join(righe))
        print(f"\n{salvate} partita/e registrata/e con successo.")
        utils.salva_archivio(archivio)
    else:
        print("Nessun dato inserito.")

def ramo_statistiche(archivio):
    if not archivio:
        print("Archivio vuoto.")
        return

    print("\n1. Statistiche per Squadra")
    print("2. Statistiche per Mese")
    print("3. Statistiche Annuali")
    scelta = input("Scegli: ").strip()

    if scelta == "1":
        squadra = input("Nome squadra: ").strip()
        tot = utils.conta_partite_squadra(archivio, squadra)
        print(f"Totale partite viste per {squadra}: {tot}")
        if tot > 0:
            print("Premi q per chiudere il grafico.")
            utils.mostra_grafico_squadra(archivio, squadra)

    elif scelta == "2":
        mese_input = input("Inserisci mese (es. 'gennaio' o 'gennaio 2026'): ").strip()
        risultato = utils.converti_input_mese(mese_input)
        print("Premi q per chiudere il grafico.")
        if not risultato:
            print("Mese non riconosciuto.")
            return

        num_mese, anno = risultato
        nome_mese_display = mese_input.split()[0].capitalize()
        tot = utils.conta_partite_mese(archivio, num_mese, anno)
        print(f"Totale partite viste per {nome_mese_display} {anno}: {tot}")
        if tot > 0:
            utils.mostra_grafico_mensile(archivio, num_mese, anno)

    elif scelta == "3":
        print("\nPremi 1 per il grafico dei mesi")
        print("Premi 2 per il grafico delle squadre")
        print("Premi 3 per il grafico dei gol")
        scelta_grafico = input("Inserisci un numero: ").strip()
        if scelta_grafico == "1":
            anno_input = input("Inserisci anno (es. '2026'): ").strip()
            if not anno_input.isdigit():
                print("Anno non valido.")
                return
            anno = int(anno_input)
            print("Premi q per chiudere il grafico.")
            utils.mostra_grafico_annuale_mesi(archivio, anno)
        elif scelta_grafico == "2":
            anno_input = input("Inserisci anno (es. '2026'): ").strip()
            if not anno_input.isdigit():
                print("Anno non valido.")
                return
            anno = int(anno_input)
            print("Premi q per chiudere il grafico.")
            utils.mostra_grafico_annuale_squadre(archivio, anno)
        elif scelta_grafico == "3":
            anno_input = input("Inserisci anno (es. '2026'): ").strip()
            if not anno_input.isdigit():
                print("Anno non valido.")
                return
            anno = int(anno_input)
            print ("Gol totali visti nell'anno {}: {}".format(anno, utils.conta_gol_totali([m for m in archivio if m["data"].year == anno])))
            print("Premi q per chiudere il grafico.")
            utils.mostra_grafico_annuale_gol(archivio, anno)

    else:
        print("Opzione non valida.")

def main():
    archivio = utils.carica_archivio()
    print(f"Caricate {len(archivio)} partite.")

    while True:
        print("\n=== MENU PRINCIPALE ===")
        print("1. Scrivi (Inserisci partite)")
        print("2. Stats (Controlla statistiche)")
        print("3. Mostra archivio")
        print("4. Esci")

        comando = input("Seleziona: ").strip()

        if comando == "1":
            ramo_scrittura(archivio)
        elif comando == "2":
            ramo_statistiche(archivio)
        elif comando == "3":
            if not archivio:
                print("L'archivio è vuoto.")
            else:
                utils.mostra_archivio(archivio)

        elif comando == "4":
            break
        else:
            print("Comando sconosciuto.")

if __name__ == "__main__":
    main()