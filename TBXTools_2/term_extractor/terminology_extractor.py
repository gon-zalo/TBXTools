from core import Improvements, StatisticalExtractor

class TerminologyExtractor:
    def __init__(self):
        self.extractor= StatisticalExtractor()
        self.sqlmanager= self.extractor.sqlmanager
        self.improvements= Improvements(self.sqlmanager)

    def load_corpus(self, corpus):
        self.sqlmanager.load_corpus(corpus)

    def load_stopwords(self, archivo):
        self.sqlmanager.load_stopwords(archivo)

    def load_inner_stopwords(self, archivo):
        self.sqlmanager.load_inner_stopwords(archivo)

    def create_project(self, projectname, overwrite=True):
        self.sqlmanager.create_project(projectname, overwrite=overwrite)

    def merge_term_frequencies(self, verbose=False):
        self.improvements.merge_term_frequencies()

    def load_exclusion_regex(self, archivo):
        self.sqlmanager.load_exclusion_regexps(archivo)

        

    def regex_exclusion(self, verbose=False):
        self.improvements.regex_exclusion()

    def nest_normalization(self,percent=10,verbose=False):
        self.improvements.nest_normalization()

    def save_term_candidate_archivo(self, outputfile, encoding="utf-8"):
        self.sqlmanager.save_term_candidate_archivo(outputfile)





    def ngram_calculation(self, nmin, nmax, minfreq=2):
        print("Running ngram calculation")

        self.extractor.ngram_calculation(nmin, nmax, minfreq)

    # 1. INPUT (DB)
        #segments = self.sqlmanager.get_segments()

    # 2. LOGIC
        #ngram_data, token_data = self.extractor.ngram_calculation(
        #nmin,
        #nmax,
        #minfreq
        #)

    # 3. OUTPUT (DB)
        #self.sqlmanager.insert_ngrams(ngram_data)
        #self.sqlmanager.insert_tokens(token_data)

    def statistical_term_extraction(self,minfreq=2):
        print("Running statistical term extraction")

        self.extractor.statistical_term_extraction(minfreq)


        #self.sqlmanager.delete_term_candidates()

        #stopwords=self.sqlmanager.get_stopwords()
                
        #inner_stopwords= self.sqlmanager.get_inner_stopwords()
        
        #ngrammi= self.sqlmanager.get_candidate_terms_ngrams()

        #data= self.extractor.statistical_term_extraction(
        #stopwords=stopwords,
        #inner_stopwords=inner_stopwords,
        #ngrammi= ngrammi,
        #minfreq=minfreq
        #)

        #self.sqlmanager.insert_candidate_terms(data)   









