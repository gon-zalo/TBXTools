import re
from ..base.base import BaseMethodology
from ...results import Results
from ...processor import Processor
from .patterns_learning import PatternsLearning
from collections import Counter

class LinguisticMethodology(BaseMethodology): 

    '''
    Manages linguistic terminology extraction.
    
    Attributes:
        nmin (int): The minimum number of words a candidate term can contain.
        nmax (int): The maximum number a candidate term can contain.
        processor (Processor): An internal instance of the Processor class used to handle text preprocessing tasks.

    '''

    def __init__(self, nmin, nmax, is_corpus_tagged=False, linguistic_patterns=None, evaluation_terms=None, tsr_terms=None):
        
        self.name = "LinguisticMethodology"
        self.is_corpus_tagged = is_corpus_tagged
        self.linguistic_patterns = linguistic_patterns
        self.evaluation_terms = evaluation_terms
        self.tsr_terms = tsr_terms 
        
        self.processor = Processor()
        self.processor.nmin = nmin 
        self.processor.nmax = nmax 

    # MAIN FUNCTION

    def extract(self, segments, tagged_segments, minfreq=2, verbose=False):
        '''
        Prepares the linguistic extraction pipeline by validating tagged segments,
        calculating n-grams, learning POS patterns if missing, and executing the extraction.
        '''

        if not tagged_segments:
            tagged_segments = self.processor.create_tagged_segments(segments=segments)

        clean_ngrams, tagged_ngrams = self.processor.ngram_calculation(segments=tagged_segments, is_corpus_tagged=True) # never change boolean, since we are passing tagged_segments then corpus is tagged now
        
        filtered_tagged_ngrams = []
        combined_ngrams = list(zip(clean_ngrams, tagged_ngrams))
        for term in self.evaluation_terms:
            for row in combined_ngrams:
                clean_ngram = row[0][0]
                tagged_ngram = row[1][0]
                n = row[1][1]
                freq = row[1][2]
                if term == clean_ngram:
                    row = (tagged_ngram, n, freq)
                    filtered_tagged_ngrams.append(row)

        if not self.linguistic_patterns: # learn patterns
            print("Linguistic patterns not found. Starting automatic pattern learning")
            pattern_learner = PatternsLearning()

            learn_dict = pattern_learner.learn_linguistic_patterns(outputfile="learned_linguistic_patterns.txt", filtered_tagged_ngrams=filtered_tagged_ngrams, verbose=verbose)
 
            if learn_dict:
                #added to order the patterns by frequency
                sorted_patterns = sorted(learn_dict.keys(), key=lambda x: learn_dict[x], reverse=True)
                linguistic_patterns = list(sorted_patterns)
                self.linguistic_patterns = [(linguistic_pattern,) for linguistic_pattern in linguistic_patterns] # strings must be in tuples

            else:
                raise ValueError("Learning process produced no patterns. Please verify database data.")
     
        translated_linguistic_patterns = self.processor.translate_pattern(self.linguistic_patterns)
        candidate_terms = self._linguistic_extraction(ngrams_output=tagged_ngrams, linguistic_patterns=translated_linguistic_patterns, minfreq=minfreq)

        return Results(tagged_ngrams=tagged_ngrams,
                       ngrams=clean_ngrams, 
                       terms=candidate_terms, 
                       linguistic_patterns=self.linguistic_patterns), tagged_segments # returning these, in case they were created, to be stored in the db
    
    
    def _linguistic_extraction(self, linguistic_patterns, ngrams_output, minfreq=2):

        '''Extracts candidate terms using the linguistic methodology'''

        processed_patterns=[]
        controlpatterns=[]

        for linguistic_pat in linguistic_patterns:
                transformedpattern="^"+linguistic_pat+"$"
                if not transformedpattern in controlpatterns:
                    processed_patterns.append(transformedpattern)
                    controlpatterns.append(transformedpattern)  

        raw_candidates=[]
        for tupla in ngrams_output:
            tagged_ngram = tupla[0]
            n = tupla[1]
            frequency = tupla[2]

            filtered_ngram = self.processor.filter_by_stopwords_linguistic(term=tagged_ngram)

            if filtered_ngram is None:
                continue

            for pattern in processed_patterns:
                match = re.search(pattern, tagged_ngram) 
                if match:          
                        if match.group(0) == tagged_ngram:
                            candidate =" ".join(match.groups()[1:])
                            raw_candidates.append((candidate, n, "frequency", frequency))
                            break
        
        candidate_frequencies= Counter()
        for candidate, n, _, frequency in raw_candidates: # underscore to ignore the third element "frequency" - not needed for aggregation
            candidate_frequencies[candidate] += frequency # If the candidate already exists, aggregate its frequency
        
        # Generate and return the final data structure 
        return [[term, len(term.split()), "frequency", freq] for term, freq in candidate_frequencies.items()]  # .items() yields (term, total_frequency) pairs from the Counter
        