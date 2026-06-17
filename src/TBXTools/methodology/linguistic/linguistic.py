import re
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

    def extract(self, segments, tagged_segments, minfreq=2):
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

            learn_dict = pattern_learner.learn_linguistic_patterns(outputfile="learned_linguistic_patterns.txt", evaluation_terms=self.evaluation_terms, filtered_tagged_ngrams=filtered_tagged_ngrams)
 
            if learn_dict:
                linguistic_patterns = list(learn_dict.keys())
                self.linguistic_patterns = [(linguistic_pattern,) for linguistic_pattern in linguistic_patterns] # strings must be in tuples

            else:
                raise ValueError("Learning process produced no patterns. Please verify database data.")
     
        translated_linguistic_patterns = self.processor.translate_pattern(self.linguistic_patterns)
        candidate_terms = self._linguistic_extraction(ngrams_output=tagged_ngrams, linguistic_patterns=translated_linguistic_patterns, minfreq=minfreq)

        return Results(tagged_ngrams=tagged_ngrams, 
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

#you could move Move this logic into a separate function within the processor
            for pattern in processed_patterns:
                match = re.search(pattern, tagged_ngram)
                if match:
                        
                        if match.group(0)== tagged_ngram:
                            candidate =" ".join(match.groups()[1:])
                            record=[]
                            record.append(candidate)     
                            record.append(n)  
                            record.append("frequency")
                            record.append(frequency)   
                            raw_candidates.append(record)
                            break
         
#make this more pythonic        
        tcaux={}
        for a in raw_candidates: # tuple is (tagged_ngram, n, "frequency", frequency)
            cand_name=a[0]
            cand_freq=a[3]
            if not cand_name in tcaux:
                tcaux[cand_name]=cand_freq
            else:
                tcaux[cand_name]+= cand_freq
        
        data=[] 
        for tc in tcaux:
            record=[]
            record.append(tc)            
            record.append(len(tc.split()))    
            record.append("frequency")
            record.append(tcaux[tc])   
            data.append(record)
        
        return data