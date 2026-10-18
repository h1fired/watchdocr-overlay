

MAPPED_TEXT_SEPARATOR = '\n\n'


class OcrTranslatorTextAdapter:
    def __init__(self, separator=MAPPED_TEXT_SEPARATOR):
        self._separator = separator

    def generate_mapped_string(
        self, full_text: str, parts: tuple[str, ...]
    ) -> str:
        if not full_text:
            return ''

        return self._separator.join((full_text, *parts))

    def unpack_mapped_string(
        self, text: str
    ) -> tuple[str, tuple[str, ...]]:
        if not text:
            return '', ()
        parts = text.split(self._separator)
        return parts[0], tuple(parts[1:]) if parts[1:] != [''] else ()
