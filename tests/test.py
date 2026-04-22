from TBXTools import TerminologyExtractor

extractor = TerminologyExtractor()

extractor.create_project("test")
extractor.load_corpus("Mental_disorder.txt")

extractor.ngram_calculation(n_min=2,n_max=3)

extractor.load_stopwords()
extractor.load_inner_stopwords()

extractor.statistical_term_extraction()
extractor.case_normalization(verbose=True) # error with casing