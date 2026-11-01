# Bison feestdagenrooster

Wie van de Bison werkt er met kerst (24, 25 en 26 december) en oud en nieuw (31 december en 1 januari), en is dat over de jaren eerlijk verdeeld tussen de 5 ploegen?

**Dashboard:** https://hermanvandenberg.github.io/Bison-Feestdagenrooster/ (kies zelf hoe ver vooruit, tot 2126; werkt op mobiel)

## Uitkomst

Kerst 2026 tot en met kerst 2046 (21 jaar):

| Ploeg | Kerst dag | Kerst nacht | O&N dag | O&N nacht | Totaal | Jaren zonder dienst | Waarvan helemaal vrij |
|---|---|---|---|---|---|---|---|
| 1 | 12 | 11 | 9 | 8 | 40 | 4 | 1 |
| 2 | 12 | 12 | 9 | 9 | 42 | 4 | 1 |
| 3 | 14 | 12 | 7 | 9 | 42 | 2 | 0 |
| 4 | 11 | 16 | 9 | 7 | 43 | 4 | 1 |
| 5 | 14 | 12 | 8 | 9 | 43 | 2 | 0 |

Kerst 2026 tot en met kerst 2126 (101 jaar):

| Ploeg | Kerst dag | Kerst nacht | O&N dag | O&N nacht | Totaal | Jaren zonder dienst | Waarvan helemaal vrij |
|---|---|---|---|---|---|---|---|
| 1 | 64 | 59 | 40 | 43 | 206 | 13 | 2 |
| 2 | 59 | 63 | 40 | 40 | 202 | 14 | 4 |
| 3 | 60 | 63 | 40 | 38 | 201 | 16 | 3 |
| 4 | 59 | 59 | 43 | 39 | 200 | 16 | 4 |
| 5 | 61 | 59 | 39 | 42 | 201 | 14 | 2 |

De verdeling is nagenoeg eerlijk: elke ploeg zit binnen een paar diensten van het gemiddelde. Over 20 jaar heeft ploeg 4 wel de meeste kerstnachten.

- *Jaren zonder dienst*: op geen van de vijf feestdagen een dag- of nachtdienst (reserve kan wel).
- *Helemaal vrij*: ook geen reserve.

## Hoe het werkt

Het rooster is een cyclus van 35 dagen (5 weken). Elke ploeg heeft per cyclus een reserveweek (de letters R-E-S-E-R-V-E in het rooster). De plek in de cyclus voor een datum is `((datum - 1 jan 2027) + 4) mod 35`. Dit klopt met het rooster van 2027: met kerst heeft ploeg 4 nachten en ploeg 5 dagen, en met de jaarwisseling heeft ploeg 2 dagen en ploeg 3 nachten. Het script controleert dat elke keer.

Aanname: de cyclus loopt elk jaar ongewijzigd door, zonder ruilen of verlof.

## Zelf draaien

```
pip install openpyxl xlrd
python scripts/analyse.py "rooster/bisonrooster 2027.xls" --van 2026 --tot 2126
```

`--van` en `--tot` kies je zelf. Zonder rooster-bestand gebruikt het script het patroon van 2027 dat erin staat (dan is `xlrd` niet nodig).

## Bestanden

- `rooster/bisonrooster 2027.xls`: het originele jaarrooster.
- `scripts/analyse.py`: rekent de diensten uit en maakt de CSV en de Excel.
- `data/bison_diensten_2026-2126.csv`: per jaar, datum en ploeg de dienst. Dit is de bron van het dashboard.
- `output/bison_kerst_oudnieuw_2026-2126.xlsx`: overzicht per datum, per ploeg en de totalen.
- `index.html`: het dashboard voor GitHub Pages. Wordt gemaakt met `python scripts/bouw_pagina.py` uit `dashboard/index.html`; pas die aan en bouw opnieuw.
- `dashboard/index.html`: de inhoud van het dashboard (ook gebruikt in het Claude-dashboard).
