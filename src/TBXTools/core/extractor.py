# main class
from ..sqlite_manager import _SQLiteManager # remove underscore from class name
from .._preprocessor import Preprocessor
from ..results import Results

from pathlib import Path

class Extractor:

    def __init__(self, project_name, method, corpus, stopwords=None, inner_stopwords=None, language=None):
        self.project_name = project_name
        self.corpus = corpus
        self.extractor = method
        self.language = language # should be implemented at some point

        self.preprocessor = Preprocessor()
        # internal sqlite class to manage everything related to the db
        self._sqlite = _SQLiteManager()

        self._ngrams = None
        self._tokens = None
        self._terms = None

        # path objects, should be implemented in the Resources class
        self._TBXTools_path = Path("../src/TBXTools")
        self._resources_path = self._TBXTools_path / "resources"
        self._stopwords_eng = self._resources_path /  "stopwords" / "stop-eng.txt"
        self._inner_stopwords_eng = self._resources_path / "inner" / "inner-stop-eng.txt"
        self._exclusion_regexes = self._resources_path / "regexes" / "regex-eng.txt"

        # all of this is automatic
        self.create_project(project_name=project_name)
        self.load_corpus(corpus_file=corpus)
        self.load_stopwords(stopwords_file=self._stopwords_eng) # add a default
        self.load_inner_stopwords(inner_stopwords_file=self._inner_stopwords_eng)

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

    def save_candidates(self, file_name): # save as csv?
        candidate_terms = self._sqlite.get_candidate_terms()
        with open(file_name, "w", encoding='utf-8') as f:
            for row in candidate_terms:
                f.write(",".join(str(element) for element in row) + "\n")

# EXTRACTION  FUNCTIONS
    def extract(self):
        print("Running term extraction")
        segments = self._sqlite.get_segments()

        # this returns a Result object
        results = self.extractor.extract(segments=segments)

        self._sqlite.insert_candidate_terms(results._terms)
        self._sqlite.insert_tokens(results._tokens)
        
        self._terms = results._terms
        self._tokens = results._tokens

        if not results._extractor_info:
            print("Error: Unknown extractor")

        if results._extractor_info == "statistical":
            self._sqlite.insert_ngrams(results._ngrams)

    def postprocess(self):
        pass
        

# ACCESSING ATTRIBUTES
    # [0] is the first element in the tuple (table row)
    def terms(self, limit=20):
        terms = [term[0] for term in self._terms]
        return terms[:limit]

    def tokens(self, limit=20):
        tokens = [token[0] for token in self._tokens]
        return tokens[:limit]



# PREPROCESSOR FUNCTIONS
    def case_normalization(self, verbose=False):

        candidate_terms = self._sqlite.get_candidate_terms()

        normalized_terms = self.preprocessor.case_normalization(candidate_terms=candidate_terms, verbose=verbose)

        self._sqlite.delete_candidate_terms()
        self._sqlite.insert_candidate_terms(normalized_terms)

    def nest_normalization(self, percent=10, verbose=False):
        # not implemented in preprocessor yet
        candidate_terms = self._sqlite.get_candidate_terms()
        for row in candidate_terms:

            candidate_term = row[0]
            candidate_term_n = row[1]
            candidate_term_freq = row[2]
            second_term_n = candidate_term_n + 1

            fmax = candidate_term_freq * percent/100 + candidate_term_freq
            fmin = candidate_term_freq * percent/100 - candidate_term_freq

            filtered_candidate_terms = self._sqlite.get_filtered_candidate_terms_by_frequency(fmax=fmax, fmin=fmin, nb=second_term_n)

            for filtered_row in filtered_candidate_terms:

                filtered_term = filtered_row[0]
                filtered_term_freq = filtered_row[2]

                if not candidate_term == filtered_term and not filtered_term.find(candidate_term)==-1: # que coño es esto
                    self._sqlite.delete_specific_candidate_term(candidate=candidate_term)

                    if verbose:
                        print(str(candidate_term_freq),candidate_term,"-->",str(filtered_term_freq),filtered_term)

        # intento de implementación de nest_norm
        # def nest_normalization_new(self, percent=10, verbose=False):
        #     candidate_terms = self._sqlite.get_candidate_terms()

        #     fmax, fmin, nb = self.preprocessor._get_frequencies(candidate_terms=candidate_terms)

        #     candidate_terms_by_freq = self._sqlite.get_candidate_terms_by_frequency(fmax=fmax, fmin=fmin, nb=nb)

        #     normalized_terms = self.preprocessor.nest_normalization(candidate_terms_by_freq=candidate_terms_by_freq, ta=ta, fa=fa)

    def regex_exclusion(self, verbose=False):
        print("Running regex exclusion")
        regexes = self._sqlite.get_exclusion_regexes()
        candidate_terms = self._sqlite.get_candidate_terms()

        candidates_to_exclude = self.preprocessor.regex_exclusion(regexes=regexes, candidate_terms=candidate_terms)

        if candidates_to_exclude:
            for candidate in candidates_to_exclude:
                self._sqlite.delete_specific_candidate_term(candidate=candidate)
                print(f"Excluded {len(candidates_to_exclude)} terms")
        else:
            print("No candidate terms excluded")

    def bert_extract(self):
        print("Running BERT extraction")
        segments = self._sqlite.get_segments()

        self.extractor.extract(segments)
