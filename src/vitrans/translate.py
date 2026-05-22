import time

from deep_translator import GoogleTranslator


class TranslationError(RuntimeError):
    pass


_TRANSLATION_CACHE: dict[tuple[str, str], str] = {}


def translate_texts(texts: list[str], target_language: str = "vi", attempts: int = 2) -> list[str]:
    if not texts:
        return []

    missing_texts = [text for text in dict.fromkeys(texts) if (target_language, text) not in _TRANSLATION_CACHE]
    if missing_texts:
        _translate_missing_texts(missing_texts, target_language, attempts)

    return [_TRANSLATION_CACHE[(target_language, text)] for text in texts]


def _translate_missing_texts(texts: list[str], target_language: str, attempts: int) -> None:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            translator = GoogleTranslator(source="auto", target=target_language)
            translations = translator.translate_batch(texts)
            for text, translated in zip(texts, translations, strict=True):
                _TRANSLATION_CACHE[(target_language, text)] = translated
            return
        except Exception as exc:
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(0.5)

    raise TranslationError(str(last_error))
