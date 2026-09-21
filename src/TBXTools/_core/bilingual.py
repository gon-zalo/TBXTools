from TBXTools._results.bilingual import BilingualResults
from .extractor import Extractor
from TBXTools._processor.file_parser import FileParser

class BilingualExtractor: 

    def __init__(self, project_name, src_methodology, tgt_methodology, src_language, tgt_language, parallel_corpus=None, src_stopwords=None, tgt_stopwords=None, overwrite_project=False):
        
        self.src_language = src_language
        self.tgt_language = tgt_language

        self.project_name = project_name
        self.parser = FileParser(corpus=parallel_corpus, src_lang=src_language, tgt_lang=tgt_language)
            
        self.src_extractor = Extractor(
            project_name=f"{project_name}-{src_language}",
            methodology=src_methodology,
            corpus=self.parser.src,
            stopwords=src_stopwords,
            language=src_language,
            overwrite_project=overwrite_project
        )
        
        self.tgt_extractor = Extractor(
            project_name=f"{project_name}-{tgt_language}",
            methodology=tgt_methodology,
            corpus=self.parser.tgt,
            stopwords=tgt_stopwords,
            language=tgt_language,
            overwrite_project=overwrite_project
        )
                
    def extract(self, verbose: bool = False) -> BilingualResults:
        
        src_results = self.src_extractor.extract(verbose=verbose)

        tgt_results = self.tgt_extractor.extract(verbose=verbose)

        bilingual_results = BilingualResults(
            src_results=src_results, 
            tgt_results=tgt_results,
            src_lang=self.src_language,  
            tgt_lang=self.tgt_language         
        )

        return bilingual_results
