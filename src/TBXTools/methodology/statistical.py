import nltk
from nltk.util import ngrams as compute_ngrams
from .base import BaseExtractor
from ..results import Results
from ..processor import Processor 

class StatisticalExtractor(BaseExtractor):
    '''
    Manages statistical terminology extraction.
    
    Attributes:
        nmin (int): The minimum length for the extracted n-grams.
        nmax (int): The maximum length for the extracted n-grams.
        extractor_info (str): A string identifier for the extraction methodology used (defaults to "statistical").
        _processor (Processor): An internal instance of the Processor class used to handle text preprocessing tasks.

    '''
    
    def __init__(self, nmin, nmax):
        
        self.nmin = nmin
        self.nmax = nmax

        self.extractor_info = "statistical"
        self._processor = None # passed from Extractor()
        
# MAIN FUNCTION
    def extract(self, segments, stopwords, inner_stopwords, verbose=False):
        '''
        Extracts candidate terms from text segments using a statistical methodology. This methodology is based on calculating n-grams and filtering candidates using stopwords and inner stopwords. Specifically, it removes any terms that start or end with a word in the stopword list, as well as terms that contain an inner stopword. The actual extraction logic is delegated to the '_statistical_extraction' method.

    Args:
        segments: A list of text segments to process.
        stopwords: A collection of words to ignore during extraction.
        inner_stopwords: A collection of words to ignore if they appear inside a term.
        verbose (bool, optional): If True, prints processing details. Defaults to False.

    Returns:
        Results: An object containing the candidate terms, n-grams, tokens, and extractor information. 
        '''
        print("Methodology: statistical")
        
        ngrams, tokens, candidate_terms = self._statistical_extraction(segments=segments, stopwords=stopwords, inner_stopwords=inner_stopwords)

        return Results(terms=candidate_terms, ngrams=ngrams, tokens=tokens, extractor_info=self.extractor_info)
    
# COMPUTING FUNCTIONS

    def _statistical_extraction (self, segments, stopwords, inner_stopwords, minfreq=2):
        '''
        Handles the core computation of the statistical extraction pipeline. It processes the text segments to generate tokens and n-grams, calculates their frequency distributions, and applies stopword filtering (both boundary and inner) alongside a minimum frequency threshold to isolate the final candidate terms. 

        Args:
            segments: A list of text segments to process.
            stopwords: A collection of words to ignore at the boundaries (start/end) of extraction.
            inner_stopwords: A collection of words to ignore if they appear inside a term.
            minfreq (int, optional): The minimum frequency required for an n-gram to be considered a candidate term. Defaults to 2.

        Returns:
               tuple: A tuple containing three elements:
                    - ngrams: The extracted n-grams with their respective frequencies.
                    - tokens: The tokenized words from the input segments.
                    - candidate_terms: The final filtered statistical candidate terms.
        '''
        
        ngramsFD= nltk.probability.FreqDist() 
        tokensFD= nltk.probability.FreqDist()
        nmin = self.nmin
        nmax = self.nmax
            
        for segment in segments:

                tokens= self._processor.tokenize(segment)
                
                #token frequencies
                for token in tokens:
                    tokensFD[token] += 1
                
                #ngram frequencies
                for n in range(nmin, nmax+1):  
                    ngrams = compute_ngrams(tokens, n) 

                    for ngram in ngrams:
                        ngramsFD[ngram] += 1 

        ngrams_output = []
        for ngram, freq in ngramsFD.most_common(): 

            if freq>=minfreq:
                ngrams_row=(" ".join(ngram), len(ngram), freq) 
                ngrams_output.append(ngrams_row)
                           
        self.ngrams = ngrams_output

        tokens_output = []                
        for token, freq in tokensFD.most_common(): 
            tokens_row=(token, freq)   
            tokens_output.append(tokens_row)

        self.tokens = tokens_output

        #statistical filtering
        candidate_terms = []
 
        for full_term, n, freq in ngrams_output:

            full_term = self._processor.filter_by_stopwords(term=full_term, stopwords=stopwords, inner_stopwords=inner_stopwords)

            if full_term is None:
                continue

            candidate_terms.append((full_term, n, freq, "frequency", freq))

        return ngrams_output, tokens_output, candidate_terms



    
    