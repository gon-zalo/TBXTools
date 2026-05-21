from .base import BaseExtractor
from ..processor import Processor 
from ..results import Results

class LinguisticExtractor(BaseExtractor):

    def __init__(self):

        self.extractor_info = "linguistic"
        self._processor= Processor()
        pass

    # MAIN FUNCTION

    def ling_extract(self): #guarda come è costruito tutto in statistical.py
        return Results()
        pass


    def linguistic_term_extraction(self,minfreq=2):
        '''Performs an linguistic term extraction using the extracted tagged ngrams (tagged_ngram_calculation should be executed first). '''
        #qui dentro deve starci pure tagged_ngram_calculation- nello stesso modo in cui hai unificato ngram e statistical in statistical.py
        pass



