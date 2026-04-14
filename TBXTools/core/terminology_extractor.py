# main class
from ..preprocessor import DefaultPreprocessor, CustomPreprocessor
from ..candidate_extractor import DefaultCandidateExtractor
from ..sqlite import SQLiteManager

class TerminologyExtractor:
    def __init__(self, preprocessor=None, candidate_extractor=None, scorer=None, filter_=None, case_normalization=False):
        
        self.preprocessor = preprocessor or DefaultPreprocessor()
        self.candidate_extractor = candidate_extractor or DefaultCandidateExtractor()

        # self.sqlite = SQLiteManager()
        
    def process(self, x):
        return self.preprocessor.process(x)
    
    def extract(self, x):
        return self.candidate_extractor.extract(x)
    
    def case_normalization(self, x):
        return self.preprocessor.case_normalization(x)