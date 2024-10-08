# language_utils.py

import logging
from logging.handlers import RotatingFileHandler
from typing import Any

# Set up a specific logger for missing languages
missing_lang_logger: logging.Logger = logging.getLogger("missing_languages")
missing_lang_logger.setLevel(logging.WARNING)

# Create a rotating file handler
log_file = "missing_languages.log"
handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=5)
formatter = logging.Formatter("%(asctime)s - %(message)s")
handler.setFormatter(formatter)
missing_lang_logger.addHandler(handler)

LANGUAGE_MAP: dict[str, str] = {
    "en": "Английский",
    "eng": "Английский",
    "ru": "Русский",
    "rus": "Русский",
    "fr": "Французский",
    "fre": "Французский",
    "fra": "Французский",
    "de": "Немецкий",
    "ger": "Немецкий",
    "deu": "Немецкий",
    "es": "Испанский",
    "spa": "Испанский",
    "it": "Итальянский",
    "ita": "Итальянский",
    "pt": "Португальский",
    "por": "Португальский",
    "nl": "Нидерландский",
    "dut": "Нидерландский",
    "nld": "Нидерландский",
    "ja": "Японский",
    "jpn": "Японский",
    "zh": "Китайский",
    "chi": "Китайский",
    "zho": "Китайский",
    "ar": "Арабский",
    "ara": "Арабский",
    "ko": "Корейский",
    "kor": "Корейский",
    "hi": "Хинди",
    "hin": "Хинди",
    "be": "Беларуский",
    "bel": "Беларуский",
    "uk": "Украинский",
    "ukr": "Украинский",
    "pl": "Польский",
    "pol": "Польский",
    "cs": "Чешский",
    "cze": "Чешский",
    "ces": "Чешский",
    "sv": "Шведский",
    "swe": "Шведский",
    "no": "Норвежский",
    "nor": "Норвежский",
    "fi": "Финский",
    "fin": "Финский",
    "da": "Датский",
    "dan": "Датский",
    "tr": "Турецкий",
    "tur": "Турецкий",
    "el": "Греческий",
    "gre": "Греческий",
    "ell": "Греческий",
    "he": "Иврит",
    "heb": "Иврит",
    "la": "Латинский",
    "lat": "Латинский",
    "hu": "Венгерский",
    "hun": "Венгерский",
    "ro": "Румынский",
    "ron": "Румынский",
    "sk": "Словацкий",
    "slk": "Словацкий",
    "sl": "Словенский",
    "slv": "Словенский",
    "bg": "Болгарский",
    "bul": "Болгарский",
    "sr": "Сербский",
    "srp": "Сербский",
    "hr": "Хорватский",
    "hrv": "Хорватский",
    "ca": "Каталанский",
    "cat": "Каталанский",
    "lt": "Литовский",
    "lit": "Литовский",
    "lv": "Латышский",
    "lav": "Латышский",
    "et": "Эстонский",
    "est": "Эстонский",
    "vi": "Вьетнамский",
    "vie": "Вьетнамский",
    "th": "Тайский",
    "tha": "Тайский",
    "id": "Индонезийский",
    "ind": "Индонезийский",
    "ms": "Малайский",
    "msa": "Малайский",
    "fa": "Персидский",
    "per": "Персидский",
    "fas": "Персидский",
    "ur": "Урду",
    "urd": "Урду",
    "bn": "Бенгальский",
    "ben": "Бенгальский",
    "ta": "Тамильский",
    "tam": "Тамильский",
    "te": "Телугу",
    "tel": "Телугу",
    "mr": "Маратхи",
    "mar": "Маратхи",
    "gu": "Гуджарати",
    "guj": "Гуджарати",
    "kn": "Каннада",
    "kan": "Каннада",
    "ml": "Малаялам",
    "mal": "Малаялам",
    "baq": "Баскский",
    "rum": "Румынский",
    "und": "Неизвестно",
}

GOODREADS_LANGUAGE_MAP: dict[str, str] = {
    "English": "Английский",
    "Russian": "Русский",
    "French": "Французский",
    "German": "Немецкий",
    "Spanish": "Испанский",
    "Italian": "Итальянский",
    "Portuguese": "Португальский",
    "Dutch": "Нидерландский",
    "Japanese": "Японский",
    "Chinese": "Китайский",
    "Arabic": "Арабский",
    "Korean": "Корейский",
    "Hindi": "Хинди",
    "Belarusian": "Беларуский",
    "Ukrainian": "Украинский",
    "Polish": "Польский",
    "Czech": "Чешский",
    "Swedish": "Шведский",
    "Norwegian": "Норвежский",
    "Finnish": "Финский",
    "Danish": "Датский",
    "Turkish": "Турецкий",
    "Greek": "Греческий",
    "Hebrew": "Иврит",
    "Latin": "Латинский",
    "Hungarian": "Венгерский",
    "Romanian": "Румынский",
    "Slovak": "Словацкий",
    "Slovenian": "Словенский",
    "Bulgarian": "Болгарский",
    "Serbian": "Сербский",
    "Croatian": "Хорватский",
    "Catalan": "Каталанский",
    "Lithuanian": "Литовский",
    "Latvian": "Латышский",
    "Estonian": "Эстонский",
    "Vietnamese": "Вьетнамский",
    "Thai": "Тайский",
    "Indonesian": "Индонезийский",
    "Malay": "Малайский",
    "Persian": "Персидский",
    "Urdu": "Урду",
    "Bengali": "Бенгальский",
    "Tamil": "Тамильский",
    "Telugu": "Телугу",
    "Marathi": "Маратхи",
    "Gujarati": "Гуджарати",
    "Kannada": "Каннада",
    "Malayalam": "Малаялам",
    "Basque": "Баскский",
    "Unknown": "Неизвестно",
}


def standardize_language_code(lang: str, book_data: dict[str, Any]) -> str:
    """
    Standardize language codes, converting them to full Russian language names.

    Args:
        lang (str): The language code or name to standardize.
        book_data (dict[str, Any]): The book data containing title, author, and ISBN.

    Returns:
        str: The standardized language name in Russian.
    """
    normalized_lang: str = lang.lower()
    if normalized_lang in LANGUAGE_MAP:
        return LANGUAGE_MAP[normalized_lang]
    elif lang in GOODREADS_LANGUAGE_MAP:
        return GOODREADS_LANGUAGE_MAP[lang]
    else:
        log_missing_language(lang, book_data)
        return lang


def log_missing_language(lang: str, book_data: dict[str, Any]) -> None:
    """
    Log information about a missing language code along with book details.

    Args:
        lang (str): The unknown language code.
        book_data (Dict[str, Any]): The book data containing title, author, and ISBN.
    """
    title: str = book_data.get("title", "None")
    authors: str = ", ".join(book_data.get("authors", ["None"]))
    isbn: str = book_data.get("isbn", "None")

    message: str = (
        f"Unknown language code: {lang} | Title: {title} | Author(s): {authors} | ISBN: {isbn}"
    )
    missing_lang_logger.warning(message)
