from .._sqlite.sqlite import SQLite
from .._results.results import Results
from .._resources.resources import Resources
from .._utils.utils import get_lang

class Extractor:
    """
    Orchestrates the terminology extraction pipeline.

    This class acts as the main controller, managing the integration between the chosen extraction methodology, database storage, and text preprocessing components.

    Attributes:
        methodology (object): The extraction strategy instance (e.g., LinguisticExtractor or StatisticalExtractor).
        project_name (str): The unique name identifier for the current extraction project, which also determines the filename of the generated SQLite database.
        tagged_corpus: The tagged corpus used as the source for terminology extraction (in the case of linguistic extraction).
        corpus: The text corpus used as the source for terminology extraction (in the case of statistical extraction).
        language (str): The language of the corpus text (e.g., "english").
        linguistic_patterns (str, optional): File path to the POS patterns (used only for linguistic extraction).
        overwrite_project (bool): If True, overwrites existing project data in the database.
        _sqlite (SQLiteManager): Internal component to manage database interactions.
    """

    def __init__(self, project_name, methodology, corpus=None, stopwords=None, inner_stopwords=None, language=None, overwrite_project=False):
        
        self.lang, self._lang_code = get_lang(language.lower())
        self._methodology = methodology
        self._sqlite = SQLite(
            project_name=project_name, 
            stopwords=stopwords, 
            inner_stopwords=inner_stopwords, 
            corpus=corpus,
            is_corpus_tagged=getattr(self._methodology,'is_corpus_tagged', False),
            exclusion_regexes=getattr(self._methodology,'exclusion_regexes', None),
            linguistic_patterns=getattr(self._methodology, 'linguistic_patterns', None),
            evaluation_terms=getattr(self._methodology,'evaluation_terms', None),
            tsr_terms=getattr(self._methodology, "tsr_terms", None),
            overwrite_project=overwrite_project,
            lang_code=self._lang_code,
            lang=self.lang
            )
        
        self.stopwords = self._sqlite.get("stopwords")
        self.inner_stopwords = self._sqlite.get("inner_stopwords")

        self._methodology.processor.stopwords = self._sqlite.get("stopwords")
        self._methodology.processor.inner_stopwords = self._sqlite.get("inner_stopwords")
        self._methodology.processor.lang_code = self._lang_code

# EXTRACTION FUNCTIONS
    def extract(self, verbose=False) -> Results:
        '''
        Coordinates the extraction pipeline by fetching data from the database, calling the selected extraction methodology (linguistic or statistical), applying optional filtering/normalization procedures, and persisting the extracted candidates back to the SQLite database.

        Args:
            verbose (bool, optional): If True, enables detailed logging. Defaults to False.

        Returns:
            Results: An instance of the Results class.
        '''
        
        self._methodology.extractor = self

        if self._sqlite.overwrite_project == False and self._sqlite.table_is_populated("candidate_terms"): # if we are not overwriting and the calculations have been done
            print("Fetching data from database", flush=True)
            candidate_terms = self._sqlite.get_candidate_terms()
            ngrams = self._sqlite.get_ngrams()
            tokens = self._sqlite.get("tokens")
            tagged_ngrams = self._sqlite.get_ngrams(tagged=True)
            linguistic_patterns = self._sqlite.get("linguistic_patterns")

            results = Results(
                terms=candidate_terms, 
                ngrams=ngrams if ngrams else None, 
                tokens=tokens, 
                tagged_ngrams=tagged_ngrams if tagged_ngrams else None,
                linguistic_patterns=linguistic_patterns if linguistic_patterns else None
                )

        else:
            print(f"\n{self._methodology.name} initialized", flush=True)
            print("Running term extraction", flush=True)

            segments = list(self._sqlite.get_segments(tagged=False))

            results = self._methodology.run(segments=segments, verbose=verbose)

            self._sqlite.insert_candidate_terms(results._terms)   

        results._extractor = self  
        results._methodology = self._methodology
        
        return results
    
    def add_stopwords(self, stopwords_list):
        '''
        Adds standard stopwords to the project and updates the processor. Inserts the provided list of stopwords into the SQLite database and refreshes the internal processor's active stopword list.

        Args:
            stopwords_list (list[str]): A list of stopwords. 
        '''
        if isinstance(stopwords_list, list):
            self._sqlite.add_stopwords(stopwords_list=stopwords_list)
            self._methodology.processor.stopwords = self._sqlite.get("stopwords") # updating the attribute of the class
            self.stopwords = self._sqlite.get("stopwords")

            print("Additional stopwords added")

    def add_inner_stopwords(self, inner_stopwords_list):
        '''
        Adds inner stopwords to the project and updates the processor. Inserts the provided list of inner stopwords into the SQLite database and refreshes the internal processor's active inner stopword list.

        Args:
            inner_stopwords_list (list[str]): A list of inner stopwords.
        '''
        if isinstance(inner_stopwords_list, list):
            self._sqlite.add_inner_stopwords(inner_stopwords_list=inner_stopwords_list)
            self._methodology.processor.inner_stopwords = self._sqlite.get("inner_stopwords")
            self.inner_stopwords = self._sqlite.get("inner_stopwords")