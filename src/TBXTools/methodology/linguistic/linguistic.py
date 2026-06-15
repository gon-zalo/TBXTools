import re
import sys
from collections import Counter
from ..base.base import BaseMethodology
from ...results import Results
from ...processor import Processor
from .patterns_learning import PatternsLearning

class LinguisticMethodology(BaseMethodology): #add the attributes that you added to the doc string- mira si quitart cosas internas como extractor info y processor- el usuario no lo tiene que importar

    '''
    Manages linguistic terminology extraction.
    
    Attributes:
        nmin (int): The minimum number of words a candidate term can contain.
        nmax (int): The maximum number a candidate term can contain.
        processor (Processor): An internal instance of the Processor class used to handle text preprocessing tasks.

    '''

    def __init__(self, nmin, nmax, is_corpus_tagged=False, linguistic_patterns=None, evaluation_terms=None):
        
        self.name = "LinguisticMethodology"
        self.is_corpus_tagged = is_corpus_tagged
        self.linguistic_patterns = linguistic_patterns
        self.evaluation_terms = evaluation_terms
        
        self.processor = Processor()
        self.processor.nmin = nmin 
        self.processor.nmax = nmax 

    # MAIN FUNCTION

    def extract(self, tagged_segments, tagged_ngrams, filtered_tagged_ngrams, minfreq=2, table_is_populated=False):
        '''
        Prepares the linguistic extraction pipeline by validating tagged segments,
        calculating n-grams, learning POS patterns if missing, and executing the extraction.
        '''

        if not self.linguistic_patterns: # learn patterns
            print("Linguistic patterns not found. Starting automatic pattern learning")
            pattern_learner = PatternsLearning()

            learn_dict = pattern_learner.learn_linguistic_patterns(outputfile="learned_linguistic_patterns.txt", evaluation_terms=self.evaluation_terms, filtered_tagged_ngrams=filtered_tagged_ngrams)
 
            if learn_dict:
                linguistic_patterns = list(learn_dict.keys())
                self.linguistic_patterns = linguistic_patterns

            else:
                print("Error: Learning process produced no patterns. Please verify database data.")
                sys.exit()
     
        linguistic_patterns = self.processor.translate_pattern(self.linguistic_patterns)

        candidate_terms = self._linguistic_extraction(ngrams_output=tagged_ngrams, linguistic_patterns=linguistic_patterns, minfreq=minfreq)

        return Results(tagged_ngrams=tagged_ngrams, terms=candidate_terms, linguistic_patterns=linguistic_patterns)
    
    
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
            #clean_ngram = tupla[0]
            tagged_ngram = tupla[1]
            n = tupla[2]
            frequency = tupla[3]

            filtered_ngram = self.processor.filter_by_stopwords_linguistic(term=tagged_ngram)
            if filtered_ngram is None:
                continue

#you could move Move this logic into a separate function within the processor
            for pattern in processed_patterns:
                match = re.search(pattern, tagged_ngram)
                if match:
                        
                        if match.group(0) == tagged_ngram:
                            candidate =" ".join(match.groups()[1:])
                            record=[]
                            record.append(candidate)     
                            record.append(n)  
                            record.append("frequency")
                            record.append(frequency)   
                            raw_candidates.append(record)
                            break
        
        candidate_frequencies= Counter()
        for candidate, n, _, frequency in raw_candidates: # underscore to ignore the third element "frequency" - not needed for aggregation
            candidate_frequencies[candidate] += frequency # If the candidate already exists, aggregate its frequency
        
        # Generate and return the final data structure 
        return [[term, len(term.split()), "frequency", freq] for term, freq in candidate_frequencies.items()]  # .items() yields (term, total_frequency) pairs from the Counter
        