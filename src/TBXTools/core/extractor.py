from ..sqlite import SQLite
from ..processor import Processor
from ..results import Results
from ..methodology.linguistic.tagger import LinguisticTagger
from ..utils import get_lang, get_model_from_code
from ..resources import Resources

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
        _processor (Processor): Internal component to handle text preprocessing tasks.
    """

    def __init__(self, project_name, methodology, corpus= None, stopwords=None, inner_stopwords=None, language=None, overwrite_project=False):
        
        self.methodology = methodology
        self.lang, self._lang_code = get_lang(language.lower())
        self._resources = Resources(lang_code=self._lang_code)

        case_normalization = False
        exclusion_regexes = None
        corpus_is_tagged = False
        linguistic_patterns = None
        evaluation_terms = None
        final_corpus = None
        final_tagged_corpus = None
  
        if methodology.extractor_info == "statistical":
            case_normalization= methodology.case_normalization
            exclusion_regexes= methodology.exclusion_regexes
            final_corpus = corpus

        if methodology.extractor_info == "linguistic":
            corpus_is_tagged = methodology.corpus_is_tagged 
            linguistic_patterns = methodology.linguistic_patterns 
            evaluation_terms = methodology.evaluation_terms
            if corpus_is_tagged:
                final_tagged_corpus = corpus
            else:
                final_corpus = corpus

        self._processor = Processor()
        self._processor.stopwords = stopwords or self._resources.fetch_stopwords()
        self._processor.inner_stopwords = inner_stopwords or self._resources.fetch_inner_stopwords()
        self._processor.case_normalization= case_normalization
        self._processor._lang_code = self._lang_code
        self.methodology._processor = self._processor
        self._processor.nmin= self.methodology.nmin
        self._processor.nmax = self.methodology.nmax
    
        # initializing the SQLite database
        self._sqlite = SQLite(
            project_name=project_name, 
            stopwords=stopwords or self._resources.fetch_stopwords(), 
            inner_stopwords=inner_stopwords or self._resources.fetch_inner_stopwords(), 
            corpus= final_corpus, 
            tagged_corpus = final_tagged_corpus ,
            exclusion_regexes=exclusion_regexes or None,
            linguistic_patterns=linguistic_patterns or None,
            evaluation_terms=evaluation_terms or None,
            overwrite_project=overwrite_project,
            )

# EXTRACTION FUNCTIONS
    def extract(self, verbose=False) -> Results:
        '''
        Coordinates the extraction pipeline by fetching data from the database,
        calling the selected extraction methodology (linguistic or statistical),
        applying optional filtering/normalization procedures, and persisting 
        the extracted candidates back to the SQLite database.

        Args:
            case_normalization (bool, optional): If True, applies case normalization. Defaults to False.
            verbose (bool, optional): If True, enables detailed logging. Defaults to False.

        Returns:
            Results: An instance of the Results class.
        '''
        print("Running term extraction")
        
        #Determine the extraction strategy
        extractor_type = self.methodology.extractor_info
        segments = self._sqlite.get_segments()
        self.methodology.stop_words = self._processor.stopwords

        if extractor_type == "linguistic": 

            self.methodology._processor = self._processor
            self.methodology._processor.nmin = self.methodology.nmin
            self.methodology._processor.nmax = self.methodology.nmax
            
            tagged_segments = self._sqlite.get_tagged_segments()
            tagged_segments = [(x,) for x in tagged_segments] #this to pass from a list of strings to a list of tuples
            
            if not tagged_segments:
                tagged_segments= self._processor.create_tagged_segments(segments=segments)
                self._sqlite.insert_tagged_segments(tagged_segments)

            tagged_ngrams= self._processor.ngrams_calculation(segments=tagged_segments, corpus_is_tagged=True)        
            
            self._sqlite.insert_tagged_ngrams(tagged_ngrams)
            
            existing_patterns= self._sqlite.get_linguistic_patterns()
            if existing_patterns:
                self.methodology.linguistic_patterns= existing_patterns    
            else:                
                self.methodology.linguistic_patterns = None

            evaluation_terms = self._sqlite.get_evaluation_terms()
            self.methodology.evaluation_terms = evaluation_terms

            filtered_tagged_ngrams = []
            for term in evaluation_terms:
                filtered_ngram = self._sqlite.get_tagged_ngrams(ngram_filter=term)
                filtered_tagged_ngrams.append(filtered_ngram)

            results = self.methodology.extract(tagged_segments=tagged_segments, tagged_ngrams=tagged_ngrams, filtered_tagged_ngrams=filtered_tagged_ngrams)
            
            if not existing_patterns and self.methodology.linguistic_patterns:
                self._sqlite.delete_linguistic_patterns()
                self._sqlite.load_linguistic_patterns(self.methodology.linguistic_patterns)

        if extractor_type == "statistical": 
            results = self.methodology.extract(segments=segments, verbose=verbose)

            if self._processor.case_normalization:
                normalized_terms = self._processor.apply_case_normalization(candidate_terms=results._terms, verbose=verbose)  
                results._terms = normalized_terms

            self._sqlite.insert_tokens(results._tokens)

        # passing the sqlite connection and Processor()to the Results object
        results._sqlite = self._sqlite
        results._processor = self._processor    

        # inserting data into the database
        self._sqlite.delete_candidate_terms() # keep an eye on this
        self._sqlite.insert_candidate_terms(results._terms)   

        if not results._extractor_info:
            print("Error: Unknown extractor")

        if results._extractor_info == "statistical":
            self._sqlite.insert_ngrams(results._ngrams)
        
        return results

    def stopwords(self):
        return self._processor.stopwords
    
    def inner_stopwords(self):
        return self._processor.inner_stopwords
    
    def add_stopwords(self, stopwords_list):
        '''
        Adds standard stopwords to the project and updates the processor. Inserts the provided list of stopwords into the SQLite database and refreshes the internal processor's active stopword list.

        Args:
            stopwords_list (list[str]): A list of stopwords. 
        '''
        if isinstance(stopwords_list, list):
            self._sqlite.add_stopwords(stopwords_list=stopwords_list)
            self._processor.stopwords = self._sqlite.get_stopwords() # updating the attribute of the class

    def add_inner_stopwords(self, inner_stopwords_list):
        '''
        Adds inner stopwords to the project and updates the processor. Inserts the provided list of inner stopwords into the SQLite database and refreshes the internal processor's active inner stopword list.

        Args:
            inner_stopwords_list (list[str]): A list of inner stopwords.
        '''
        if isinstance(inner_stopwords_list, list):
            self._sqlite.add_inner_stopwords(inner_stopwords_list=inner_stopwords_list)
            self._processor.inner_stopwords = self._sqlite.get_inner_stopwords()