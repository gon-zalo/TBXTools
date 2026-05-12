from TBXTools import Extractor, StatisticalExtractor

extractor = Extractor(
    method=StatisticalExtractor(
        nmin=2,
        nmax=3),
    project_name="test-new",
    corpus="Mental_health.txt"
)

results = extractor.extract(case_normalization=True, verbose=False)

results.nest_normalization()
results.regex_exclusion()
results.save_candidates("test.txt")