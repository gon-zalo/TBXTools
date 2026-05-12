# main class
from ..sqlite import SQLite # remove underscore from class name
from ..processor import Processor
from ..results import Results

from pathlib import Path

class Extractor:

    def __init__(self, project_name, method, corpus, stopwords=None, inner_stopwords=None, language=None, overwrite_project=False):
        self.project_name = project_name
        self.corpus = corpus
        self.extractor = method
        self.language = language # should be implemented at some point, can be changed to lang

        self._processor = Processor()

        # self._ngrams = None
        # self._tokens = None
        # self._terms = None

        # path objects, should be implemented in the Resources class
        self._TBXTools_path = Path("../src/TBXTools")

        self._resources_path = self._TBXTools_path / "resources"
        self._stopwords_eng = self._resources_path /  "stopwords" / "stop-eng.txt"
        self._inner_stopwords_eng = self._resources_path / "inner" / "inner-stop-eng.txt"
        self._exclusion_regexes = self._resources_path / "regexes" / "regex-eng.txt"

        self._sqlite = SQLite(corpus_file=corpus, project_name=self.project_name, stopwords=self._stopwords_eng, inner_stopwords=self._inner_stopwords_eng, exclusion_regexes=self._exclusion_regexes, overwrite_project=overwrite_project)

        self.stopwords = self._sqlite.get_stopwords() 
        self.inner_stopwords = self._sqlite.get_inner_stopwords()
        # setting the extractor stopwords here
        # this is temporary until Resources and Preprocessor class is implemented, these stopwords can also be passed in extract()
        self.extractor.stopwords = self.stopwords
        self.extractor.inner_stopwords = self.inner_stopwords
        

# EXTRACTION FUNCTIONS
    def extract(self, case_normalization=False, regex_exclusion=False, verbose=False) -> Results:
        '''
        Function to extract terms from a segmented corpus.
        Returns a Results() object.
        '''
        print("Running term extraction")
        segments = self._sqlite.get_segments()

        # this returns a Results object
        results = self.extractor.extract(segments=segments, verbose=verbose)
        self._sqlite.insert_tokens(results._tokens)

        # print(results._terms)
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