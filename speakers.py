XTTS_V2_SPEAKERS = [
    "Claribel Dervla",
    "Daisy Studious",
    "Gracie Wise",
    "Tammie Ema",
    "Alison Dietlinde",
    "Ana Florence",
    "Annmarie Nele",
    "Asya Anara",
    "Brenda Stern",
    "Gitta Nikolina",
    "Henriette Usha",
    "Sofia Hellen",
    "Tammy Grit",
    "Tanja Adelina",
    "Vjollca Johnnie",
    "Andrew Chipper",
    "Badr Odhiambo",
    "Dionisio Schuyler",
    "Royston Min",
    "Viktor Eka",
    "Abrahan Mack",
    "Adde Michal",
    "Baldur Sanjin",
    "Craig Gutsy",
    "Damien Black",
    "Gilberto Mathias",
    "Ilkin Urbano",
    "Kazuhiko Atallah",
    "Ludvig Milivoj",
    "Suad Qasim",
    "Torcull Diarmuid",
    "Viktor Menelaos",
    "Zacharie Aimilios",
    "Nova Hogarth",
    "Maja Ruoho",
    "Uta Obando",
    "Lidiya Szekeres",
    "Chandra MacFarland",
    "Szofi Granger",
    "Camilla Holmström",
    "Lilya Stainthorpe",
    "Zofija Kendrick",
    "Narelle Moon",
    "Barbora MacLean",
    "Alexandra Hisakawa",
    "Alma María",
    "Rosemary Okafor",
    "Ige Behringer",
    "Filip Traverse",
    "Damjan Chapman",
    "Wulf Carlevaro",
    "Aaron Dreschner",
    "Kumar Dahl",
    "Eugenio Mataracı",
    "Ferran Simen",
    "Xavier Hayasaka",
    "Luis Moray",
    "Marcos Rudaski",
]

SPEAKER_ACCENT_MAP = {
    "es-MX": [
        "Luis Moray",
        "Marcos Rudaski",
        "Xavier Hayasaka",
        "Ferran Simen",
        "Eugenio Mataracı",
    ],
    "es-CO": [
        "Alma María",
        "Ana Florence",
        "Sofia Hellen",
        "Gitta Nikolina",
        "Henriette Usha",
    ],
    "es-VE": [
        "Claribel Dervla",
        "Daisy Studious",
        "Gracie Wise",
        "Tammie Ema",
        "Alison Dietlinde",
    ],
    "es-AR": [
        "Annmarie Nele",
        "Asya Anara",
        "Brenda Stern",
        "Tammy Grit",
        "Tanja Adelina",
    ],
    "es-ES": [
        "Vjollca Johnnie",
        "Andrew Chipper",
        "Badr Odhiambo",
        "Dionisio Schuyler",
        "Royston Min",
    ],
    "en-US": [
        "Viktor Eka",
        "Abrahan Mack",
        "Adde Michal",
        "Baldur Sanjin",
        "Craig Gutsy",
        "Damien Black",
        "Gilberto Mathias",
        "Ilkin Urbano",
        "Kazuhiko Atallah",
        "Ludvig Milivoj",
        "Suad Qasim",
        "Torcull Diarmuid",
        "Viktor Menelaos",
        "Zacharie Aimilios",
    ],
    "en-GB": [
        "Nova Hogarth",
        "Maja Ruoho",
        "Uta Obando",
        "Lidiya Szekeres",
        "Chandra MacFarland",
        "Szofi Granger",
        "Camilla Holmström",
        "Lilya Stainthorpe",
        "Zofija Kendrick",
        "Narelle Moon",
        "Barbora MacLean",
        "Alexandra Hisakawa",
        "Rosemary Okafor",
        "Ige Behringer",
        "Filip Traverse",
        "Damjan Chapman",
        "Wulf Carlevaro",
        "Aaron Dreschner",
        "Kumar Dahl",
    ],
}

ACCENT_DISPLAY_NAMES = {
    "es-MX": "Español - México 🇲🇽",
    "es-CO": "Español - Colombia 🇨🇴",
    "es-VE": "Español - Venezuela 🇻🇪",
    "es-AR": "Español - Argentina 🇦🇷",
    "es-ES": "Español - España 🇪🇸",
    "en-US": "English - US 🇺🇸",
    "en-GB": "English - UK 🇬🇧",
}

LANGUAGE_ACCENTS = {
    "es": ["es-MX", "es-CO", "es-VE", "es-AR", "es-ES"],
    "en": ["en-US", "en-GB"],
}

DEFAULT_SPEAKER = "Luis Moray"
DEFAULT_ACCENT = "es-MX"
DEFAULT_LANGUAGE = "es"


def get_speakers_for_accent(accent: str) -> list:
    return SPEAKER_ACCENT_MAP.get(accent, [])


def get_accent_for_speaker(speaker: str) -> str:
    for accent, speakers in SPEAKER_ACCENT_MAP.items():
        if speaker in speakers:
            return accent
    return "es-MX"


def get_accents_for_language(language: str) -> list:
    return LANGUAGE_ACCENTS.get(language, [])


def get_all_speakers() -> list:
    return XTTS_V2_SPEAKERS.copy()


def get_accent_display_name(accent: str) -> str:
    return ACCENT_DISPLAY_NAMES.get(accent, accent)