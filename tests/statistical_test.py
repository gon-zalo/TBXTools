from TBXTools import Extractor, StatisticalExtractor

extractor = Extractor(
    method=StatisticalExtractor(
        nmin=2,
        nmax=3),
    project_name="prove_tokenizer_8",
    corpus="Mental_disorder.txt"
)

results = extractor.extract(case_normalization=True, verbose=False)

#results.nest_normalization()
#results.regex_exclusion()
#results.save_candidates("test.txt")

print(results.tokens(limit=50))


