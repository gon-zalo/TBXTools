from TBXTools._results.bilingual_results import BilingualResults
from .extractor import Extractor

class BilingualExtractor:

    def __init__(self, project_name, src_methodology, tgt_methodology, src_language, tgt_language, src_corpus=None, tgt_corpus=None, parallel_corpus=None, src_stopwords=None, tgt_stopwords=None, overwrite_project=False):

        self.project_name = project_name
        self.src_language = src_language
        self.tgt_language = tgt_language

        if parallel_corpus:
            src_corpus = parallel_corpus
            tgt_corpus = parallel_corpus
            
        self.src_extractor = Extractor(
            project_name=f"{project_name}-{src_language}",
            methodology=src_methodology,
            corpus=src_corpus,
            stopwords=src_stopwords,
            language=src_language,
            role = "source",
            overwrite_project=True
        )

        self.tgt_extractor = Extractor(
            project_name=f"{project_name}-{tgt_language}",
            methodology=tgt_methodology,
            corpus=tgt_corpus,
            stopwords=tgt_stopwords,
            language=tgt_language,
            role="target",
            overwrite_project=True
        )
        
        self.src_extractor._sqlite.src_language = src_language
        self.tgt_extractor._sqlite.src_language = src_language
        
        
    def extract(self, verbose: bool = False) -> BilingualResults:
        
        src_results = self.src_extractor.extract(verbose=verbose)

        tgt_results = self.tgt_extractor.extract(verbose=verbose)

        bilingual_results = BilingualResults(
            src_results=src_results, 
            tgt_results=tgt_results
        )

        return bilingual_results
