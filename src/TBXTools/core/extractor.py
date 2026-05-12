# main class
from ..sqlite import SQLite # remove underscore from class name
from ..processor import Processor
from ..results import Results

from pathlib import Path

class Extractor:

    def __init__(self, project_name, method, corpus, stopwords=None, inner_stopwords=None, language=None):
        self.project_name = project_name
        self.corpus = corpus
        self.extractor = method
        self.language = language # should be implemented at some point, can be changed to lang

        self._processor = Processor()
        self._sqlite = SQLite()

        # self._ngrams = None
        # self._tokens = None
        # self._terms = None

        # path objects, should be implemented in the Resources class
        self._TBXTools_path = Path("../src/TBXTools")
        self._resources_path = self._TBXTools_path / "resources"
        self._stopwords_eng = self._resources_path /  "stopwords" / "stop-eng.txt"
        self._inner_stopwords_eng = self._resources_path / "inner" / "inner-stop-eng.txt"
        self._exclusion_regexes = self._resources_path / "regexes" / "regex-eng.txt"

        # all of this is automatic, although they should be run in SQLiteManager()
        self.create_project(project_name=project_name) # should be implemented in SQLiteManager(), project_name can be passed as an object arg or changing the object's attribute from here
        self.load_corpus(corpus_file=corpus)
        self.load_stopwords(stopwords_file=self._stopwords_eng) # add a default
        self.load_inner_stopwords(inner_stopwords_file=self._inner_stopwords_eng)
        self.load_exclusion_regexes(exclusion_regexes_file=self._exclusion_regexes)

        self.stopwords = self._sqlite.get_stopwords() 
        self.inner_stopwords = self._sqlite.get_inner_stopwords()
        # setting the extractor stopwords here
        # this is temporary until Resources and Preprocessor class is implemented, these stopwords can also be passed in extract()
        self.extractor.stopwords = self.stopwords
        self.extractor.inner_stopwords = self.inner_stopwords
        

# SQLITE FUNCTIONS 
    # most can be removed as the user does not need to run them anymore
    def create_project(self, project_name, overwrite=False):
        self._sqlite.create_project(project_name, overwrite)

    def open_project(self, project_name):
        self._sqlite.open_project(project_name)
            
    # load functions
    def load_corpus(self, corpus_file, encoding="utf-8", compoundify=False, comp_symbol="▁"): # move to sqlitemanager and fix
        # quizás habría que preprocesarlo antes de guardarlo en sqlite
        '''Loads a monolingual corpus for the source language. It's recommended, but not compulsory, that the corpus is segmented (one segment per line). Use external tools to segment the corpus. A plain text corpus (not segmented), can be also used.'''
        self._sqlite.delete_corpus()
        # NOT IMPLEMENTED IN SQLMANAGER, porque no sé que es compoundify
        if compoundify:
            compterms=[]
            self.cur.execute('SELECT term from compoundify_terms_sl')
            data=self.cur.fetchall()
            for d in data:
                compterms.append(d[0])            

        data = []
        continserts = 0

        with open(corpus_file, "r", encoding=encoding, errors="ignore") as cf:
            for line in cf:
                line = line.rstrip()

                if compoundify:
                    for compterm in compterms:
                        if line.find(compterm)>=1:
                            comptermMOD=compterm.replace(" ",comp_symbol)
                            line=line.replace(compterm,comptermMOD)

                data.append((line,))
                continserts += 1

                if continserts == self._sqlite.maxinserts:
                    self._sqlite.insert_segments(data)
                    data = []
                    continserts = 0

        self._sqlite.insert_segments(data)

    def load_stopwords(self, stopwords_file=None):
        stopwords_file = self._stopwords_eng # temporary since we are using english only for now
        self._sqlite.load_stopwords(stopwords_file)

    def load_inner_stopwords(self, inner_stopwords_file=None):
        inner_stopwords_file = self._inner_stopwords_eng # temporary since we are using english only for now
        self._sqlite.load_inner_stopwords(inner_stopwords_file)

    def load_exclusion_regexes(self, exclusion_regexes_file=None):
        exclusion_regexes_file = self._exclusion_regexes # temporary since we are using english only for now
        self._sqlite.load_exclusion_regexes(exclusion_regexes_file=exclusion_regexes_file)

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