from TBXTools._results.bilingual_results import BilingualResults
from .extractor import Extractor
from pathlib import Path
from TBXTools._processor.parser import FileParser


class BilingualExtractor: 

    def __init__(self, project_name, src_methodology, tgt_methodology, src_language, tgt_language, src_corpus=None, tgt_corpus=None, parallel_corpus=None, src_stopwords=None, tgt_stopwords=None, overwrite_project=False):

        self.project_name = project_name
        self.src_language = src_language
        self.tgt_language = tgt_language
        
        if parallel_corpus:
            if isinstance(parallel_corpus, (tuple, list)) and len(parallel_corpus) == 2:
                src_corpus, tgt_corpus = parallel_corpus
            else:
                ext = Path(parallel_corpus).suffix.lower()
                if ext in [".tab", ".tsv"]:
                    src_corpus, tgt_corpus = FileParser._parse_tab(parallel_corpus)
                elif ext == ".tmx":
                    src_corpus, tgt_corpus = FileParser._parse_tmx(parallel_corpus, src_language, tgt_language)
                else:
                    raise ValueError(f"Unsupported file format: {ext}")
            
        self.src_extractor = Extractor(
            project_name=f"{project_name}-{src_language}",
            methodology=src_methodology,
            corpus=src_corpus,
            stopwords=src_stopwords,
            language=src_language,
            overwrite_project=True
        )
        
        self.tgt_extractor = Extractor(
            project_name=f"{project_name}-{tgt_language}",
            methodology=tgt_methodology,
            corpus=tgt_corpus,
            stopwords=tgt_stopwords,
            language=tgt_language,
            overwrite_project=True
        )
        
        
    def extract(self, verbose: bool = False) -> BilingualResults:
        
        src_results = self.src_extractor.extract(verbose=verbose)

        tgt_results = self.tgt_extractor.extract(verbose=verbose)

        bilingual_results = BilingualResults(
            src_results=src_results, 
            tgt_results=tgt_results
        )

        return bilingual_results
