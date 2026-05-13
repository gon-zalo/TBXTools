from importlib import import_module

class Resources:

    def __init__(self, lang_code):
        self.lang_code = lang_code

    def fetch_stopwords(self):
        module = import_module(f"TBXTools.resources.stopwords.{self.lang_code}")
        return module.STOPWORDS

    def fetch_inner_stopwords(self):
        module = import_module(f"TBXTools.resources.inner.{self.lang_code}")
        return module.INNER_STOPWORDS