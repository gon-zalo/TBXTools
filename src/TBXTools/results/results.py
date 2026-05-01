class Results:

    def __init__(self, *, terms=None, ngrams=None, tokens=None, extractor_info=None):
        self._terms = terms or []
        self._ngrams = ngrams or []
        self._tokens = tokens or []
        self._extractor_info = extractor_info or None

    def ngrams(self, limit=20):
        return self._ngrams[:limit]
    
    def tokens(self, limit=20):
        return self._tokens[:limit]
    
    def terms(self, limit=20):
        terms = self._terms
        return terms
    