from TBXTools import Extractor, LinguisticExtractor


extractor = Extractor(
    methodology=LinguisticExtractor(nmin=2, nmax=3, input_is_tagged= False, evaluation_terms= "evaluation_terms.txt"),
    project_name="prova",
    corpus="Mental_disorder.txt",
    language="english",
    overwrite_project=True
)

results = extractor.extract(case_normalization=True, verbose=False)

results.nest_normalization(verbose=False)
results.save_candidates("test.txt")
