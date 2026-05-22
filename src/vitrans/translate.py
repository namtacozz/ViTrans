import time

from deep_translator import GoogleTranslator


class TranslationError(RuntimeError):
    pass


def translate_texts(texts: list[str], target_language: str = "vi", attempts: int = 2) -> list[str]:
    if not texts:
        return []

    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            translator = GoogleTranslator(source="auto", target=target_language)
            return translator.translate_batch(texts)
        except Exception as exc:
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(0.5)

    raise TranslationError(str(last_error))
