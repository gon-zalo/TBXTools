import nltk
from nltk.util import ngrams as compute_ngrams
from .base import BaseExtractor
from ..results import Results

class StatisticalExtractor(BaseExtractor):

    def __init__(self, nmin, nmax, nest_normalization=False, nest_normalization_percent=10, stopwords=None, inner_stopwords=None):
        
        self.nmin = nmin
        self.nmax = nmax
        self.stopwords = stopwords # or a basic stopwords list
        self.inner_stopwords = inner_stopwords # or a basic inner stopwords list

        self.n_grams = None
        self.tokens = None
        self.extractor_info = "statistical"
        self.nest_normalization = nest_normalization
        self.nest_normalization_percent = nest_normalization_percent

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
    def _ngram_calculation (self, segments, minfreq=2, corpus=None):
        '''Performs the calculation of ngrams.'''
        # change variable names, fix lines 57 to 70 (transform into tuples)
        ngramsFD= nltk.probability.FreqDist() #Crea un oggetto FreqDist di NLTK per contare le frequenze degli n-grammi - esempio {'machine learning': 5, 'deep learning': 3}
        tokensFD= nltk.probability.FreqDist() 
        nmin = self.nmin
        nmax = self.nmax
            
        for segment in segments:
            for n in range(nmin, nmax+1): #we DON'T calculate one order bigger in order to detect nested candidates
                
                tokens= self.tokenize_prova_regex(segment)
                #tokens = segment.split() # tokenizing here, can be done separately
                ngrams = compute_ngrams(tokens, n)

                for ngram in ngrams:
                    ngramsFD[ngram] += 1

            for token in tokens:
                tokensFD[token] += 1

        ngrams_output = []
        for c in ngramsFD.most_common(): # what is c?
            # print(ngramsFD.most_common())
            if c[1]>=minfreq: # accessing frequency

                ngrams_row=[] # change to tuple
                ngrams_row.append(" ".join(c[0]))            
                ngrams_row.append(len(c[0]))
                ngrams_row.append(c[1])   
                ngrams_output.append(ngrams_row)

        self.ngrams = ngrams_output

        tokens_output = []                
        for c in tokensFD.most_common(): # what is c?
            tokens_row=[]
            tokens_row.append(c[0])            
            tokens_row.append(c[1])   
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
            first_word = split_term[0] #this variable is not used, but it can be useful for some filters (e.g. stop-words at the beginning of the term)- es machine learning --> first_word = machine, last_word = learning
            # last_word = split_term[-1]

            # ignoring terms that contain stopwords at the beginning or end
            if split_term[0] in self.stopwords or split_term[-1] in self.stopwords:
                continue

            # ignoring terms that contain stopwords inside
            for element in range(1, len(split_term)): #dovrebbe essere range(1, len(split_term)-1) se vogliamo escludere solo stopwords interne
                if split_term[element] in self.inner_stopwords:
                    continue

            terms_row = (full_term, n, freq, "frequency", freq)

            candidate_terms.append(terms_row)

            if freq < min_freq:
                break

        return candidate_terms
    



    #idea per migliorare statistical - da verificare

    #def _statistical_term_extraction(self, ngrams, min_freq=2):

    #candidate_terms = []

    #for row in ngrams:

        #full_term = row[0]
        #n = row[1]
        #freq = row[2]

        # --- preprocessing con regex ---
        #cleaned = re.sub(r"[^\w\s]", " ", full_term)
        #cleaned = re.sub(r"\s+", " ", cleaned).strip().lower()

        #split_term = cleaned.split()

        #if not split_term:
            #continue

        # --- rimozione stopwords iniziali/finali ---
        #while split_term and split_term[0] in self.stopwords:
            #split_term = split_term[1:]

        #while split_term and split_term[-1] in self.stopwords:
            #split_term = split_term[:-1]

        #if not split_term:
            #continue

        # --- rimozione stopwords interne ---
        #split_term = [
            #w for w in split_term
            #if w not in self.inner_stopwords
        #]

        #if not split_term:
            #continue

        #cleaned_term = " ".join(split_term)

        #terms_row = (
            #cleaned_term,
            #n,
            #freq,
            #"frequency",
            #freq
        #)

        #candidate_terms.append(terms_row)

        # attenzione: questo break è valido solo se ngrams è ordinato
        #if freq < min_freq:
            #break

    #return candidate_terms