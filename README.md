# Co-ci-pokaze2

## Wyszukiwarka ofert pracy w Norwegii – monterzy rusztowań i malarze przemysłowi

Narzędzie agregujące ogłoszenia o pracę dla:

- **Monterów rusztowań** (stillasbygger, §17-4, NS 9700, ISO 45001, CISRS)
- **Malarzy / piaskarzy konstrukcji stalowych** (NORSOK M-501:2022, FROSIO, NACE, ISO 8501)

Skrypt przeszukuje norweskie i międzynarodowe serwisy (NAV, FINN.no i inne),
filtruje oferty według wymaganych kryteriów i generuje ustrukturyzowany raport.

---

## Wymagania

- Python 3.9+
- Dostęp do internetu (wyszukiwanie w czasie rzeczywistym)

```bash
pip install -r requirements.txt
```

---

## Użycie

```bash
# Wyszukaj wszystkie oferty (monterzy rusztowań + malarze)
python job_search.py

# Tylko monterzy rusztowań
python job_search.py --category scaffolder

# Tylko malarze / piaskarze
python job_search.py --category painter

# Zapisz raport do pliku tekstowego
python job_search.py --output raport.txt

# Eksport do JSON
python job_search.py --format json --output raport.json

# Eksport do CSV
python job_search.py --format csv --output raport.csv
```

---

## Struktura raportu

Raport zawiera **4 sekcje**:

1. **Przegląd ofert pracy** – liczba dostępnych ogłoszeń, lokalizacje, typy umów
2. **Szczegóły każdej oferty** – firma, stanowisko, lokalizacja, wynagrodzenie, system rotacji
3. **Kryteria selekcji** – wymagany system rotacji (14/21 lub 14/14), zakwaterowanie i wyżywienie od pracodawcy
4. **Słowa kluczowe** – pełna lista terminów wyszukiwania (ISO, §17-4, NS 9700, NORSOK M-501:2022, FROSIO, NACE, CISRS itp.)

---

## Kryteria selekcji ofert

Oferty są oznaczane symbolem **✔** gdy spełniają oba kryteria obowiązkowe:

| Kryterium | Wymagana wartość |
|---|---|
| System rotacji | **14/21** lub **14/14** |
| Zakwaterowanie | zapewnione przez pracodawcę |
| Wyżywienie | zapewnione przez pracodawcę |

---

## Zastosowane słowa kluczowe

### Monter rusztowań (Scaffolder / Stillasbygger)

`scaffolder`, `stillasbygger`, `§17`, `§17-4`, `paragraf 17`, `NS 9700`,
`ISO 45001`, `CISRS`, `COTS`, `offshore scaffolding`, `rusztowania`

### Malarz / Piaskarz (Industrial Painter / Sandblaster)

`industrial painter`, `sandblaster`, `NORSOK M-501`, `NORSOK M-501:2022`,
`FROSIO`, `NACE`, `ISO 8501`, `ISO 12944`, `overflatebehandling`, `blåsing`

---

## Przeszukiwane serwisy

| Serwis | URL |
|---|---|
| NAV (Norwegia) | https://arbeidsplassen.nav.no/stillinger |
| FINN.no | https://www.finn.no/job/fulltime/search.html |
| LinkedIn | https://www.linkedin.com/jobs/search/ |
| Rigzone | https://www.rigzone.com/oil/jobs/ |
| Indeed NO | https://no.indeed.com/ |
| Jobbnorge | https://www.jobbnorge.no/ |
| Offshorejobs | https://www.offshorejobs.com/ |

---

## Testy

```bash
python -m pytest tests/ -v
```

---

## Pliki projektu

| Plik | Opis |
|---|---|
| `job_search.py` | Główny skrypt wyszukiwarki i generatora raportów |
| `config.py` | Konfiguracja: słowa kluczowe, kryteria, adresy serwisów |
| `requirements.txt` | Zależności Pythona |
| `tests/test_job_search.py` | Testy jednostkowe |
