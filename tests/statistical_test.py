from TBXTools import Extractor, StatisticalExtractor

corpus = ["Mental_health.txt"]

extractor = Extractor(
    methodology=StatisticalExtractor(nmin=2, nmax=3),
    project_name="test-example",
    corpus=corpus,
    language="english",
    overwrite_project=True
)

results = extractor.extract(case_normalization=True, verbose=False)

results.nest_normalization(verbose=True)
results.regex_exclusion(verbose=False)
results.save_candidates("save-test.txt")

# Results can be inspected with the following methods:
print(f"\nTerms: {results.terms()}")
print(f"\nNgrams: {results.ngrams()}")
print(f"\nTokens: {results.tokens()}")