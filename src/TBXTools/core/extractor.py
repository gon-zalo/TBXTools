from ..sqlite import SQLite
from ..results import Results
from ..resources import Resources
from ..utils import get_lang

class Extractor: #remember to add the attributes that you added while implementing the linguistic extractor
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

    def __init__(self, project_name, methodology, corpus= None, stopwords=None, inner_stopwords=None, language=None, overwrite_project=False):
        
        self.lang, self._lang_code = get_lang(language.lower())

        # initializing objects
        self._methodology = methodology
        self._resources = Resources(lang_code=self._lang_code)

        self.stopwords = stopwords or self._resources.fetch_stopwords()
        self.inner_stopwords = inner_stopwords or self._resources.fetch_inner_stopwords()

        # assigning basic attributes to Processor()
        self._methodology.processor.stopwords = self.stopwords
        self._methodology.processor.inner_stopwords = self.inner_stopwords
        self._methodology.processor.lang_code = self._lang_code

        # initializing the SQLite database
        self._sqlite = SQLite(
            project_name=project_name, 
            stopwords=self.stopwords, 
            inner_stopwords=self.inner_stopwords, 
            corpus=corpus,
            is_corpus_tagged=getattr(self._methodology,'is_corpus_tagged', False),
            exclusion_regexes=getattr(self._methodology,'exclusion_regexes', None),
            linguistic_patterns=getattr(self._methodology, 'linguistic_patterns', None),
            evaluation_terms=getattr(self._methodology,'evaluation_terms', None),
            tsr_terms=getattr(self._methodology, "tsr_terms", None),
            overwrite_project=overwrite_project,
            )

# EXTRACTION FUNCTIONS
    def extract(self, verbose=False) -> Results:
        '''
        Coordinates the extraction pipeline by fetching data from the database, calling the selected extraction methodology (linguistic or statistical), applying optional filtering/normalization procedures, and persisting the extracted candidates back to the SQLite database.

        Args:
            verbose (bool, optional): If True, enables detailed logging. Defaults to False.

        Returns:
            Results: An instance of the Results class.
        '''
        print(f"\n{self._methodology.name} initialized", flush=True)
        print("Running term extraction", flush=True)
        
        segments = self._sqlite.get_segments(is_corpus_tagged=False)

        if self._methodology.name == "LinguisticMethodology":

            self._methodology.evaluation_terms = self._sqlite.get_evaluation_terms()
            self._methodology.linguistic_patterns = self._sqlite.get_linguistic_patterns()
            tagged_segments = self._sqlite.get_segments(is_corpus_tagged=True)

            results, returned_segments = self._methodology.extract(segments=segments, tagged_segments=tagged_segments, verbose=verbose)

            self._sqlite.insert_segments(returned_segments, tagged=True)
            self._sqlite.insert_tagged_ngrams(results._tagged_ngrams)
            self._sqlite.insert_ngrams(results._ngrams)
            self._sqlite.insert_linguistic_patterns(self._methodology.linguistic_patterns)

        if self._methodology.name == "StatisticalMethodology":

            results = self._methodology.extract(segments=segments, verbose=verbose)

            self._sqlite.insert_tokens(results._tokens)
            self._sqlite.insert_ngrams(results._ngrams)

        if self._methodology.name == "BertMethodology":

            results, tokenized_corpus = self._methodology.extract(segments=segments, verbose=False)

            self._sqlite.insert_segments(data=tokenized_corpus, tagged=False, tokenized=True)
            self._sqlite.insert_tokens(data=results._tokens)

        results._extractor = self  
        results._methodology = self._methodology

        self._sqlite.delete_candidate_terms() # keep an eye on this
        self._sqlite.insert_candidate_terms(results._terms)   

        if not results._methodology.name:
            print("Error: Unknown extractor")

        return results
    
    def add_stopwords(self, stopwords_list):
        '''
        Adds standard stopwords to the project and updates the processor. Inserts the provided list of stopwords into the SQLite database and refreshes the internal processor's active stopword list.

        Args:
            stopwords_list (list[str]): A list of stopwords. 
        '''
        if isinstance(stopwords_list, list):
            self._sqlite.add_stopwords(stopwords_list=stopwords_list)
            self._methodology.processor.stopwords = self._sqlite.get_stopwords() # updating the attribute of the class
            self.stopwords = self._sqlite.get_stopwords()

    def add_inner_stopwords(self, inner_stopwords_list):
        '''
        Adds inner stopwords to the project and updates the processor. Inserts the provided list of inner stopwords into the SQLite database and refreshes the internal processor's active inner stopword list.

        Args:
            inner_stopwords_list (list[str]): A list of inner stopwords.
        '''
        if isinstance(inner_stopwords_list, list):
            self._sqlite.add_inner_stopwords(inner_stopwords_list=inner_stopwords_list)
            self._methodology.processor.inner_stopwords = self._sqlite.get_inner_stopwords()
            self.inner_stopwords = self._sqlite.get_inner_stopwords()

    def train_bert(self, trainer=None):

        trainer = trainer

        segments = self._sqlite.get_segments()

        trainer._train(train_data=segments)