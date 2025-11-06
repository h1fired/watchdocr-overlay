from src.ocr.backends import OcrBackend, OcrStatus, OcrData
from tesserocr import PyTessBaseAPI, PSM, OEM, RIL, iterate_level
import re


DATA_MODELS_DIR = 'data/tessdata-4.1.0'


def clean_text(text: str):
    # Remove hyphenation at line breaks
    text = re.sub(r'-\n', '', text)
    # Normalize whitespace and newlines
    text = re.sub(r'\s+', ' ', text)
    # Remove non-printable ASCII characters (except newlines)
    text = re.sub(r'[^\x20-\x7E\n]', '', text)
    # Replace single newlines (not
    # part of paragraph breaks) with spaces
    text = re.sub(r'\n(?!\s*\n)', ' ', text)
    # Collapse multiple newlines into a single blank line
    text = re.sub(r'\n{2,}', '\n', text)

    return text.strip()


class TesseractOcrBackend(OcrBackend):
    name = 'Tesseract'

    def __init__(self):
        self._api = PyTessBaseAPI(
            path=DATA_MODELS_DIR,
            oem=OEM.LSTM_ONLY,
            psm=PSM.SPARSE_TEXT_OSD
        )

    def recognize(self, image):
        try:
            self._api.SetImage(image)

            # Get general cleaned text
            text = self._api.GetUTF8Text()
            cleaned_text = clean_text(text)

            # Get components parameters (words, boxes, confidences)
            details = OcrData()
            ri = self._api.GetIterator()
            level = RIL.WORD
            for r in iterate_level(ri, level):
                word = r.GetUTF8Text(level)
                box = r.BoundingBox(level)
                conf = r.Confidence(level)
                details.push(word, box, conf)

        except Exception as e:
            return {'status': OcrStatus.ERROR, 'text': repr(e), 'data': details}
        return {'status': OcrStatus.SUCCESS, 'text': cleaned_text, 'data': details}
