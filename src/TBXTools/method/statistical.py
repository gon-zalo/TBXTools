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
        
        print("Computing n grams")
        ngrams, tokens = self._ngram_calculation(segments, nmin, nmax)
        candidate_terms = self._statistical_term_extraction(ngrams=ngrams)

        return Results(terms=candidate_terms, ngrams=ngrams, tokens=tokens, extractor_info=self.extractor_info)
# COMPUTING FUNCTIONS

#it works
    def _ngram_calculation (self, segments, minfreq=2, corpus=None):
        '''Performs the calculation of ngrams.'''
        ngramsFD= nltk.probability.FreqDist() #object to count ngrams frequence - it workks like a dictionary- {'machine learning': 5, 'deep learning': 3}
        tokensFD= nltk.probability.FreqDist()
        nmin = self.nmin
        nmax = self.nmax
            
        for segment in segments:
            for n in range(nmin, nmax+1): #we DON'T calculate one order bigger in order to detect nested candidates
                #for each segment it tries every dimension of ngram 

                tokens= self._processor.tokenize(segment)
                #tokens = segment.split() # tokenizing here, can be done separately
                ngrams = compute_ngrams(tokens, n) #funzione esterna che calcola ngrammi- es da tokens = ['I', 'love', 'NLP'] con n=2 produce [('I', 'love'), ('love', 'NLP')]


                for ngram in ngrams:
                    ngramsFD[ngram] += 1 #incrementa la freq dell'n gramma

            for token in tokens:
                tokensFD[token] += 1

        ngrams_output = []
        for tuple_ngram_freq in ngramsFD.most_common(): # what is c? c is a tuple- ((token1, token2), frequenza)
            # print(ngramsFD.most_common())

            ngrama= tuple_ngram_freq[0]
            freq= tuple_ngram_freq[1]

            if freq>=minfreq:
                ngrams_row=(
                    " ".join(ngrama), #unire termini tupla in una stringa- (machine, learning) a (machine learning)
                    len(ngrama), #quanti n grams- machine learning- n= 2
                    freq
                ) 

                ngrams_output.append(ngrams_row)
                           

        self.ngrams = ngrams_output

        tokens_output = []                
        for tuple_token_freq in tokensFD.most_common(): 

            the_token= tuple_token_freq[0]
            freq_token= tuple_token_freq[1]

            tokens_row=(the_token,
                        freq_token)
    
            tokens_output.append(tokens_row)

        self.tokens = tokens_output

        return ngrams_output, tokens_output


    def _statistical_term_extraction(self, ngrams, min_freq=2):
        '''Performs an statistical term extraction using the extracted ngrams (ngram_calculation should be executed first). Loading stop-words is advisable. '''

        candidate_terms = []
        for row in ngrams:

            # row is (full_term, n, freq)
            full_term = row[0]
            n = row[1]
            freq = row[2]

            split_term = full_term.lower().split()
            first_word = split_term[0]



            # ignoring terms that contain stopwords at the beginning or end
            if split_term[0] in self.stopwords or split_term[-1] in self.stopwords:
                continue
#
        
            for element in range(1, len(split_term)):
                if split_term[element] in self.inner_stopwords:
                    continue

            terms_row = (full_term, n, freq, "frequency", freq)

            candidate_terms.append(terms_row)

            if freq < min_freq:
                break

        return candidate_terms
    