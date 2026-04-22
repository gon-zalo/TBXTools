import nltk
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
            # print(segment)
            for n in range(n_min, n_max+1): #we DON'T calculate one order bigger in order to detect nested candidates

                tokens = segment.split() # tokenizing here, can be done separately
                # print(tokens)
                ngs = ngrams(tokens, n)

                for ng in ngs:
                    ngramsFD[ng] += 1

            for token in tokens:
                tokensFD[token] += 1

        n_grams = []
        for c in ngramsFD.most_common():
            if c[1]>=minfreq:

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
        for ngram_row in ngrams:
            ngram = ngram_row[0].lower().split()

            if ngram[0] in stopwords or ngram[-1] in stopwords:
                continue

            for element in range(1, len(ngram)):
                if ngram[element] in inner_stopwords:
                    continue
            row = []
            row.append(ngram_row[0])
            row.append(ngram_row[1])
            row.append(ngram_row[2])
            row.append("frequency")
            row.append(ngram_row[2])

            candidate_terms.append(row)
            # print(candidate_terms)

            if ngram_row[2] < min_freq:
                break

        return candidate_terms