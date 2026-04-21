from TBXTools import TerminologyExtractor

extractor = TerminologyExtractor()

extractor.open_project("test")

# extractor.load_corpus("Mental_disorder.txt")

# extractor.load_sl_corpus("Mental_disorder.txt")

# extractor.ngram_calculation(n_min=2,n_max=3)
for ngram in extractor.n_grams:
    print(ngram)

extractor.load_stopwords()

# print(extractor.stopwords_eng)


# extractor.load_sl_inner_stopwords("inner-stop-eng.txt")
# extractor.statistical_term_extraction()
# extractor.case_normalization(verbose=True)
# extractor.nest_normalization(verbose=True)
# extractor.load_sl_exclusion_regexps("regexps.txt")
# extractor.regexp_exclusion(verbose=True)
# extractor.save_term_candidates("candidates-stat-eng.txt")   