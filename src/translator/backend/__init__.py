

class TranslationBackend:

    def load(self):
        pass

    def translate(self, text: str, translate_to: str = 'EN'):
        raise NotImplementedError
