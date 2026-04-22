# main class
from ..sqlite_manager import _SQLiteManager
from ..candidate_extractor import StatisticalExtractor

from pathlib import Path

class TerminologyExtractor:
    def __init__(self, candidate_extractor=None):
        
        self.candidate_extractor = candidate_extractor or StatisticalExtractor()


        # internal sqlite class to manage everything related to the db
        self._sqlite = _SQLiteManager()

            # testing stuff
        self.n_grams = None

        # path objects
        self._TBXTools_path = Path("../TBXTools")
        self._resources_path = self._TBXTools_path / "resources"
        self._stopwords_eng = self._resources_path /  "stopwords" / "stop-eng.txt"
        self._inner_stopwords_eng = self._resources_path / "inner" / "inner-stop-eng.txt"
    
    # SQLite functions
    def create_project(self, project_name, overwrite=False):
        self._sqlite.create_project(project_name, overwrite)

    def open_project(self, project_name):
        self._sqlite.open_project(project_name)
            
    # load corpus func
    def load_corpus(self, corpus_file, encoding="utf-8", compoundify=False, comp_symbol="▁"):
        '''Loads a monolingual corpus for the source language. It's recommended, but not compulsory, that the corpus is segmented (one segment per line). Use external tools to segment the corpus. A plain text corpus (not segmented), can be also used.'''
        self._sqlite.delete_corpus()
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
        stopwords_file = self._stopwords_eng
        self._sqlite.load_stopwords(stopwords_file)

    def load_inner_stopwords(self, inner_stopwords_file=None):
        inner_stopwords_file = self._inner_stopwords_eng
        self._sqlite.load_inner_stopwords(inner_stopwords_file)


    # statistical extraction
    def ngram_calculation(self, n_min, n_max, corpus=None): # make private? implement into statistical_term_extraction?
        print("Calculating n grams")
        self._sqlite.delete_ngrams()
        self._sqlite.delete_tokens()

        segments = self._sqlite.get_segments()
    
        n_grams, tokens_output = self.candidate_extractor.ngram_calculation(
            segments, 
            n_min, 
            n_max
            )

        self._sqlite.insert_ngrams(n_grams)
        self._sqlite.insert_tokens(tokens_output)

        # self.n_grams = self.candidate_extractor.n_grams

    def statistical_term_extraction(self, min_freq=2, corpus=None):
        print("Running statistical term extraction")
        self._sqlite.delete_candidate_terms()

        stopwords = self._sqlite.get_stopwords()
        inner_stopwords = self._sqlite.get_inner_stopwords()
        ngrams = self._sqlite.get_ngrams()

        candidate_terms = self.candidate_extractor.statistical_term_extraction(
            ngrams=ngrams, 
            stopwords=stopwords, 
            inner_stopwords=inner_stopwords
            )

        self._sqlite.insert_candidate_terms(candidate_terms)
        
        # self.candidate_terms = self.candidate_extractor.candidate_terms 

    def case_normalization(self, verbose=False):
        
        candidate_terms = self._sqlite.get_candidate_terms()

        auxiliar={}

        for r in candidate_terms:
            auxiliar[r[0]]=r[1]

        normalized_terms = []
        for a in candidate_terms:
            row = []
            if not a[0]==a[0].lower() and a[0].lower() in auxiliar:

                terma=a[0]
                termb=a[0].lower()
                freqa=a[1]
                freqb=auxiliar[termb]
                n=len(termb.split())
                freqtotal=freqa+freqb
                if verbose:
                    print(terma,freqa,"-->",termb,freqb,"-->",freqtotal)


                row.append(termb)
                row.append(n)
                row.append(freqtotal)
                row.append("freq")
                row.append(freqtotal)

                normalized_terms.append(row)

        self._sqlite.delete_candidate_terms()
        self._sqlite.insert_candidate_terms(normalized_terms)