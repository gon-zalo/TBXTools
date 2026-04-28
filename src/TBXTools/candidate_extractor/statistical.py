from nltk.util import ngrams
from nltk.probability import FreqDist

class StatisticalExtractor:

    def __init__(self):
        self.n_grams = None
        self.tokens = None

    def ngram_calculation (self, segments, n_min, n_max, minfreq=2, corpus=None):
        '''Performs the calculation of ngrams.'''
        
        ngramsFD= FreqDist()
        tokensFD= FreqDist()
        n_min = n_min
        n_max = n_max
            
        for segment in segments:
            for n in range(n_min, n_max+1): #we DON'T calculate one order bigger in order to detect nested candidates

                tokens = segment.split() # tokenizing here, can be done separately
                ngs = ngrams(tokens, n)

                for ng in ngs:
                    ngramsFD[ng] += 1

            for token in tokens:
                tokensFD[token] += 1

        n_grams = []
        for c in ngramsFD.most_common():
            # print(ngramsFD.most_common())
            if c[1]>=minfreq: # accessing frequency

                ngrams_row=[] # change
                ngrams_row.append(" ".join(c[0]))            
                ngrams_row.append(len(c[0]))
                ngrams_row.append(c[1])   
                n_grams.append(ngrams_row)

        self.n_grams = n_grams

        tokens_output = []                
        for c in tokensFD.most_common():
            tokens_row=[]
            tokens_row.append(c[0])            
            tokens_row.append(c[1])   
            tokens_output.append(tokens_row)

        self.tokens = tokens_output

        return n_grams, tokens_output

    def statistical_term_extraction(self, ngrams, min_freq=2, stopwords=None, inner_stopwords=None):
        '''Performs an statistical term extraction using the extracted ngrams (ngram_calculation should be executed first). Loading stop-words is advisable. '''

        candidate_terms = []
        for row in ngrams:

            # row is (full_term, n, freq)
            full_term = row[0]
            n = row[1]
            freq = row[2]

            split_term = full_term.lower().split()

            # ignoring terms that contain stopwords at the beginning or end
            if split_term[0] in stopwords or split_term[-1] in stopwords:
                continue

            # ignoring terms that contain stopwords inside
            for element in range(1, len(split_term)):
                if split_term[element] in inner_stopwords:
                    continue

            terms_row = (full_term, n, freq, "frequency", freq)

            candidate_terms.append(terms_row)

            if freq < min_freq:
                break

        return candidate_terms