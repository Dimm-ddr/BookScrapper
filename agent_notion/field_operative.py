# agent_notion/field_operative.py

import logging
from logging.handlers import RotatingFileHandler
import re
from typing import Any

from golden_book_retriever.utils.string_utils import normalize_tags, is_useful_tag

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


# agent_notion/field_operative.py

import logging
from logging.handlers import RotatingFileHandler
import re
from typing import Any

from golden_book_retriever.utils.string_utils import normalize_tags, is_useful_tag

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


def sanitize_field_value(value: str) -> str:
    """
    Sanitize a field value by removing commas and other problematic characters.
    """
    # Remove commas, quotation marks, and other potentially problematic characters
    sanitized: str = re.sub(r'[,"\'\(\)\[\]{}]', "", value)
    # Replace multiple spaces with a single space and trim
    return re.sub(r"\s+", " ", sanitized).strip()


def sanitize_list(items: list[str]) -> list[str]:
    """
    Sanitize a list of items, removing duplicates and empty values.
    """
    return list(set(sanitize_field_value(item) for item in items if item))


def prepare_multiselect_field(field_name: str, values: list[str]) -> dict:
    """
    Prepare a multi-select field for Notion, sanitizing values.
    """
    sanitized_values: list[str] = sanitize_list(values)
    return {
        field_name: {"multi_select": [{"name": value} for value in sanitized_values]}
    }


def prepare_select_field(field_name: str, value: str) -> dict:
    """
    Prepare a select field for Notion, sanitizing the value.
    """
    sanitized_value: str = sanitize_field_value(value)
    return {field_name: {"select": {"name": sanitized_value}}}


def enhance_title(title: str) -> str:
    """
    Enhance a title by capitalizing each word.

    Args:
        title (str): The title to enhance.

    Returns:
        str: The enhanced title.
    """
    return " ".join(word.capitalize() for word in title.split())


def extract_brief(description: str) -> str:
    """
    Extract a brief description from the full text.

    Args:
        description (str): The full description.

    Returns:
        str: A brief description, truncated to about 200 characters.
    """
    sentences: list[str | Any] = re.split(r"(?<=[.!?])\s+", description.strip())
    brief: str = " ".join(sentences[:2])
    if len(brief) > 200:
        brief = brief[:197].rsplit(" ", 1)[0] + "..."
    return brief


def standardize_language_code(lang: str, book_data: dict[str, Any]) -> str:
    """
    Standardize language codes, converting them to full Russian language names.

    Args:
        lang (str): The language code or name to standardize.
        book_data (Dict[str, Any]): The book data containing title, author, and ISBN.

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


def prepare_book_intel(book_data: dict[str, Any]) -> dict[str, Any]:
    """
    Prepare book data for Notion upload.

    Args:
        book_data (dict[str, Any]): Raw book data.

    Returns:
        dict[str, Any]: Prepared book data for Notion.
    """
    description: str = book_data.get("description", "")
    brief: str = extract_brief(description)
    isbn: str = book_data.get("isbn", "")
    isbn = "" if isbn is None else isbn

    # Type assertion for Pylance
    authors: list[str] = book_data.get("authors", [])
    languages: list[str] = book_data.get("languages", [])
    tags: list[str] = book_data.get("tags", [])
    publishers: list[str] = book_data.get("publishers", [])

    # Standardize language codes
    standardized_languages: list[str] = [
        standardize_language_code(lang, book_data) for lang in languages
    ]

    # Tags are already normalized, so we just need to sanitize them for Notion
    sanitized_tags: list[str] = [sanitize_field_value(tag) for tag in tags]

    prepared_data = {
        "Название": {
            "title": [{"text": {"content": enhance_title(book_data.get("title", ""))}}]
        },
        "ISBN": {"rich_text": [{"text": {"content": isbn}}]},
        "Год первой публикации": {"number": book_data.get("first_publish_year")},
        "Кратко": {"rich_text": [{"text": {"content": brief}}]},
        "Количество страниц": {"number": book_data.get("page_count")},
        "Cover": {
            "type": "files",
            "files": [
                {
                    "name": "Cover Image",
                    "type": "external",
                    "external": {"url": book_data.get("cover", "")},
                }
            ],
        },
        "Link": {"url": book_data.get("link", "")},
        "Editions count": {"number": book_data.get("editions_count")},
    }

    # Prepare multi-select fields
    prepared_data.update(prepare_multiselect_field("Авторы", authors))
    prepared_data.update(prepare_multiselect_field("Языки", standardized_languages))
    prepared_data.update(prepare_multiselect_field("Тэги", sanitized_tags))
    prepared_data.update(prepare_multiselect_field("Издатель", publishers))

    # Prepare select fields
    russian_translation = (
        "Есть" if "Русский" in standardized_languages else "Неизвестно"
    )
    prepared_data.update(
        prepare_select_field("Перевод на русский", russian_translation)
    )

    series: str | None = book_data.get("series", None)
    if series is not None:
        prepared_data["Серия"] = {"select": {"name": sanitize_field_value(series)}}

    return prepared_data
