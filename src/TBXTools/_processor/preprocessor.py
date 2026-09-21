import re
class Preprocessor():

    def __init__(self, methodology):
        import nltk
        import string

        self.methodology = methodology
        self.nmin = getattr(self.methodology, 'nmin', None)
        self.nmax = getattr(self.methodology, 'nmax', None)

        self.tokens_freq_dist = nltk.probability.FreqDist()
        self.ngrams_freq_dist = nltk.probability.FreqDist()
        self.tagged_ngrams_freq_dist = nltk.probability.FreqDist()
        self.punctuation = [char for char in string.punctuation if char != ["'", "|"]]
        self.stopwords = None
        self.inner_stopwords = None

    def _set_filter_parameters(self):
        self.stopwords = self.methodology.extractor.stopwords
        self.inner_stopwords = self.methodology.extractor.inner_stopwords
        self.invalid_tokens = set(self.stopwords) | set(self.punctuation)
        
    def compute_ngrams(self, tokenized_segment):
        from nltk.util import ngrams as calc_ngrams_nltk

        ngrams = []
        for n in range(self.nmin, self.nmax + 1):  
            segment_ngrams = calc_ngrams_nltk(tokenized_segment, n)

            ngrams.extend(segment_ngrams)

        return ngrams
       
    def calculate_tokens_freq_dist(self, tokenized_segment):
        self.tokens_freq_dist.update(tokenized_segment)

    def calculate_ngrams_freq_dist(self, ngrams_list):
        self.ngrams_freq_dist.update(ngrams_list)

    def clean_ngram(self, ngram):
        """
        Cleans an ngram removing punctuation from the beginning and end of the string.
        """
        ngram = ngram.strip()

        cleaned = re.sub(r"^[,.\-:;\"¿]+|[,.\-:;\"?]+$", "", ngram)

        cleaned = cleaned.strip()
        if cleaned.startswith("(") and cleaned.endswith(")"):
            cleaned = cleaned[1:-1]

        elif cleaned.startswith("("):
            cleaned = cleaned.lstrip("(")

        cleaned = cleaned.strip(   )
        if cleaned.count("(") != cleaned.count(")"):
            return None

        return cleaned

    def filter_ngram(self, ngram):
        """
        Filters an ngram by checking for invalid stopwords and punctuation. It is rejected if it contains a stopword or punctation at its boundaries (first/last element) or an inner stopword or punctuation in its middle token(s) (between the first/last elements).

        Args: 
          ngram(str): The ngram to validate.
        
        Returns:
          str or None: The original term string if it passes all  filters, otherwise None.

        """
        split_ngram = ngram.lower().split()

        # stopwords and punctuation at boundaries
        if split_ngram[0] in self.invalid_tokens or split_ngram[-1] in self.invalid_tokens:
            return None

        # inner stopwords and punctuation
        for token in split_ngram[1:-1]:
            if token in self.inner_stopwords or token in self.punctuation:
                return None

        return ngram.strip()