"""
Główny moduł wyszukiwarki ofert pracy w Norwegii.

Skrypt agreguje ogłoszenia dla monterów rusztowań (§17-4 / NS 9700)
oraz malarzy/piaskarzy konstrukcji stalowych (NORSOK M-501:2022)
z norweskich i międzynarodowych serwisów z ofertami pracy,
a następnie generuje ustrukturyzowany raport w języku polskim.

Użycie:
    python job_search.py [--category scaffolder|painter|all]
                         [--output raport.txt]
                         [--format text|json|csv]

Wymagane pakiety:
    pip install -r requirements.txt
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import List, Optional
from urllib.parse import urlencode, urljoin

import requests
from bs4 import BeautifulSoup
from tabulate import tabulate

from config import (
    ALL_KEYWORDS,
    JOB_BOARD_URLS,
    JOB_CATEGORIES,
    KEYWORDS_PAINTER,
    KEYWORDS_SCAFFOLDER,
    LOCATIONS,
    OUTPUT_DATE_FORMAT,
    REPORT_TITLE,
    REQUIRED_BENEFITS,
    ROTATION_PATTERNS,
)

# ─── Stałe ──────────────────────────────────────────────────────────────────

REQUEST_TIMEOUT = 15  # sekund
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; JobSearchBot/1.0; "
        "+https://github.com/Szybkimarcin95/Co-ci-pokaze2)"
    )
}
NAV_API_BASE = "https://arbeidsplassen.nav.no/public-feed/api/v1/ads"
NAV_PAGE_SIZE = 50


# ─── Modele danych ──────────────────────────────────────────────────────────


@dataclass
class JobListing:
    """Reprezentuje pojedynczą ofertę pracy."""

    title: str
    company: str
    location: str
    country: str = "Norwegia"
    salary_range: str = "Nie podano"
    rotation_schedule: str = "Nie podano"
    contract_type: str = "Nie podano"
    source_url: str = ""
    source_board: str = ""
    published_date: str = ""
    benefits: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    description_snippet: str = ""
    meets_rotation_criteria: bool = False
    meets_benefits_criteria: bool = False

    def meets_all_criteria(self) -> bool:
        return self.meets_rotation_criteria and self.meets_benefits_criteria


# ─── Funkcje pomocnicze ──────────────────────────────────────────────────────


def _normalize(text: str) -> str:
    """Zwraca tekst w małych literach bez zbędnych białych znaków."""
    return " ".join(text.lower().split())


def detect_rotation(text: str) -> str:
    """Wykrywa schemat rotacji w tekście ogłoszenia."""
    normalized = _normalize(text)
    for pattern in ROTATION_PATTERNS:
        if pattern.lower() in normalized:
            return pattern
    # Szukaj wzorca X/Y lub X weeks on / Y weeks off
    match = re.search(r"\b(\d{1,2})\s*/\s*(\d{1,2})\b", normalized)
    if match:
        return f"{match.group(1)}/{match.group(2)}"
    return "Nie podano"


def meets_rotation_criteria(rotation: str) -> bool:
    """Sprawdza czy schemat rotacji spełnia wymagania (14/21 lub 14/14)."""
    return rotation in ("14/21", "14/14")


def detect_benefits(text: str) -> List[str]:
    """Wykrywa wymienione świadczenia (zakwaterowanie, wyżywienie) w tekście."""
    normalized = _normalize(text)
    found = []
    for benefit in REQUIRED_BENEFITS:
        if benefit.lower() in normalized:
            found.append(benefit)
    return found


def meets_benefits_criteria(benefits: List[str]) -> bool:
    """Sprawdza czy oferta zawiera zakwaterowanie i wyżywienie od pracodawcy."""
    normalized_benefits = [b.lower() for b in benefits]
    has_accommodation = any(
        kw in " ".join(normalized_benefits)
        for kw in (
            "accommodation",
            "housing",
            "lodging",
            "zakwaterowanie",
            "nocleg",
        )
    )
    has_meals = any(
        kw in " ".join(normalized_benefits)
        for kw in ("meals", "board", "wyżywienie", "catering")
    )
    return has_accommodation and has_meals


def detect_certifications(text: str, category: str) -> List[str]:
    """Wykrywa wymagane certyfikaty w tekście ogłoszenia."""
    normalized = _normalize(text)
    certs = JOB_CATEGORIES.get(category, {}).get("certifications", [])
    return [c for c in certs if c.lower() in normalized]


# ─── Parsery serwisów z ogłoszeniami ────────────────────────────────────────


def _safe_get(url: str, params: Optional[dict] = None) -> Optional[requests.Response]:
    """Wykonuje bezpieczne żądanie GET z obsługą błędów."""
    try:
        resp = requests.get(
            url,
            params=params,
            headers=REQUEST_HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        return resp
    except requests.RequestException as exc:
        print(f"  [OSTRZEŻENIE] Nie udało się pobrać {url}: {exc}", file=sys.stderr)
        return None


def fetch_nav_listings(keywords: List[str]) -> List[JobListing]:
    """
    Pobiera oferty z norweskiego urzędu pracy NAV (arbeidsplassen.nav.no)
    używając publicznego API REST.

    API dokumentacja: https://arbeidsplassen.nav.no/public-feed/swagger-ui/
    """
    listings: List[JobListing] = []
    search_query = " OR ".join(f'"{kw}"' for kw in keywords[:5])  # max 5 słów kluczowych
    params = {
        "q": search_query,
        "country": "NORGE",
        "size": NAV_PAGE_SIZE,
        "page": 0,
    }
    resp = _safe_get(NAV_API_BASE, params=params)
    if resp is None:
        return listings

    try:
        data = resp.json()
    except ValueError:
        return listings

    for ad in data.get("content", []):
        full_text = " ".join(
            [
                ad.get("title", ""),
                ad.get("description", ""),
                ad.get("employerName", ""),
            ]
        )
        rotation = detect_rotation(full_text)
        benefits = detect_benefits(full_text)
        listing = JobListing(
            title=ad.get("title", "Brak tytułu"),
            company=ad.get("employerName", "Brak nazwy firmy"),
            location=ad.get("locationList", [{}])[0].get("city", "Brak lokalizacji")
            if ad.get("locationList")
            else "Brak lokalizacji",
            country="Norwegia",
            contract_type=ad.get("engagementtype", "Nie podano"),
            rotation_schedule=rotation,
            source_url=ad.get("sourceurl", ""),
            source_board="NAV (arbeidsplassen.nav.no)",
            published_date=ad.get("published", "")[:10]
            if ad.get("published")
            else "",
            benefits=benefits,
            description_snippet=ad.get("description", "")[:300],
            meets_rotation_criteria=meets_rotation_criteria(rotation),
            meets_benefits_criteria=meets_benefits_criteria(benefits),
        )
        listings.append(listing)
    return listings


def fetch_finn_listings(keywords: List[str]) -> List[JobListing]:
    """
    Pobiera oferty z FINN.no przez scrapowanie HTML wyników wyszukiwania.
    FINN.no jest największym norweskim serwisem ogłoszeniowym.
    """
    listings: List[JobListing] = []
    base_url = "https://www.finn.no/job/fulltime/search.html"

    for keyword in keywords[:3]:  # ograniczamy liczbę zapytań
        params = {"q": keyword, "geo_id": "0.20003"}  # Norwegia
        resp = _safe_get(base_url, params=params)
        if resp is None:
            continue

        soup = BeautifulSoup(resp.text, "lxml")
        articles = soup.select("article[data-testid='ads-list-result-item']")

        for article in articles[:10]:
            title_el = article.select_one("h2")
            company_el = article.select_one("[data-testid='employer-name']")
            location_el = article.select_one("[data-testid='location']")
            link_el = article.select_one("a[href]")

            title = title_el.get_text(strip=True) if title_el else "Brak tytułu"
            company = company_el.get_text(strip=True) if company_el else "Brak nazwy"
            location = location_el.get_text(strip=True) if location_el else "Norwegia"
            url = urljoin("https://www.finn.no", link_el["href"]) if link_el else ""

            full_text = article.get_text(" ", strip=True)
            rotation = detect_rotation(full_text)
            benefits = detect_benefits(full_text)

            listings.append(
                JobListing(
                    title=title,
                    company=company,
                    location=location,
                    country="Norwegia",
                    rotation_schedule=rotation,
                    source_url=url,
                    source_board="FINN.no",
                    benefits=benefits,
                    meets_rotation_criteria=meets_rotation_criteria(rotation),
                    meets_benefits_criteria=meets_benefits_criteria(benefits),
                )
            )
        time.sleep(1)  # uprzejme opóźnienie między zapytaniami
    return listings


# ─── Agregator ──────────────────────────────────────────────────────────────


def search_jobs(category: str = "all") -> List[JobListing]:
    """
    Przeprowadza wyszukiwanie ofert pracy we wszystkich skonfigurowanych źródłach.

    Args:
        category: 'scaffolder', 'painter' lub 'all'

    Returns:
        Lista obiektów JobListing posortowana wg spełnienia kryteriów.
    """
    if category == "scaffolder":
        keywords = KEYWORDS_SCAFFOLDER
    elif category == "painter":
        keywords = KEYWORDS_PAINTER
    else:
        keywords = ALL_KEYWORDS

    print(f"🔍 Wyszukiwanie ofert: kategoria='{category}', słów kluczowych={len(keywords)}")
    all_listings: List[JobListing] = []

    print("  → Pobieranie z NAV (arbeidsplassen.nav.no)…")
    all_listings.extend(fetch_nav_listings(keywords))

    print("  → Pobieranie z FINN.no…")
    all_listings.extend(fetch_finn_listings(keywords))

    # Deduplikacja po tytule + firma
    seen: set = set()
    unique: List[JobListing] = []
    for listing in all_listings:
        key = (listing.title.lower(), listing.company.lower())
        if key not in seen:
            seen.add(key)
            unique.append(listing)

    # Sortowanie: najpierw spełniające oba kryteria, potem rotacja, potem reszta
    unique.sort(
        key=lambda x: (
            not x.meets_all_criteria(),
            not x.meets_rotation_criteria,
            not x.meets_benefits_criteria,
        )
    )
    return unique


# ─── Formatowanie raportu ────────────────────────────────────────────────────


def _section(title: str, width: int = 80) -> str:
    line = "─" * width
    return f"\n{line}\n  {title}\n{line}"


def format_report_text(listings: List[JobListing], category: str = "all") -> str:
    """Generuje raport tekstowy w języku polskim."""
    now = datetime.now().strftime(OUTPUT_DATE_FORMAT)
    lines: List[str] = []

    lines.append("=" * 80)
    lines.append(f"  {REPORT_TITLE}")
    lines.append(f"  Wygenerowano: {now}  |  Kategoria: {category.upper()}")
    lines.append("=" * 80)

    # ── 1. Przegląd ofert ───────────────────────────────────────────────────
    lines.append(_section("1. PRZEGLĄD OFERT PRACY"))

    total = len(listings)
    meeting_all = sum(1 for j in listings if j.meets_all_criteria())
    meeting_rotation = sum(1 for j in listings if j.meets_rotation_criteria)

    location_counts: dict = {}
    contract_counts: dict = {}
    for j in listings:
        location_counts[j.location] = location_counts.get(j.location, 0) + 1
        contract_counts[j.contract_type] = contract_counts.get(j.contract_type, 0) + 1

    lines.append(f"\n  Łączna liczba znalezionych ofert:          {total}")
    lines.append(f"  Oferty spełniające WSZYSTKIE kryteria:     {meeting_all}")
    lines.append(f"  Oferty z odpowiednim systemem rotacji:     {meeting_rotation}")

    lines.append("\n  Lokalizacje:")
    for loc, cnt in sorted(location_counts.items(), key=lambda x: -x[1])[:10]:
        lines.append(f"    • {loc}: {cnt}")

    lines.append("\n  Typy umów:")
    for ctype, cnt in sorted(contract_counts.items(), key=lambda x: -x[1]):
        lines.append(f"    • {ctype}: {cnt}")

    # ── 2. Szczegóły ofert ─────────────────────────────────────────────────
    lines.append(_section("2. SZCZEGÓŁY OFERT PRACY"))
    if not listings:
        lines.append("\n  Brak ofert spełniających kryteria wyszukiwania.")
    else:
        table_data = []
        for i, j in enumerate(listings, start=1):
            criteria_ok = "✔" if j.meets_all_criteria() else ("~" if j.meets_rotation_criteria else "✘")
            table_data.append(
                [
                    i,
                    criteria_ok,
                    j.company[:30],
                    j.title[:40],
                    j.location[:20],
                    j.salary_range[:20],
                    j.rotation_schedule,
                    j.contract_type[:15],
                ]
            )
        headers = ["#", "OK", "Firma", "Stanowisko", "Lokalizacja", "Wynagrodzenie", "Rotacja", "Umowa"]
        lines.append("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))

    # Szczegółowe opisy (tylko oferty spełniające kryteria)
    best = [j for j in listings if j.meets_all_criteria()]
    if best:
        lines.append("\n  ── Oferty spełniające wszystkie kryteria ──")
        for j in best:
            lines.append(f"\n  Firma:           {j.company}")
            lines.append(f"  Stanowisko:      {j.title}")
            lines.append(f"  Lokalizacja:     {j.location}, {j.country}")
            lines.append(f"  Wynagrodzenie:   {j.salary_range}")
            lines.append(f"  Rotacja:         {j.rotation_schedule}")
            lines.append(f"  Typ umowy:       {j.contract_type}")
            lines.append(f"  Świadczenia:     {', '.join(j.benefits) or 'Nie podano'}")
            lines.append(f"  Certyfikaty:     {', '.join(j.certifications) or 'Nie podano'}")
            lines.append(f"  Opublikowano:    {j.published_date or 'Nie podano'}")
            lines.append(f"  Źródło:          {j.source_board}")
            lines.append(f"  Link:            {j.source_url or 'Brak'}")
            if j.description_snippet:
                lines.append(f"  Opis (fragment): {j.description_snippet[:200]}…")
            lines.append("  " + "─" * 60)

    # ── 3. Kryteria selekcji ───────────────────────────────────────────────
    lines.append(_section("3. KRYTERIA SELEKCJI OFERT"))
    lines.append(
        "\n  Oferty są filtrowane według następujących kryteriów obowiązkowych:"
    )
    lines.append(
        "\n  a) System rotacji:"
    )
    for pattern in ROTATION_PATTERNS:
        lines.append(f"     • {pattern}")
    lines.append(
        "\n  b) Świadczenia zapewniane przez pracodawcę:"
    )
    lines.append("     • Zakwaterowanie (accommodation / housing / nocleg)")
    lines.append("     • Wyżywienie (meals / board / wyżywienie)")
    lines.append(
        "\n  Legenda w tabeli ofert:"
    )
    lines.append("     ✔  – spełnia WSZYSTKIE kryteria (rotacja + świadczenia)")
    lines.append("     ~  – spełnia tylko kryterium rotacji")
    lines.append("     ✘  – nie spełnia kryteriów")

    # ── 4. Słowa kluczowe wyszukiwania ─────────────────────────────────────
    lines.append(_section("4. ZASTOSOWANE SŁOWA KLUCZOWE I TERMINY WYSZUKIWANIA"))

    lines.append("\n  Monter rusztowań (Scaffolder / Stillasbygger):")
    for kw in KEYWORDS_SCAFFOLDER:
        lines.append(f"    • {kw}")

    lines.append(
        "\n  Malarz / Piaskarz konstrukcji stalowych (Industrial Painter / Sandblaster):"
    )
    for kw in KEYWORDS_PAINTER:
        lines.append(f"    • {kw}")

    lines.append("\n  Przeszukiwane serwisy z ofertami pracy:")
    for name, url in JOB_BOARD_URLS.items():
        lines.append(f"    • {name}: {url}")

    lines.append("\n" + "=" * 80)
    lines.append("  Koniec raportu")
    lines.append("=" * 80 + "\n")

    return "\n".join(lines)


def format_report_json(listings: List[JobListing]) -> str:
    """Eksportuje wyniki do formatu JSON."""
    data = {
        "generated_at": datetime.now().isoformat(),
        "total_listings": len(listings),
        "listings_meeting_all_criteria": sum(
            1 for j in listings if j.meets_all_criteria()
        ),
        "job_listings": [asdict(j) for j in listings],
        "search_keywords": {
            "scaffolder": KEYWORDS_SCAFFOLDER,
            "painter": KEYWORDS_PAINTER,
        },
        "selection_criteria": {
            "rotation_patterns": ROTATION_PATTERNS,
            "required_benefits": REQUIRED_BENEFITS,
        },
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def format_report_csv(listings: List[JobListing]) -> str:
    """Eksportuje wyniki do formatu CSV."""
    import io

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(
        [
            "Firma",
            "Stanowisko",
            "Lokalizacja",
            "Kraj",
            "Wynagrodzenie",
            "Rotacja",
            "Typ umowy",
            "Spełnia rotację",
            "Spełnia świadczenia",
            "Spełnia wszystkie kryteria",
            "Źródło",
            "Link",
            "Data publikacji",
        ]
    )
    for j in listings:
        writer.writerow(
            [
                j.company,
                j.title,
                j.location,
                j.country,
                j.salary_range,
                j.rotation_schedule,
                j.contract_type,
                "Tak" if j.meets_rotation_criteria else "Nie",
                "Tak" if j.meets_benefits_criteria else "Nie",
                "Tak" if j.meets_all_criteria() else "Nie",
                j.source_board,
                j.source_url,
                j.published_date,
            ]
        )
    return buf.getvalue()


# ─── Interfejs wiersza poleceń ──────────────────────────────────────────────


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Wyszukiwarka ofert pracy w Norwegii – monterzy rusztowań "
            "i malarze przemysłowi."
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--category",
        choices=["scaffolder", "painter", "all"],
        default="all",
        help=(
            "Kategoria ofert do wyszukania:\n"
            "  scaffolder – monterzy rusztowań (§17-4, NS 9700)\n"
            "  painter    – malarze/piaskarze (NORSOK M-501:2022)\n"
            "  all        – obie kategorie (domyślnie)"
        ),
    )
    parser.add_argument(
        "--output",
        default=None,
        metavar="PLIK",
        help="Opcjonalna ścieżka do pliku wyjściowego (domyślnie: stdout).",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json", "csv"],
        default="text",
        help="Format wyjściowy raportu (domyślnie: text).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    listings = search_jobs(category=args.category)

    print(f"\n✅ Znaleziono {len(listings)} ofert(y).")
    meets = sum(1 for j in listings if j.meets_all_criteria())
    print(f"   z czego {meets} spełnia wszystkie kryteria (rotacja + świadczenia).\n")

    if args.format == "json":
        report = format_report_json(listings)
    elif args.format == "csv":
        report = format_report_csv(listings)
    else:
        report = format_report_text(listings, category=args.category)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(report)
        print(f"📄 Raport zapisano do pliku: {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()
