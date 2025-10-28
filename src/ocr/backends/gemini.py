from src.ocr.backends import OcrBackend, OcrStatus
from google import genai
from google.genai import types
import io


MODEL = 'gemini-2.0-flash-lite'
PROMPT = (
    'Act like text scanner, OCR model.'
    'Recognize text from image and give only recognized text.'
    'Without any descriptions.'
)


class GeminiOCRBackend(OcrBackend):
    name = 'Gemini'

    def __init__(self):
        self._client = genai.Client()

    def recognize(self, image):
        buf = io.BytesIO()
        image.save(buf, 'JPEG')

        response = self._client.models.generate_content(
            model=MODEL,
            contents=[
                types.Part.from_bytes(
                    data=buf.getvalue(),
                    mime_type='image/jpeg',
                ),
                PROMPT
            ]
        )
        buf.close()
        return {'status': OcrStatus.SUCCESS, 'text': response.text}
