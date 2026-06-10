from ..sqlite import SQLite
from ..processor import Processor
from ..results import Results
from ..utils import get_lang
from ..resources import Resources

class Extractor:

    def __init__(self, project_name, methodology, corpus, stopwords=None, inner_stopwords=None, exclusion_regexes=None, language=None, overwrite_project=False):
        self.methodology = methodology
        self.lang, self._lang_code = get_lang(language.lower())

        self._resources = Resources(lang_code=self._lang_code)

        self._processor = Processor()
        self._processor.stopwords = stopwords or self._resources.fetch_stopwords()
        self._processor.inner_stopwords = inner_stopwords or self._resources.fetch_inner_stopwords()

        self.methodology._processor = self._processor

        # initializing the SQLite database
        self._sqlite = SQLite(
            corpus=corpus, 
            project_name=project_name, 
            stopwords=stopwords or self._resources.fetch_stopwords(), 
            inner_stopwords=inner_stopwords or self._resources.fetch_inner_stopwords(), 
            exclusion_regexes=exclusion_regexes or None,
            overwrite_project=overwrite_project)

# EXTRACTION FUNCTIONS
    def extract(self, case_normalization=False, regex_exclusion=False, verbose=False) -> Results:
        '''
        Function to extract terms from a segmented corpus.
        Returns a Results() object.
        '''
        print("Running term extraction")
        segments = self._sqlite.get_segments()
        self.methodology.stop_words = self._processor.stopwords

        # this returns a Results object
        results = self.methodology.extract(segments=segments, verbose=verbose)
        self._sqlite.insert_tokens(results._tokens)

        # passing the sqlite connection and Processor()to the Results object
        results._sqlite = self._sqlite
        results._processor = self._processor
        
        if case_normalization:
            normalized_terms = self._processor.case_normalization(candidate_terms=results._terms, verbose=verbose)
           
            results._terms = normalized_terms

        # inserting data into the database
        self._sqlite.delete_candidate_terms() # keep an eye on this
        self._sqlite.insert_candidate_terms(results._terms)
        
        if not results._extractor_info:
            print("Error: Unknown extractor")

        if results._extractor_info == "statistical":
            self._sqlite.insert_ngrams(results._ngrams)

        if results._extractor_info == "bert":
            self._sqlite.insert_tokenized_segments(results._tokenized_corpus)

        return results

    def stopwords(self):
        return self._processor.stopwords
    
    def inner_stopwords(self):
        return self._processor.inner_stopwords
    
    def add_stopwords(self, stopwords_list):
        if isinstance(stopwords_list, list):
            self._sqlite.add_stopwords(stopwords_list=stopwords_list)
            self._processor.stopwords = self._sqlite.get_stopwords() # updating the attribute of the class

    def add_inner_stopwords(self, inner_stopwords_list):
        if isinstance(inner_stopwords_list, list):
            self._sqlite.add_inner_stopwords(inner_stopwords_list=inner_stopwords_list)
            self._processor.inner_stopwords = self._sqlite.get_inner_stopwords()