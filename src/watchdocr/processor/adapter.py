

MAPPED_TEXT_SEPARATOR = '\n\n'


class OcrTranslatorTextAdapter:
    def __init__(self, separator=MAPPED_TEXT_SEPARATOR):
        self._separator = separator

    def generate_mapped_string(self, full_text: str, boxes: tuple):
        mapped_text = (
            f'{full_text}{MAPPED_TEXT_SEPARATOR}' +
            MAPPED_TEXT_SEPARATOR.join(b.text for b in boxes)
        )
        return mapped_text

    def unpack_mapped_string(self, text: str) -> tuple[str, tuple]:
        if text == '':
            return '', tuple()
        parts = tuple(text.split(MAPPED_TEXT_SEPARATOR))
        return parts[0], parts[1:]

    def generate_translated_boxes(self, o_boxes, t_parts):
        boxes = []
        for i, (_, t) in enumerate(zip(o_boxes, t_parts)):
            boxes.append((t, o_boxes[i].boundings, o_boxes[i].confidence))
        return tuple(boxes)
