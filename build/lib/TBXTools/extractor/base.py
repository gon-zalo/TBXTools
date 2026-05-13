class BaseExtractor:
    def preprocess(self, corpus, **kwargs):
        raise NotImplementedError

    def extract(self, segments, **kwargs):
        raise NotImplementedError

    def postprocess(self, terms, **kwargs):
        raise NotImplementedError
