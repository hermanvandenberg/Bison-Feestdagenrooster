"""Bison feestdagenrooster: wie werkt er met kerst en oud en nieuw?

Leest het jaarrooster (.xls) met de 35-daagse cyclus van de 5 ploegen en
rekent voor elk jaar uit welke ploeg dag, nacht, reserve of vrij heeft op
24, 25, 26 december, 31 december en 1 januari.

Gebruik:
    python scripts/analyse.py "bisonrooster 2027.xls" --van 2026 --tot 2126

Zonder rooster-bestand kan het ook: het patroon van 2027 zit in het script.
    python scripts/analyse.py --van 2026 --tot 2126

Maakt:
    output/bison_kerst_oudnieuw_<van>-<tot>.xlsx
    data/bison_diensten_<van>-<tot>.csv
"""
import argparse
import collections
import csv
import datetime as dt
import os

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

# Het rooster van 2027 heeft 35 kolommen (5 weken, maandag t/m zondag).
# 1 januari 2027 (vrijdag) staat in kolom 5, dus index 4.
REF = dt.date(2027, 1, 1)
REF_KOLOM = 4
CYCLUS = 35

# Patroon uit bisonrooster 2027.xls, Blad1 rij 29 t/m 33, kolom 1 t/m 35.
# D = dag, N = nacht, - = vrij. De letters R-E-S-E-R-V-E spellen over 7 dagen
# het woord RESERVE: dat is de reserveweek (bij ploeg 1 loopt die over de
# cyclusgrens: VE aan het begin, RESER aan het eind).
PATROON_2027 = {
    1: "VE--NNN--DD---DDNN---NN--DDD--RESER",
    2: "--DD---DDNN---NN--DDD--RESERVE--NNN",
    3: "NN--DDD--RESERVE--NNN--DD---DDNN---",
    4: "--RESERVE--NNN--DD---DDNN---NN--DDD",
    5: "DDNN---NN--DDD--RESERVE--NNN--DD---",
}

NAAM = {"D": "Dag", "N": "Nacht", "R": "Reserve", "-": "Vrij"}
KLEUR = {"D": "FFF2B3", "N": "B3C7FF", "R": "E0E0E0"}
WD = ["ma", "di", "wo", "do", "vr", "za", "zo"]


def lees_patroon(pad):
    """Leest het patroon uit het .xls-bestand (vereist xlrd)."""
    import xlrd

    s = xlrd.open_workbook(pad).sheet_by_index(0)
    return {int(s.cell_value(r, 0)): "".join(s.cell_value(r, c) or "-" for c in range(1, CYCLUS + 1)) for r in range(28, 33)}


def dienst(patroon, ploeg, datum):
    v = patroon[ploeg][((datum - REF).days + REF_KOLOM) % CYCLUS]
    if v in ("D", "N"):
        return v
    if v == "-":
        return "-"
    return "R"  # de letters R-E-S-E-R-V-E vormen samen de reserveweek


def feestdagen(jaar):
    return [
        (dt.date(jaar, 12, 24), "24 dec", "Kerst"),
        (dt.date(jaar, 12, 25), "25 dec", "Kerst"),
        (dt.date(jaar, 12, 26), "26 dec", "Kerst"),
        (dt.date(jaar, 12, 31), "31 dec", "Oud en nieuw"),
        (dt.date(jaar + 1, 1, 1), "1 jan", "Oud en nieuw"),
    ]


def controleer(P):
    """Controle tegen wat bekend is van het rooster 2027."""
    kerst = [dt.date(2027, 12, d) for d in (24, 25, 26)]
    assert all(dienst(P, 4, d) == "N" for d in kerst), "kerst 2027: ploeg 4 hoort nacht te hebben"
    assert all(dienst(P, 5, d) == "D" for d in kerst), "kerst 2027: ploeg 5 hoort dag te hebben"
    wissel = [dt.date(2027, 12, 31), dt.date(2028, 1, 1), dt.date(2028, 1, 2)]
    assert all(dienst(P, 2, d) == "D" for d in wissel), "jaarwisseling: ploeg 2 hoort dag te hebben"
    assert all(dienst(P, 3, d) == "N" for d in wissel), "jaarwisseling: ploeg 3 hoort nacht te hebben"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rooster", nargs="?", help="pad naar het jaarrooster (.xls); zonder dit wordt het patroon van 2027 gebruikt")
    ap.add_argument("--van", type=int, default=2026, help="eerste jaar (kerst van dat jaar), standaard 2026")
    ap.add_argument("--tot", type=int, default=2126, help="laatste jaar, inclusief, standaard 2126")
    ap.add_argument("--uit", default=".", help="map waarin data/ en output/ komen")
    a = ap.parse_args()
    if a.tot < a.van:
        ap.error("--tot moet gelijk aan of na --van liggen")

    P = lees_patroon(a.rooster) if a.rooster else PATROON_2027
    controleer(P)

    jaren = range(a.van, a.tot + 1)
    tag = f"{a.van}-{a.tot}"
    os.makedirs(os.path.join(a.uit, "data"), exist_ok=True)
    os.makedirs(os.path.join(a.uit, "output"), exist_ok=True)

    # CSV: een rij per jaar, datum en ploeg
    with open(os.path.join(a.uit, "data", f"bison_diensten_{tag}.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["jaar", "datum", "dag", "periode", "ploeg", "dienst"])
        for y in jaren:
            for d, lab, per in feestdagen(y):
                for p in range(1, 6):
                    w.writerow([y, d.isoformat(), lab, per, p, NAAM[dienst(P, p, d)]])

    wb = Workbook()

    # Per datum: wie heeft dag, nacht, reserve, vrij
    x = wb.active
    x.title = "Per datum"
    x.append(["Jaar", "Datum", "Dag", "Dagdienst", "Nachtdienst", "Reserve", "Vrij"])
    for y in jaren:
        for d, _, _ in feestdagen(y):
            g = collections.defaultdict(list)
            for p in range(1, 6):
                g[dienst(P, p, d)].append(str(p))
            f = lambda k: "Ploeg " + ", ".join(g[k]) if g[k] else "-"
            x.append([y, d.strftime("%d-%m-%Y"), WD[d.weekday()], f("D"), f("N"), f("R"), f("-")])
            x.cell(x.max_row, 4).fill = PatternFill("solid", fgColor=KLEUR["D"])
            x.cell(x.max_row, 5).fill = PatternFill("solid", fgColor=KLEUR["N"])
        x.append([])
    for col, wdt in zip("ABCDEFG", [7, 12, 5, 13, 13, 11, 16]):
        x.column_dimensions[col].width = wdt

    # Per ploeg: per jaar wat die ploeg op elke datum heeft
    q = wb.create_sheet("Per ploeg")
    q.append(["Ploeg", "Jaar", "24 dec", "25 dec", "26 dec", "31 dec", "1 jan", "Dag", "Nacht", "Totaal"])
    tot = {p: collections.Counter() for p in range(1, 6)}
    for p in range(1, 6):
        for y in jaren:
            v = [dienst(P, p, d) for d, _, _ in feestdagen(y)]
            q.append([p, y] + [NAAM[k] for k in v] + [v.count("D"), v.count("N"), v.count("D") + v.count("N")])
            for i, k in enumerate(v):
                if k in KLEUR:
                    q.cell(q.max_row, 3 + i).fill = PatternFill("solid", fgColor=KLEUR[k])
                if k in ("D", "N"):
                    tot[p][("kerst" if i < 3 else "on") + k] += 1
                if k == "R":
                    tot[p]["R"] += 1
            if v[3] == "N":
                tot[p]["oudejaarsnacht"] += 1
            if "D" not in v and "N" not in v:
                tot[p]["jaren_vrij"] += 1
                if "R" not in v:
                    tot[p]["jaren_helemaal_vrij"] += 1
        q.append([])

    # Totalen
    t = wb.create_sheet(f"Totaal {tag}")
    t.append(["Ploeg", "Kerst dag", "Kerst nacht", "O&N dag", "O&N nacht", "Totaal diensten", "Oudejaarsnacht", "Reservedagen",
              "Jaren zonder dienst", "Jaren helemaal vrij"])
    for p in range(1, 6):
        c = tot[p]
        som = c["kerstD"] + c["kerstN"] + c["onD"] + c["onN"]
        t.append([p, c["kerstD"], c["kerstN"], c["onD"], c["onN"], som, c["oudejaarsnacht"], c["R"],
                  c["jaren_vrij"], c["jaren_helemaal_vrij"]])
    t.append([])
    t.append(["Jaren zonder dienst: geen dag- of nachtdienst op alle vijf feestdagen. Helemaal vrij: ook geen reserve."])
    t.append(["D = dagdienst, N = nachtdienst. Aanname: de 35-daagse cyclus van het rooster 2027 loopt ongewijzigd door."])
    for ws in (x, q, t):
        for c in ws[1]:
            c.font = Font(bold=True)
    wb.save(os.path.join(a.uit, "output", f"bison_kerst_oudnieuw_{tag}.xlsx"))

    print(f"Totaal {tag} (kerst = 24/25/26 dec, oud en nieuw = 31 dec/1 jan):")
    for p in range(1, 6):
        c = tot[p]
        som = c["kerstD"] + c["kerstN"] + c["onD"] + c["onN"]
        print(f"  ploeg {p}: kerst {c['kerstD']} dag / {c['kerstN']} nacht, "
              f"oud en nieuw {c['onD']} dag / {c['onN']} nacht, totaal {som}, "
              f"jaren zonder dienst {c['jaren_vrij']} (helemaal vrij {c['jaren_helemaal_vrij']})")


if __name__ == "__main__":
    main()
