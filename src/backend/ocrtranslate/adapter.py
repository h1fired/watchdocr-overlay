

MAPPED_TEXT_SEPARATOR = '\n\n'


class OcrTranslatorTextAdapter:
    def __init__(self, separator=MAPPED_TEXT_SEPARATOR):
        self._separator = separator

    def generate_mapped_string(self, full_text: str, parts: tuple[str]):
        if full_text == '':
            return ''

        mapped_text = (
            f'{full_text}{self._separator}' +
            self._separator.join(parts)
        )
        return mapped_text

    def unpack_mapped_string(self, text: str) -> tuple[str, tuple]:
        if text == '':
            return '', tuple()
        parts = tuple(text.split(self._separator))
        return parts[0], parts[1:]
