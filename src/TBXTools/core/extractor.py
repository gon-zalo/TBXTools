# main class
from ..sqlite import SQLite
from ..processor import Processor
from ..results import Results
from ..utils import get_lang
from ..resources import Resources

from pathlib import Path

class Extractor:

    def __init__(self, project_name, method, corpus, stopwords=None, inner_stopwords=None, exclusion_regexes=None, language=None, overwrite_project=False):
        # self.project_name = project_name
        # self.corpus = corpus
        self.method = method
        self.lang, self._lang_code = get_lang(language.lower())

        self._processor = Processor()
        self._resources = Resources(lang_code=self._lang_code)

        # initializing the SQLite database
        self._sqlite = SQLite(
            corpus_file=corpus, 
            project_name=project_name, 
            stopwords=stopwords or self._resources.fetch_stopwords(), 
            inner_stopwords=inner_stopwords or self._resources.fetch_inner_stopwords(), 
            exclusion_regexes=None,
            overwrite_project=overwrite_project)

        # setting the extractor stopwords here
        # this is temporary until Resources and Preprocessor class is implemented, these stopwords can also be passed in extract()
        self.method.stopwords = self._sqlite.get_stopwords() 
        self.method.inner_stopwords = self._sqlite.get_inner_stopwords()
        

# EXTRACTION FUNCTIONS
    def extract(self, case_normalization=False, regex_exclusion=False, verbose=False) -> Results:
        '''
        Function to extract terms from a segmented corpus.
        Returns a Results() object.
        '''
        print("Running term extraction")
        segments = self._sqlite.get_segments()

        # this returns a Results object
        results = self.method.extract(segments=segments, verbose=verbose)
        self._sqlite.insert_tokens(results._tokens)

        if case_normalization:

            normalized_terms = self._processor.case_normalization(candidate_terms=results._terms, verbose=verbose)
           

            results._terms = normalized_terms


        # inserting data into the database
        self._sqlite.insert_candidate_terms(results._terms)
        # passing the sqlite connection to the Results object
        results._sqlite = self._sqlite

        if not results._extractor_info:
            print("Error: Unknown extractor")

        if results._extractor_info == "statistical":
            self._sqlite.insert_ngrams(results._ngrams)

        return results

    def preprocess(self):
        pass

    # nest norm?
    def postprocess(self):
        pass

    def stopwords(self):
        return self._sqlite.get_stopwords()

    def inner_stopwords(self):
        return self._sqlite.get_inner_stopwords()
    
    def add_stopwords(self, stopwords_list):
        if isinstance(stopwords_list, list):
            self._sqlite.add_stopwords(stopwords_list=stopwords_list)

    def add_inner_stopwords(self, inner_stopwords_list):
        if isinstance(inner_stopwords_list, list):
            self._sqlite.add_inner_stopwords(inner_stopwords_list=inner_stopwords_list)