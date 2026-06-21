import ctypes
import os
import copy
from ctypes import Structure, byref, POINTER, c_int64, c_int32, c_float, c_ubyte, c_char, c_char_p
from PIL import Image
from dataclasses import dataclass


MODEL_NAME = 'oneocr.onemodel'
DLL_NAME = 'oneocr.dll'
MODEL_KEY = b"kj)TGtrK>f]b[Piow.gU+nC@s\"\"\"\"\"\"4"


c_int64_p = POINTER(c_int64)
c_float_p = POINTER(c_float)
c_ubyte_p = POINTER(c_ubyte)


class ImageStructure(Structure):
    '''Image data structure'''
    _fields_ = [
        ('type', c_int32),
        ('width', c_int32),  # Image width in pixels
        ('height', c_int32),  # Image height in pixels
        ('_reserved', c_int32),
        ('step_size', c_int64),  # Bytes per row
        ('data_ptr', c_ubyte_p)  # Pointer to image data
    ]


class BoundingBox(Structure):
    '''Text bounding box coordinates'''
    _fields_ = [
        ('x1', c_float),
        ('y1', c_float),
        ('x2', c_float),
        ('y2', c_float),
        ('x3', c_float),
        ('y3', c_float),
        ('x4', c_float),
        ('y4', c_float)
    ]


BoundingBox_p = POINTER(BoundingBox)


DLL_FUNCTIONS = [
    ('CreateOcrInitOptions', [c_int64_p], c_int64),
    ('OcrInitOptionsSetUseModelDelayLoad', [c_int64, c_char], c_int64),
    ('CreateOcrPipeline', [c_char_p, c_char_p, c_int64, c_int64_p], c_int64),
    ('CreateOcrProcessOptions', [c_int64_p], c_int64),
    ('OcrProcessOptionsSetMaxRecognitionLineCount', [c_int64, c_int64], c_int64),
    ('RunOcrPipeline', [c_int64, POINTER(ImageStructure), c_int64, c_int64_p], c_int64),

    ('GetImageAngle', [c_int64, c_float_p], c_int64),
    ('GetOcrLineCount', [c_int64, c_int64_p], c_int64),
    ('GetOcrLine', [c_int64, c_int64, c_int64_p], c_int64),
    ('GetOcrLineContent', [c_int64, POINTER(c_char_p)], c_int64),
    ('GetOcrLineBoundingBox', [c_int64, POINTER(BoundingBox_p)], c_int64),
    ('GetOcrLineWordCount', [c_int64, c_int64_p], c_int64),
    ('GetOcrWord', [c_int64, c_int64, c_int64_p], c_int64),
    ('GetOcrWordContent', [c_int64, POINTER(c_char_p)], c_int64),
    ('GetOcrWordBoundingBox', [c_int64, POINTER(BoundingBox_p)], c_int64),
    ('GetOcrWordConfidence', [c_int64, c_float_p], c_int64),

    ('ReleaseOcrResult', [c_int64], None),
    ('ReleaseOcrInitOptions', [c_int64], None),
    ('ReleaseOcrPipeline', [c_int64], None),
    ('ReleaseOcrProcessOptions', [c_int64], None)
]


@dataclass(slots=True, frozen=True)
class OcrWord:
    text: str
    boundings: tuple[int, int, int, int, int, int, int, int]
    confidence: float


@dataclass(slots=True, frozen=True)
class OcrLine:
    text: str
    boundings: tuple[int, int, int, int, int, int, int, int]
    words: tuple[OcrWord, ...]


@dataclass(slots=True, frozen=True)
class OcrOutputData:
    text: str
    lines: tuple[OcrLine, ...]
    angle: float


class OcrEngine:
    def __init__(self, dlls_path: str):
        self._dlls_path = dlls_path
        self._load_dll()
        self.init_options = self._create_init_options()
        self.pipeline = self._create_pipeline()
        self.process_options = self._create_process_options()
        self.empty_result = OcrOutputData('', tuple(), 0.)

    def recognize(self, image: Image.Image):
        '''Process PIL Image object'''
        if any(x < 50 or x > 10000 for x in image.size):
            result = copy.deepcopy(self.empty_result)
            result['error'] = 'Unsupported image size'
            return result

        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        # Convert to BGRA format expected by DLL
        b, g, r, a = image.split()
        bgra_image = Image.merge('RGBA', (b, g, r, a))

        return self._process_image(
            cols=bgra_image.width,
            rows=bgra_image.height,
            step=bgra_image.width * 4,
            data=bgra_image.tobytes()
        )

    def __del__(self):
        if self.ocr_dll:
            self.ocr_dll.ReleaseOcrProcessOptions(self.process_options)
            self.ocr_dll.ReleaseOcrPipeline(self.pipeline)
            self.ocr_dll.ReleaseOcrInitOptions(self.init_options)

    def _bind_dll_functions(self, dll, functions):
        '''Dynamically bind function specifications to DLL methods'''
        for name, argtypes, restype in functions:
            try:
                func = getattr(dll, name)
                func.argtypes = argtypes
                func.restype = restype
            except AttributeError as e:
                raise RuntimeError(f'Missing DLL function: {name}') from e

    def _load_dll(self):
        self.ocr_dll = None
        try:
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            if hasattr(kernel32, 'SetDllDirectoryW'):
                kernel32.SetDllDirectoryW(self._dlls_path)

            dll_path = os.path.join(self._dlls_path, DLL_NAME)
            ocr_dll = ctypes.WinDLL(dll_path)
            self._bind_dll_functions(ocr_dll, DLL_FUNCTIONS)
            self.ocr_dll = ocr_dll
        except (OSError, RuntimeError) as e:
            raise RuntimeError(f'DLL initialization failed: {e}') from e

    def _create_init_options(self):
        init_options = c_int64()
        self._check_dll_result(
            self.ocr_dll.CreateOcrInitOptions(byref(init_options)),
            'Init options creation failed'
        )

        self._check_dll_result(
            self.ocr_dll.OcrInitOptionsSetUseModelDelayLoad(init_options, 0),
            'Model loading config failed'
        )
        return init_options

    def _create_pipeline(self):
        model_path = os.path.join(self._dlls_path, MODEL_NAME)
        model_buf = ctypes.create_string_buffer(model_path.encode())
        key_buf = ctypes.create_string_buffer(MODEL_KEY)

        pipeline = c_int64()
        self._check_dll_result(
            self.ocr_dll.CreateOcrPipeline(
                model_buf,
                key_buf,
                self.init_options,
                byref(pipeline)
            ),
            'Pipeline creation failed'
        )
        return pipeline

    def _create_process_options(self):
        process_options = c_int64()
        self._check_dll_result(
            self.ocr_dll.CreateOcrProcessOptions(byref(process_options)),
            'Process options creation failed'
        )

        self._check_dll_result(
            self.ocr_dll.OcrProcessOptionsSetMaxRecognitionLineCount(
                process_options, 1000),
            'Line count config failed'
        )
        return process_options

    def _process_image(self, cols, rows, step, data):
        '''Create image structure'''
        if isinstance(data, bytes):
            data_ptr = (c_ubyte * len(data)).from_buffer_copy(data)
        else:
            data_ptr = ctypes.cast(ctypes.c_void_p(data), c_ubyte_p)

        img_struct = ImageStructure(
            type=3,
            width=cols,
            height=rows,
            _reserved=0,
            step_size=step,
            data_ptr=data_ptr
        )

        return self._perform_ocr(img_struct)

    def _perform_ocr(self, image_struct):
        '''Execute OCR pipeline and parse results'''
        ocr_result = c_int64()
        if self.ocr_dll.RunOcrPipeline(
            self.pipeline,
            byref(image_struct),
            self.process_options,
            byref(ocr_result)
        ) != 0:
            return self.empty_result

        parsed_result = self._parse_ocr_results(ocr_result)
        self.ocr_dll.ReleaseOcrResult(ocr_result)
        return parsed_result

    def _parse_ocr_results(self, ocr_result):
        '''Extract and format OCR results from DLL'''
        line_count = c_int64()
        if self.ocr_dll.GetOcrLineCount(ocr_result, byref(line_count)) != 0:
            return self.empty_result

        lines = self._get_lines(ocr_result, line_count)
        return OcrOutputData(
            text='\n'.join(line.text for line in lines),
            angle=self._get_text_angle(ocr_result),
            lines=lines
        )

    def _get_text_angle(self, ocr_result):
        '''Extract text angle'''
        text_angle = c_float()
        if self.ocr_dll.GetImageAngle(ocr_result, byref(text_angle)) != 0:
            return 0.
        return text_angle.value

    def _get_lines(self, ocr_result, line_count):
        '''Extract individual text lines'''
        return tuple([self._process_line(ocr_result, idx) for idx in range(line_count.value)])

    def _process_line(self, ocr_result, line_index):
        '''Process a single text line'''
        line_handle = c_int64()
        if self.ocr_dll.GetOcrLine(ocr_result, line_index, byref(line_handle)) != 0:
            return OcrLine('', tuple(), tuple())

        return OcrLine(
            text=self._get_text(line_handle, self.ocr_dll.GetOcrLineContent),
            boundings=self._get_bounding_box(line_handle, self.ocr_dll.GetOcrLineBoundingBox),
            words=self._get_words(line_handle)
        )

    def _get_words(self, line_handle) -> tuple[OcrWord, ...]:
        '''Extract words from a text line'''
        word_count = c_int64()
        if self.ocr_dll.GetOcrLineWordCount(line_handle, byref(word_count)) != 0:
            return tuple()

        return tuple([self._process_word(line_handle, idx) for idx in range(word_count.value)])

    def _process_word(self, line_handle, word_index):
        '''Process individual word'''
        word_handle = c_int64()
        if self.ocr_dll.GetOcrWord(line_handle, word_index, byref(word_handle)) != 0:
            return OcrWord('', tuple(), 0.)

        return OcrWord(
            text=self._get_text(word_handle, self.ocr_dll.GetOcrWordContent),
            boundings=self._get_bounding_box(word_handle, self.ocr_dll.GetOcrWordBoundingBox),
            confidence=self._get_word_confidence(word_handle)
        )

    def _get_text(self, handle, text_function):
        '''Extract text content from handle'''
        content = c_char_p()
        if text_function(handle, byref(content)) == 0:
            return content.value.decode('utf-8', errors='ignore')
        return None

    def _get_bounding_box(self, handle, bbox_function) -> tuple:
        '''Extract bounding box from handle'''
        bbox_ptr = BoundingBox_p()
        if bbox_function(handle, byref(bbox_ptr)) == 0 and bbox_ptr:
            bbox = bbox_ptr.contents
            return (
                int(bbox.x1),
                int(bbox.y1),
                int(bbox.x2),
                int(bbox.y2),
                int(bbox.x3),
                int(bbox.y3),
                int(bbox.x4),
                int(bbox.y4)
            )
        return tuple()

    def _get_word_confidence(self, word_handle):
        '''Extract confidence value from word handle'''
        confidence = c_float()
        if self.ocr_dll.GetOcrWordConfidence(word_handle, byref(confidence)) == 0:
            return confidence.value
        return None

    def _check_dll_result(self, result_code, error_message):
        if result_code != 0:
            raise RuntimeError(f'{error_message} (Code: {result_code})')
