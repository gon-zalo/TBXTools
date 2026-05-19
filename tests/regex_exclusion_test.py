from TBXTools import Extractor, StatisticalExtractor

corpora = ["Mental_health.txt", "Mental_disorder.txt"]
regexes = [".+ health"]

extractor = Extractor(
    method=StatisticalExtractor(nmin=2, nmax=3),
    project_name="test-example",
    corpus=corpora,
    language="english",
    exclusion_regexes=regexes,
    overwrite_project=True
)

results = extractor.extract(case_normalization=False, verbose=False)

results.regex_exclusion(verbose=True)