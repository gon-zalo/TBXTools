import nltk
from ..base.base import BaseMethodology
from ...results import Results
from ...processor import Processor

class StatisticalMethodology(BaseMethodology):
    '''
    Manages statistical terminology extraction.
    
    Attributes:
        nmin (int): The minimum number of words a candidate term can contain.
        nmax (int): The maximum number of words a candidate term can contain.
        _processor (Processor): An internal instance of the Processor class used to handle text preprocessing tasks.
    '''
    
    def __init__(self, nmin, nmax, case_normalization=False):
        
        self.name = "StatisticalMethodology"
        self.case_normalization = case_normalization
        
        self.processor = Processor()
        self.processor.nmin = nmin    
        self.processor.nmax = nmax    

# MAIN FUNCTION
    def extract(self, segments, verbose=False):
        '''
    Extracts candidate terms from text segments using a statistical methodology. This methodology is based on calculating n-grams and filtering candidates using stopwords and inner stopwords. Specifically, it removes any terms that start or end with a word in the stopword list, as well as terms that contain an inner stopword. The actual extraction logic is delegated to the '_statistical_extraction' method.

    Args:
        segments: A list of text segments to process.
        verbose (bool, optional): If True, enables detailed logging. Defaults to False.

    Returns:
        Results: An object containing the candidate terms, n-grams, tokens, and extractor information. 
        '''
        
        ngrams, tokens, candidate_terms = self._statistical_extraction(segments=segments)

        if self.case_normalization:
             candidate_terms = self.processor.case_normalization(
                candidate_terms=candidate_terms, 
                verbose=verbose) 
                
        return Results(terms=candidate_terms, ngrams=ngrams, tokens=tokens)
    
# COMPUTING FUNCTIONS
    def _statistical_extraction (self, segments, minfreq=2):
        '''
        Handles the core computation of the statistical extraction pipeline. It processes the text segments to generate tokens and n-grams, calculates their frequency distributions, and applies stopword filtering (both boundary and inner) alongside a minimum frequency threshold to isolate the final candidate terms. 

        Args:
            segments: A list of text segments to process.
            minfreq (int, optional): The minimum frequency required for an n-gram to be considered a candidate term. Defaults to 2.

        Returns:
               tuple: A tuple containing three elements:
                    - ngrams: The extracted n-grams with their respective frequencies.
                    - tokens: The tokenized words from the input segments.
                    - candidate_terms: The final filtered statistical candidate terms.
        '''
        
        #tokens calculation

        tokensFD= nltk.probability.FreqDist()
        for segment in segments:
            tokens= self.processor.tokenize(segment)
            for token in tokens:
                    tokensFD[token] += 1
        
        tokens_output = []                
        for token, freq in tokensFD.most_common():
             tokens_output.append((token, freq))

        self.tokens = tokens_output

        #ngrams calculation
        ngrams_output, _= self.processor.ngram_calculation(segments=segments)
        self.ngrams = ngrams_output
       
        #statistical filtering
        candidate_terms = []
        for full_term, n, freq in ngrams_output:
            full_term = self.processor.filter_by_stopwords(term=full_term)

            if full_term is None:
                continue

            candidate_terms.append((full_term, n, "frequency", freq))

        return ngrams_output, tokens_output, candidate_terms