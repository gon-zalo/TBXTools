from TBXTools import TerminologyExtractor

extractor = TerminologyExtractor()

extractor.create_project("test")
extractor.load_corpus("Mental_health.txt")

extractor.ngram_calculation(n_min=2,n_max=3)

extractor.load_stopwords()
extractor.load_inner_stopwords()

extractor.statistical_term_extraction()
extractor.case_normalization(verbose=False) # error with casing
extractor.nest_normalization(verbose=False)
extractor.load_exclusion_regexes()
extractor.regex_exclusion()
extractor.save_candidates("candidates_test.txt")