import nltk
from nltk.util import ngrams as compute_ngrams
import re
from .base import BaseExtractor
from ..results import Results
from ..methodology.tagger import LinguisticTagger
from ..utils import get_model_from_code
from ..methodology.pos_learning import PatternsLearning

class LinguisticExtractor(BaseExtractor): #add the attributes that you added to the doc string- mira si quitart cosas internas como extractor info y processor- el usuario no lo tiene que importar

    '''
    Manages linguistic terminology extraction.
    
    Attributes:
        nmin (int): The minimum number of words a candidate term can contain.
        nmax (int): The maximum number a candidate term can contain.
        _extractor_info (str): A string identifier for the extraction methodology used (defaults to "linguistic").
        _processor (Processor): An internal instance of the Processor class used to handle text preprocessing tasks.

    '''

    def __init__(self, *, nmin, nmax, input_is_tagged= False, linguistic_patterns= None, evaluation_terms= None):
        
        self.nmin = nmin
        self.nmax = nmax
        self.input_is_tagged= input_is_tagged
        self.linguistic_patterns= linguistic_patterns
        self.evaluation_terms= evaluation_terms

        self.extractor_info = "linguistic"
        self._processor= None
        self._sqlite = None
        self._tagger= None


    # MAIN FUNCTION

    def extract(self, minfreq=2):
        '''
        Prepares the linguistic extraction pipeline by validating tagged segments,
        calculating n-grams, learning POS patterns if missing, and executing the extraction.
        '''
        print("Methodology: linguistic")

        tagged_segments= self._sqlite.get_tagged_segments()

        if not tagged_segments:
            print("Corpus is not tagged. Starting POS tagging process")
                
            #Fetch raw data from the raw corpus table
            segments = self._sqlite.get_segments() 
            all_tagged_segments = []
            db_data_to_insert = []
                
            #Process and tag each raw text segment sequentially
            for segment in segments:
                single_tagged_segment= self._tagger.tag_segment(segment)

                if single_tagged_segment:
                    all_tagged_segments.append(single_tagged_segment)
                    db_data_to_insert.append((single_tagged_segment,))

            if db_data_to_insert: 
                self._sqlite.insert_tagged_segments(db_data_to_insert)
            tagged_segments= all_tagged_segments

        
        if not self._sqlite.table_is_populated("tagged_ngrams"):
            print("Tagged ngrams table is empty. Calculating ngrams")
            tagged_ngrams= self.tagged_ngram_calculation(tagged_segments, minfreq=2)

            if tagged_ngrams:
                    self._sqlite.insert_tagged_ngrams(tagged_ngrams)
            
        else:

            tagged_ngrams= self._sqlite.get_tagged_ngrams()

        
        linguistic_patterns = self._sqlite.get_linguistic_pattern() 
            
            #If no patterns exist, initialize the automatic learning phase
        if not linguistic_patterns:
            print("Table is empty. Starting automatic pattern learning")
            outputfile= "new_patterns.txt"
            
            
            pattern_learner= PatternsLearning()
            pattern_learner._sqlite = self._sqlite
            learn_dict= pattern_learner.learn_linguistic_patterns(outputfile=outputfile)

            if learn_dict:
                raw_patterns_list=list(learn_dict.keys())
                self._sqlite.load_linguistic_patterns(linguistic_patterns=raw_patterns_list)
                    
                    # Reload the freshly learned patterns from the DB
                linguistic_patterns = self._sqlite.get_linguistic_pattern()
            else:
                print("Warning: Learning process produced no patterns. Please verify database data.")

        if linguistic_patterns:
            print("Transforming patterns and updating database...")
        
            transformed_patterns = self._processor.translate_pattern(linguistic_patterns)
            
            self._sqlite.delete_linguistic_patterns()
            self._sqlite.load_linguistic_patterns(linguistic_patterns=transformed_patterns)
            
            linguistic_patterns = self._sqlite.get_linguistic_pattern()


        candidate_terms = self._linguistic_extraction(
        tagged_ngrams_output=tagged_ngrams, 
        linguistic_patterns=linguistic_patterns, 
        minfreq=minfreq
    )

        return Results(tagged_ngrams=tagged_ngrams, terms=candidate_terms, extractor_info="linguistic")
    

    #def extract(self, tagged_segments, linguistic_patterns, minfreq=2): 
        
        #print("Methodology: linguistic")

        #tagged_ngrams= self.tagged_ngram_calculation(tagged_segments, minfreq=minfreq)
        #candidate_terms= self._linguistic_extraction(tagged_ngrams_output=tagged_ngrams, linguistic_patterns=linguistic_patterns, minfreq=minfreq)

        #return Results(tagged_ngrams=tagged_ngrams, terms=candidate_terms, extractor_info="linguistic")
    
    # Implemented to separate tagged n-gram calculation from linguistic extraction,
    # which is required for the automatic learning of POS patterns.
    
    def tagged_ngram_calculation(self, tagged_segments, minfreq=2):

        ngramsFD=nltk.probability.FreqDist()
        nmin= self.nmin
        nmax= self.nmax

        for tagged_segment in tagged_segments:

            for n in range(nmin, nmax+1):  
                    tagged_ngrams = compute_ngrams(tagged_segment.split(), n) 

                    for tagged_ngram in tagged_ngrams:
                        ngramsFD[tagged_ngram] += 1 

        tagged_ngrams_output = []
        for tagged_ngram, freq in ngramsFD.most_common(): 

            if freq>=minfreq:
                candidate_words = []
                for ngt in tagged_ngram:
                    candidate_words.append(ngt.split("|")[0])
                    clean_ngram = " ".join(candidate_words)

                tagged_ngram_row=(clean_ngram, " ".join(tagged_ngram), len(tagged_ngram), freq) 
                tagged_ngrams_output.append(tagged_ngram_row)
                           
        self.ngrams = tagged_ngrams_output

        return tagged_ngrams_output
  

    def _linguistic_extraction(self, linguistic_patterns, tagged_ngrams_output, minfreq=2):

        '''Extracts candidate terms using the linguistic methodology'''

        processed_patterns=[]
        controlpatterns=[]

        for linguistic_pat in linguistic_patterns:
                linguistic_pattern=linguistic_pat[0]
                transformedpattern="^"+linguistic_pattern+"$"
                if not transformedpattern in controlpatterns:
                    processed_patterns.append(transformedpattern)
                    controlpatterns.append(transformedpattern)  

        raw_candidates=[] 

        for clean_ngram, tagged_ngram, n, frequency in tagged_ngrams_output:

            filtered_ngram= self._processor.filter_by_stopwords_linguistic(term= tagged_ngram)

            if filtered_ngram is None:
                continue
            
#you could move Move this logic into a separate function within the processor
            for pattern in processed_patterns:
                match=re.search(pattern, tagged_ngram)
                if match:
                     if match.group(0)== tagged_ngram:
                        candidate=" ".join(match.groups()[1:])
                        record=[]
                        record.append(candidate)     
                        record.append(n)
                        record.append(frequency)   
                        record.append("freq")
                        record.append(frequency)   
                        raw_candidates.append(record)
                        break
         
#make this more pythonic        
        tcaux={}
        for a in raw_candidates:
            cand_name=a[0]
            cand_freq=a[2]
            if not cand_name in tcaux:
                tcaux[cand_name]=cand_freq
            else:
                tcaux[cand_name]+= cand_freq
        
        data=[] 
        for tc in tcaux:
            record=[]
            record.append(tc)            
            record.append(len(tc.split())) 
            record.append(tcaux[tc])   
            record.append("freq")
            record.append(tcaux[tc])   
            data.append(record)
        
        return data
            

