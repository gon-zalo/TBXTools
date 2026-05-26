import nltk
from nltk.util import ngrams as compute_ngrams
import re
from .base import BaseExtractor
from ..results import Results

class LinguisticExtractor(BaseExtractor):

    '''
    Manages linguistic terminology extraction.
    
    Attributes:
        nmin (int): The minimum number of words a candidate term can contain.
        nmax (int): The maximum number a candidate term can contain.
        extractor_info (str): A string identifier for the extraction methodology used (defaults to "linguistic").
        _processor (Processor): An internal instance of the Processor class used to handle text preprocessing tasks.

    '''

    def __init__(self, nmin, nmax):
        
        self.nmin = nmin
        self.nmax = nmax

        self.extractor_info = "linguistic"
        self._processor= None

    # MAIN FUNCTION

    def ling_extract(self, tagged_segments, linguistic_patterns, minfreq=2): 
        
        print("Methodology: linguistic")

        candidate_terms, tagged_ngrams= self._linguistic_extraction(tagged_segments=tagged_segments, linguistic_patterns=linguistic_patterns, minfreq=minfreq)

        return Results(tagged_ngrams=tagged_ngrams, terms=candidate_terms, extractor_info="linguistic")

    #qui da qualche parte mi mette insieme singolari e plurali- es mental disorder- cerca di capire perché
    #tieni in conto che però questo lo faceva anche nel codice vecchio quindi bo
    def _linguistic_extraction(self, tagged_segments, linguistic_patterns, minfreq=2):

        '''Calculates the tagged ngrams and extract candidate terms using the linguistic methodology'''

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
                tagged_ngram_row=(" ".join(tagged_ngram), len(tagged_ngram), freq) 
                tagged_ngrams_output.append(tagged_ngram_row)
                           
        self.ngrams = tagged_ngrams_output
        
        processed_patterns=[]
        controlpatterns=[]

        for linguistic_pat in linguistic_patterns:
                linguistic_pattern=linguistic_pat[0]
                transformedpattern="^"+linguistic_pattern+"$"
                if not transformedpattern in controlpatterns:
                    processed_patterns.append(transformedpattern)
                    controlpatterns.append(transformedpattern)   

        raw_candidates=[] 

        for ngram, n, frequency in tagged_ngrams_output:

            ngram= self._processor.filter_by_stopwords_linguistic(term= ngram)

            if ngram is None:
                continue

 #questa potrebbe diventare una funzione a parte da mettere nel processing
 #vedila          
            for pattern in processed_patterns:
                match=re.search(pattern, ngram)
                if match:
                     if match.group(0)==ngram:
                        candidate=" ".join(match.groups()[1:])
                        record=[]
                        record.append(candidate)     
                        record.append(n)
                        record.append(frequency)   
                        record.append("freq")
                        record.append(frequency)   
                        raw_candidates.append(record)
                        break

#cerca di capire cosa sta facendo esattamente questa e vedi se la puoi ottimizzare o altro           
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
        
        return data, tagged_ngrams_output
            

