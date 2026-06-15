from TBXTools import Extractor, LinguisticExtractor

#patterns= ["|#|ADJ |#|NOUN"]

methodology = LinguisticExtractor(
    nmin=2,
    nmax=3,
    corpus_is_tagged=False,
    linguistic_patterns="ling_pat-ca.txt"
)

extractor = Extractor(
    methodology=methodology,
    project_name="prova",
    corpus="Trastorn_mental.txt",
    language="catalan",
    overwrite_project=True
)

results = extractor.extract(verbose=False)

results.nest_normalization(verbose=False)
results.save_candidates("test.txt")

# print(f"\nTerms: {results.terms()}")