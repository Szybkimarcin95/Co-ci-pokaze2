"""
Konfiguracja wyszukiwarki ofert pracy w Norwegii.
Zawiera słowa kluczowe, kryteria selekcji i ustawienia wyszukiwania.
"""

# ─── Słowa kluczowe wyszukiwania ────────────────────────────────────────────

KEYWORDS_SCAFFOLDER = [
    "scaffolder",
    "scaffolding",
    "stillasbygger",
    "monter rusztowań",
    "rusztowania",
    "§17",
    "§17-4",
    "paragraf 17",
    "ISO 45001",
    "NS 9700",
    "CISRS",
    "COTS",
    "offshore scaffolding",
    "industrial scaffolding",
    "scaffolder offshore Norway",
]

KEYWORDS_PAINTER = [
    "industrial painter",
    "sandblaster",
    "malarz przemysłowy",
    "malarz piaskarz",
    "malarz konstrukcji stalowych",
    "NORSOK M-501",
    "NORSOK M501",
    "NORSOK M-501:2022",
    "blåsing",
    "overflatebehandling",
    "coating inspector",
    "FROSIO",
    "NACE",
    "ISO 8501",
    "industrial painter Norway",
    "surface treatment",
]

ALL_KEYWORDS = KEYWORDS_SCAFFOLDER + KEYWORDS_PAINTER

# ─── Lokalizacje wyszukiwania ────────────────────────────────────────────────

LOCATIONS = [
    "Norway",
    "Norwegia",
    "Stavanger",
    "Bergen",
    "Oslo",
    "Haugesund",
    "Kristiansund",
    "Ålesund",
    "Offshore Norway",
    "North Sea",
    "Morze Północne",
]

# ─── Kryteria selekcji ofert ─────────────────────────────────────────────────

ROTATION_PATTERNS = [
    "14/21",
    "14/14",
    "2 weeks on / 3 weeks off",
    "2 weeks on / 2 weeks off",
    "rotation 14",
]

REQUIRED_BENEFITS = [
    "accommodation",
    "meals",
    "free accommodation",
    "free meals",
    "housing provided",
    "board and lodging",
    "zakwaterowanie",
    "wyżywienie",
    "nocleg",
]

# ─── Adresy źródłowych serwisów z ofertami pracy ────────────────────────────

JOB_BOARD_URLS = {
    "NAV (Norwegia)": "https://arbeidsplassen.nav.no/stillinger",
    "FINN.no": "https://www.finn.no/job/fulltime/search.html",
    "StepStone NO": "https://www.stepstone.no",
    "LinkedIn": "https://www.linkedin.com/jobs/search/",
    "Rigzone": "https://www.rigzone.com/oil/jobs/",
    "OilCareers": "https://www.oilcareers.com/",
    "Eurojobs": "https://www.eurojobs.com/",
    "Indeed NO": "https://no.indeed.com/",
    "Jobbnorge": "https://www.jobbnorge.no/",
    "Offshorejobs": "https://www.offshorejobs.com/",
}

# ─── Branże / typy stanowisk ─────────────────────────────────────────────────

JOB_CATEGORIES = {
    "scaffolder": {
        "pl": "Monter rusztowań",
        "no": "Stillasbygger",
        "en": "Scaffolder",
        "certifications": ["§17-4", "NS 9700", "ISO 45001", "CISRS", "COTS"],
        "description": (
            "Monter rusztowań przemysłowych pracujący zgodnie z normą NS 9700 "
            "oraz przepisami paragraf 17 norweskiego prawa pracy (§17-4)."
        ),
    },
    "industrial_painter": {
        "pl": "Malarz / piaskarz konstrukcji stalowych",
        "no": "Overflatebehandler / blåser",
        "en": "Industrial Painter / Sandblaster",
        "certifications": [
            "NORSOK M-501:2022",
            "FROSIO",
            "NACE",
            "ISO 8501",
            "ISO 12944",
        ],
        "description": (
            "Malarz piaskarz konstrukcji stalowych specjalizujący się "
            "w obróbce powierzchniowej wg normy NORSOK M-501:2022 "
            "dla sektora naftowego i gazowego w Norwegii."
        ),
    },
}

# ─── Ustawienia raportowania ─────────────────────────────────────────────────

REPORT_TITLE = (
    "Raport: Oferty pracy w Norwegii – monterzy rusztowań i malarze przemysłowi"
)
REPORT_LANGUAGE = "pl"  # język raportów: 'pl' = polski
OUTPUT_DATE_FORMAT = "%d.%m.%Y"
