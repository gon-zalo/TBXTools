class Results:

    def __init__(self, *, terms=None, ngrams=None, tokens=None, extractor_info=None):
        self._terms = terms or []
        self._ngrams = ngrams or []
        self._tokens = tokens or []
        self._extractor_info = extractor_info or None

# ACCESSING ATTRIBUTES
    # [0] is the first element in the tuple (table row)
    def terms(self, limit=20):
        terms = [term[0] for term in self._terms]
        return terms[:limit]

    def tokens(self, limit=20):
        tokens = [token[0] for token in self._tokens]
        return tokens[:limit]
    