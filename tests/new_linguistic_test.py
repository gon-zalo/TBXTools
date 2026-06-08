from TBXTools import Extractor, LinguisticExtractor

#patterns= ["|#|ADJ |#|NOUN"]

extractor = Extractor(
    methodology=LinguisticExtractor(nmin=2, nmax=3, input_is_tagged= False, linguistic_patterns= "ling_pat-en.txt"),
    project_name="prova_patterns_5",
    corpus="Mental_disorder.txt",
    language="english",
    overwrite_project=True
)

results = extractor.extract(verbose=False)

results.nest_normalization(verbose=False)
results.save_candidates("test.txt")

print(f"\nTerms: {results.terms()}")

