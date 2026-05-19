from TBXTools import Extractor, StatisticalExtractor

corpora = ["Mental_health.txt", "Mental_disorder.txt"]

extractor = Extractor(
    method=StatisticalExtractor(nmin=2, nmax=3),
    project_name="test-example",
    corpus=corpora,
    language="english"
)

results = extractor.extract(case_normalization=True, verbose=False)

results.nest_normalization()
results.regex_exclusion()
results.save_candidates("save-test.txt")

# Results can be inspected with the following methods:
print(f"\nTerms: {results.terms()}")
print(f"\nNgrams: {results.ngrams()}")
print(f"\nTokens: {results.tokens()}")