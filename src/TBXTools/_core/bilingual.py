from TBXTools._results.bilingual import BilingualResults
from .extractor import Extractor
from TBXTools._processor.file_parser import FileParser

class BilingualExtractor: 
    
    """
    Orchestrates the bilingual terminology extraction pipeline. This class acts as the main controller, managing parallel corpus parsing and coordinating source and target term extractions through dedicated Extractor instances.
    
    Attributes:
        project_name (str): The unique name identifier for the current bilingual extraction project.
        src_language (str): The language of the source corpus.
        tgt_language (str): The language of the target corpus.
        parser (FileParser): Internal component that parses and splits the parallel corpus into source and target streams.
        src_extractor (Extractor): Extractor instance dedicated to the source language.
        tgt_extractor (Extractor): Extractor instance dedicated to the target language.
    """

    def __init__(self, project_name, src_methodology, tgt_methodology, src_language, tgt_language, parallel_corpus=None, src_stopwords=None, tgt_stopwords=None, overwrite_project=False):
        
        '''
        Initializes the BilingualExtractor by setting up the parallel corpus parser and instantiating individual source and target Extractor objects with their respective configurations.

        Args:
            project_name (str): The base name identifier for the project.
            src_methodology (object): The extraction strategy instance for the source language.
            tgt_methodology (object): The extraction strategy instance for the target language.
            src_language (str): The language of the source corpus.
            tgt_language (str): The language of the target corpus.
            parallel_corpus (str or Path): File path or corpus source for the parallel text.
            src_stopwords (list): Stopwords list for the source language.
            tgt_stopwords (list): Stopwords list for the target language.
            overwrite_project (bool, optional): If True, overwrites existing project data. Defaults to False.
        '''
        
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
        
        '''
        Coordinates the bilingual extraction pipeline by executing extraction independently on both source and target extractors and wrapping the combined outputs into a BilingualResults object.

        Args:
            verbose (bool, optional): If True, enables detailed logging. Defaults to False.

        Returns:
            BilingualResults: An instance containing both source and target extraction results.
        '''
        
        src_results = self.src_extractor.extract(verbose=verbose)

        tgt_results = self.tgt_extractor.extract(verbose=verbose)

        bilingual_results = BilingualResults(
            src_results=src_results, 
            tgt_results=tgt_results,
            src_lang=self.src_language,  
            tgt_lang=self.tgt_language         
        )

        return bilingual_results
