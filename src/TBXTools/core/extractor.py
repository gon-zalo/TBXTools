from ..sqlite import SQLite
from ..processor import Processor
from ..results import Results
from ..methodology.tagger import LinguisticTagger
from ..utils import get_lang
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

    def __init__(self, project_name, methodology, corpus= None, tagged_corpus= None, stopwords=None, inner_stopwords=None, exclusion_regexes=None, linguistic_patterns=None, language=None, input_is_tagged=False, overwrite_project=False):
        self.methodology = methodology
        self.lang, self._lang_code = get_lang(language.lower())

        self._resources = Resources(lang_code=self._lang_code)

        self._processor = Processor()
        self._processor.stopwords = stopwords or self._resources.fetch_stopwords()
        self._processor.inner_stopwords = inner_stopwords or self._resources.fetch_inner_stopwords()

        #the following lines could be helpful for when you want to implement the possibility to choose between models
        #so far es_core.. is the default model
        #if spacy_model is None:
            #spacy_model= SPACY_MODELS.get(self._lang_code, "en_core_web_sm")

        self._tagger = LinguisticTagger()

        self.methodology._processor = self._processor

        is_ling = (methodology.extractor_info == "linguistic") #checks if the methodology used is the linguistic
        input_data = tagged_corpus if tagged_corpus is not None else corpus
    
        # initializing the SQLite database
        self._sqlite = SQLite(
            project_name=project_name, 
            stopwords=stopwords or self._resources.fetch_stopwords(), 
            inner_stopwords=inner_stopwords or self._resources.fetch_inner_stopwords(), 
            corpus= None if (is_ling and input_is_tagged) else input_data, #corpus with both methodology- always wuth statistical vs linguistic- only if input_is_tagged= None
            tagged_corpus=input_data if (is_ling and input_is_tagged) else None , #tagged corpus only if input_is_tagged= True and linguistic methodology
            exclusion_regexes=exclusion_regexes or None,
            linguistic_patterns=linguistic_patterns or None,
            overwrite_project=overwrite_project)

# EXTRACTION FUNCTIONS
    def extract(self, case_normalization=False, regex_exclusion=False, verbose=False) -> Results:
        '''
        Coordinates the extraction pipeline by fetching data from the database,
        calling the selected extraction methodology (linguistic or statistical),
        applying optional filtering/normalization procedures, and persisting 
        the extracted candidates back to the SQLite database.

        Args:
            case_normalization (bool, optional): If True, applies case normalization. Defaults to False.
            regex_exclusion (bool, optional): If True, filters out candidate terms matching specific regular expressions. Defaults to False.
            verbose (bool, optional): If True, enables detailed logging. Defaults to False.

        Returns:
            Results: An instance of the Results class.
        '''
        print("Running term extraction")

        extractor_type = self.methodology.extractor_info

        if extractor_type == "linguistic": 
            tagged_segments = self._sqlite.get_tagged_segments() #we check if there is a corpus in the database´s table "tagged_corpus"
        
        #the idea is to make the following part more pythonic and synthetic since we are in the extractor
        #but for now it works
            if not tagged_segments: #if tagged corpus table is empty- we proceed as follows
                print("Corpus is not tagged. Starting POS tagging process")

                segments = self._sqlite.get_segments() #we extract the segments from the table corpus- that contains the raw corpus

                all_tagged_segments = []
                db_data_to_insert = []

                for segment in segments:
                    single_tagged_segment= self._tagger.tag_segment(segment) #we pos tag every segment in the raw corpus

                    if single_tagged_segment:
                        all_tagged_segments.append(single_tagged_segment)
                    
                        db_data_to_insert.append((single_tagged_segment,))
                
                if db_data_to_insert: #we insert the new tagged corpus in the tagged corpus table
                    self._sqlite.insert_tagged_segments(db_data_to_insert)
                
                tagged_segments= all_tagged_segments
            #from here the linguistic extraction is the same
            linguistic_patterns = self._sqlite.get_linguistic_pattern() 

            results = self.methodology.ling_extract(
                tagged_segments=tagged_segments,
                linguistic_patterns=linguistic_patterns
            )

        else:
            segments = self._sqlite.get_segments()
            results = self.methodology.extract(segments=segments, verbose=verbose)

        #now the case_normalization is into the else block- in this way it works only when we perform a statistical extraction
        #note that when you run linguistic extraction- "Apllying case_normalization" doesn't appear
        #this is a temporary solution- discuss!

            if case_normalization:
                normalized_terms = self._processor.case_normalization(candidate_terms=results._terms, verbose=verbose)
           
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
        
        elif results._extractor_info == "linguistic":
            self._sqlite.insert_tagged_ngrams(results._tagged_ngrams)

        return results

    def preprocess(self):
        pass

    # nest norm?
    def postprocess(self):
        pass

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

    #maybe you'll need to use this for the spacy models
    def add_spacy_models(self):
        pass
    

            