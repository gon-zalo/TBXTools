import nltk
from nltk.util import ngrams as compute_ngrams
from .base import BaseExtractor
from ..results import Results
from ..processor import Processor 

class StatisticalExtractor(BaseExtractor):

    def __init__(self, nmin, nmax, nest_normalization=False, nest_normalization_percent=10, stopwords=None, inner_stopwords=None):
        
        self.nmin = nmin
        self.nmax = nmax
        self.stopwords = stopwords 
        self.inner_stopwords = inner_stopwords 

        self.n_grams = None
        self.tokens = None
        self.extractor_info = "statistical"
        self.nest_normalization = nest_normalization
        self.nest_normalization_percent = nest_normalization_percent
        self._processor= Processor()
        
# MAIN FUNCTION
    def extract(self, segments, verbose):
        print("Running statistical extraction")
        nmin = self.nmin
        nmax = self.nmax
        
        ngrams, tokens, candidate_terms = self._statistical_extraction(segments, nmin, nmax)

        return Results(terms=candidate_terms, ngrams=ngrams, tokens=tokens, extractor_info=self.extractor_info)
    
# COMPUTING FUNCTIONS

    def _statistical_extraction (self, segments, minfreq=2, corpus=None):
        '''
        Extract ngrams and tokens, computes their frequencies and performs statistical term extraction.
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

            full_term = self._processor.filter_by_stopwords(full_term, self.stopwords,self.inner_stopwords)

            if full_term is None:
                continue


            candidate_terms.append((full_term, n, freq, "frequency", freq))

        return ngrams_output, tokens_output, candidate_terms



    
    