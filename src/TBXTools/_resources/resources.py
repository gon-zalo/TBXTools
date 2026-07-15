from importlib import import_module

class Resources:
    '''
    Resource class to manage internal resources of the tool.

    Args:
        lang_code: The language ISO code of the corpus language.
    '''
    def __init__(self, lang_code):
        self.lang_code = lang_code

    def fetch_stopwords(self):
        module = import_module(f"TBXTools._resources.stopwords.{self.lang_code}")
        return module.STOPWORDS

    def fetch_inner_stopwords(self):
        module = import_module(f"TBXTools._resources.inner.{self.lang_code}")
        return module.INNER_STOPWORDS
    
