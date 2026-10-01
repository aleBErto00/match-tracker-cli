import json
import os
import re
import calendar
from datetime import date, datetime
import matplotlib.pyplot as plt

DB_FILE = "partite.json"

MESI_MAP = {
    "gennaio": 1, "febbraio": 2, "marzo": 3, "aprile": 4,
    "maggio": 5, "giugno": 6, "luglio": 7, "agosto": 8,
    "settembre": 9, "ottobre": 10, "novembre": 11, "dicembre": 12
}

def carica_archivio(filepath=DB_FILE) -> list[dict]:
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        dati = json.load(f)
    for m in dati:
        m["data"] = datetime.strptime(m["data"], "%Y-%m-%d").date()
    return dati

def salva_archivio(partite: list[dict], filepath=DB_FILE) -> None:
    dati = []
    for m in partite:
        copia = m.copy()
        copia["data"] = m["data"].isoformat()
        dati.append(copia)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(dati, f, indent=4, ensure_ascii=False)

def analizza_data(testo_data: str) -> date | None:
    # Rimuove eventuali punti finali (es. "3 marzo." -> "3 marzo")
    testo_data = testo_data.strip().rstrip(".").lower()
    anno_corrente = date.today().year

    m_num = re.match(r"^(\d{1,2})/(\d{1,2})$", testo_data)
    if m_num:
        try:
            return date(anno_corrente, int(m_num.group(2)), int(m_num.group(1)))
        except ValueError:
            return None

    m_txt = re.match(r"^(\d{1,2})\s+([a-z]+)$", testo_data)
    if m_txt:
        g = int(m_txt.group(1))
        mese_str = m_txt.group(2)
        if mese_str in MESI_MAP:
            try:
                return date(anno_corrente, MESI_MAP[mese_str], g)
            except ValueError:
                return None
    return None

def parsing_riga_flessibile(riga: str, data_corrente: date | None) -> tuple[dict | None, date | None]:
    riga = riga.replace("\xa0", " ").strip()
    if not riga:
        return None, data_corrente

    # Permette il punto facoltativo \.? dopo il mese/data (es: "3 marzo." o "03/03.")
    # e accetta qualsiasi carattere alfabetico/spazi nei nomi squadra ([^-\d]+)
    pattern_con_data = re.compile(
        r"^(\d{1,2}(?:\s+[a-zA-Z]+|\/\d{1,2})\.?)\s+([^-\d]+)-([^\d]+?)\s+(\d+)-(\d+)$"
    )
    match_data = pattern_con_data.match(riga)

    if match_data:
        str_data, casa, ospite, gc, go = match_data.groups()
        nuova_data = analizza_data(str_data)
        if nuova_data:
            return {
                "data": nuova_data,
                "casa": casa.strip(),
                "gol_casa": int(gc),
                "ospite": ospite.strip(),
                "gol_ospite": int(go)
            }, nuova_data

    # Caso riga senza data: eredita data_corrente
    pattern_senza_data = re.compile(r"^([^-\d]+)-([^\d]+?)\s+(\d+)-(\d+)$")
    match_senza = pattern_senza_data.match(riga)

    if match_senza and data_corrente is not None:
        casa, ospite, gc, go = match_senza.groups()
        return {
            "data": data_corrente,
            "casa": casa.strip(),
            "gol_casa": int(gc),
            "ospite": ospite.strip(),
            "gol_ospite": int(go)
        }, data_corrente

    return None, data_corrente

def inserisci_blocco_partite(archivio: list[dict], testo: str) -> int:
    conteggio = 0
    data_corrente = None
    for riga in testo.splitlines():
        riga_pulita = riga.replace("\xa0", " ").strip()
        if not riga_pulita:
            continue
        partita, data_corrente = parsing_riga_flessibile(riga_pulita, data_corrente)
        if partita:
            archivio.append(partita)
            conteggio += 1
    return conteggio

def conta_partite_squadra(partite: list[dict], squadra: str) -> int:
    sq = squadra.strip().lower()
    return sum(1 for m in partite if m["casa"].lower() == sq or m["ospite"].lower() == sq)

def conta_partite_mese(partite: list[dict], mese: int, anno: int) -> int:
    return sum(1 for m in partite if m["data"].month == mese and m["data"].year == anno)

def converti_input_mese(stringa_input: str) -> tuple[int, int] | None:
    parti = stringa_input.strip().lower().split()
    if not parti:
        return None
    nome_mese = parti[0]
    if nome_mese not in MESI_MAP:
        return None
    anno = int(parti[1]) if len(parti) > 1 and parti[1].isdigit() else date.today().year
    return MESI_MAP[nome_mese], anno

def mostra_grafico_squadra(partite: list[dict], squadra: str) -> None:
    sq = squadra.strip().lower()
    v, p, s = 0, 0, 0
    gf, gs = 0, 0

    for m in partite:
        is_casa = m["casa"].lower() == sq
        is_ospite = m["ospite"].lower() == sq
        if not (is_casa or is_ospite):
            continue

        fatti = m["gol_casa"] if is_casa else m["gol_ospite"]
        subiti = m["gol_ospite"] if is_casa else m["gol_casa"]
        gf += fatti
        gs += subiti

        if fatti > subiti:
            v += 1
        elif fatti == subiti:
            p += 1
        else:
            s += 1

    if (v + p + s) == 0:
        return

    dati_pie = [("Vittorie", v, "#4CAF50"), ("Pareggi", p, "#FFC107"), ("Sconfitte", s, "#F44336")]
    validi = [x for x in dati_pie if x[1] > 0]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    fig.canvas.manager.set_window_title(f"Statistiche: {squadra}")

    ax1.pie([x[1] for x in validi], labels=[x[0] for x in validi], autopct="%1.1f%%", colors=[x[2] for x in validi])
    ax1.set_title("Esiti Partite")

    ax2.bar(["Gol Fatti", "Gol Subiti"], [gf, gs], color=["#2196F3", "#FF9800"])
    ax2.set_title("Rapporto Gol")

    plt.tight_layout()
    plt.show()

    if (input()== "q"):
            plt.close()

def mostra_grafico_mensile(partite: list[dict], mese: int, anno: int) -> None:
    m_filtrate = [m for m in partite if m["data"].month == mese and m["data"].year == anno]
    if not m_filtrate:
        return

    _, tot_giorni = calendar.monthrange(anno, mese)
    partite_per_giorno = {p: 0 for p in range(1, tot_giorni + 1)}

    for m in m_filtrate:
        partite_per_giorno[m["data"].day] += 1

    giorni = list(partite_per_giorno.keys())
    tot_partite = list(partite_per_giorno.values())

    plt.figure(figsize=(10, 4))
    plt.gcf().canvas.manager.set_window_title(f"Statistiche Mese: {mese}/{anno}")
    plt.bar(giorni, tot_partite, color="#673AB7", edgecolor="black", width=0.7)
    plt.title(f"Distribuzione Partite ({mese}/{anno})")
    plt.xlabel("Giorno del Mese")
    plt.ylabel("Totale partite")
    plt.xticks(giorni)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()

    if (input() == "q"):
        plt.close()

def mostra_grafico_annuale_mesi(partite: list[dict], anno: int) -> None:
    m_filtrate = [m for m in partite if m["data"].year == anno]
    if not m_filtrate:
        return

    partite_per_mese = {m: 0 for m in range(1, 13)}
    for m in m_filtrate:
        partite_per_mese[m["data"].month] += 1

    mesi = list(partite_per_mese.keys())
    tot_partite = list(partite_per_mese.values())

    plt.figure(figsize=(10, 4))
    plt.gcf().canvas.manager.set_window_title(f"Statistiche Annuali: {anno}")
    plt.bar(mesi, tot_partite, color="#009688", edgecolor="black", width=0.7)
    plt.title(f"Distribuzione Partite ({anno})")
    plt.xlabel("Mese")
    plt.ylabel("Totale partite")
    plt.xticks(mesi, [calendar.month_name[m] for m in mesi], rotation=45)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()

    if (input() == "q"):
        plt.close()

def mostra_grafico_annuale_squadre(partite: list[dict], anno: int) -> None:
    conto_partite_squadre = {}
    for p in partite:
        squadra = p["casa"]
        conto_partite_squadre[squadra] = conto_partite_squadre.get(squadra, 0) + 1
        squadra = p["ospite"]
        conto_partite_squadre[squadra] = conto_partite_squadre.get(squadra, 0) + 1 
    
    conto_partite_squadre = {k: v for k, v in sorted(conto_partite_squadre.items(), key=lambda item: item[1], reverse=True)}
    
    plt.figure(figsize=(12, 6))
    plt.gcf().canvas.manager.set_window_title(f"Statistiche Squadre: {anno}")
    plt.bar(conto_partite_squadre.keys(), conto_partite_squadre.values(), color="#3F51B5", edgecolor="black")
    plt.title(f"Totale Partite per Squadra ({anno})")
    plt.xlabel("Squadra")
    plt.ylabel("Totale partite")
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()

    if (input() == "q"):
        plt.close()

def mostra_grafico_annuale_gol(partite: list[dict], anno: int) -> None:
    conto_gol_squadre = {}
    for p in partite:
        if p["data"].year == anno:
            squadra_casa = p["casa"]
            squadra_ospite = p["ospite"]
            conto_gol_squadre[squadra_casa] = conto_gol_squadre.get(squadra_casa, 0) + p["gol_casa"]
            conto_gol_squadre[squadra_ospite] = conto_gol_squadre.get(squadra_ospite, 0) + p["gol_ospite"]
    
    conto_gol_squadre = {k: v for k, v in sorted(conto_gol_squadre.items(), key=lambda item: item[1], reverse=True)}

    plt.figure(figsize=(12, 6))
    plt.pie(conto_gol_squadre.values(), labels=conto_gol_squadre.keys(), autopct="%1.1f%%", startangle=140)
    plt.title(f"Distribuzione Gol per Squadra ({anno})")
    plt.axis("equal")
    plt.tight_layout()
    plt.show()

    if (input() == "q"):
        plt.close()

def mostra_archivio(partite: list[dict]) -> None:
    if not partite:
        print("Archivio vuoto.")
        return
    sorted_partite = sorted(partite, key=lambda x: x["data"])
    for m in sorted_partite:
        print(f"{m['data'].strftime('%d/%m/%Y')} {m['casa']}-{m['ospite']} {m['gol_casa']}-{m['gol_ospite']}")

    totale_annuale = sum(1 for m in partite if m["data"].year == date.today().year)
    print(f"\nTotale partite annuali ({date.today().year}): {totale_annuale}")

def conta_gol_totali(partite: list[dict]) -> int:
    return sum(m["gol_casa"] + m["gol_ospite"] for m in partite)