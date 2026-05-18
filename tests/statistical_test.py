from TBXTools import Extractor, StatisticalExtractor

extractor = Extractor(
    method=StatisticalExtractor(
        nmin=2,
        nmax=3),
    project_name="test_no_nest",
    corpus="Mental_disorder.txt",
    language="english"
)

results = extractor.extract(case_normalization=True, verbose=False)

#results.nest_normalization()
results.regex_exclusion()
results.save_candidates("save-test.txt")

# Results can be inspected with the following methods:
print(results.terms())
print(results.ngrams())
print(results.tokens())