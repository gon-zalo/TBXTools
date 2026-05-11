from TBXTools import Extractor, StatisticalExtractor

extractor = Extractor(
    method=StatisticalExtractor(nmin=2,nmax=3),
    project_name="test-new",
    corpus="Mental_health.txt"
)

results = extractor.extract(case_normalization=False)

print(results.terms())
print(results.tokens())

# extractor.nest_normalization(verbose=False)
# extractor.load_exclusion_regexes()
# extractor.regex_exclusion()
# extractor.save_candidates("candidates_test.txt")