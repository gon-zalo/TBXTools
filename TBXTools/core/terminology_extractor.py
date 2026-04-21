# main class
from ..sqlite_manager import _SQLiteManager
from ..candidate_extractor import StatisticalExtractor

from pathlib import Path

class TerminologyExtractor:
    def __init__(self, sqlite=None, candidate_extractor=None):
        
        self.sqlite = _SQLiteManager()
        self.candidate_extractor = candidate_extractor or StatisticalExtractor()

        self.n_grams = None

        # path objects
        self._TBXTools_path = Path("../TBXTools")
        self._resources_path = self._TBXTools_path / "resources"
        self.stopwords_eng = self._resources_path /  "stop-eng.txt"
    
    # SQLite functions
    def create_project(self, project_name, overwrite=False):
        self.sqlite.create_project(project_name, overwrite)

    def open_project(self, project_name):
        self.sqlite.open_project(project_name)

    # load corpus func
    def load_corpus(self, corpus_file, encoding="utf-8", compoundify=False, comp_symbol="▁"):
        '''Loads a monolingual corpus for the source language. It's recommended, but not compulsory, that the corpus is segmented (one segment per line). Use external tools to segment the corpus. A plain text corpus (not segmented), can be also used.'''
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

                if continserts == self.sqlite.maxinserts:
                    self.sqlite.insert_segments(data)
                    data = []
                    continserts = 0

        self.sqlite.insert_segments(data)

    # statistical term extraction
    def ngram_calculation(self, n_min, n_max, corpus=None):
        print("Calculating n grams")

        segments = self.sqlite.get_segments()
    
        n_grams, tokens_output = self.candidate_extractor.ngram_calculation(segments, n_min, n_max)

        self.sqlite.insert_ngrams(n_grams)
        self.sqlite.insert_tokens(tokens_output)

        self.n_grams = self.candidate_extractor.n_grams

    def statistical_term_extraction(self, min_freq, corpus=None):

        print("Extracting terms")

    def load_stopwords(self, stopwords_file=None):
        stopwords_file = self.stopwords_eng
        self.sqlite.load_stopwords(stopwords_file)