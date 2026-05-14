from TBXTools import Extractor, StatisticalExtractor

extractor = Extractor(
    method=StatisticalExtractor(
        nmin=2,
        nmax=3),
<<<<<<< HEAD
    project_name="prove_tokenizer_8",
    corpus="Mental_disorder.txt"
=======
    project_name="test-new-5",
    corpus="Mental_health.txt",
    language="en", 
    overwrite_project=True  
>>>>>>> origin/master
)

results = extractor.extract(case_normalization=True, verbose=False)

#results.nest_normalization()
#results.regex_exclusion()
#results.save_candidates("test.txt")

print(results.tokens(limit=50))


