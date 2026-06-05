from TBXTools import Extractor, LinguisticExtractor


extractor = Extractor(
    methodology=LinguisticExtractor(nmin=2, nmax=3, input_is_tagged= True, linguistic_patterns= "ling_pat-en.txt"),
    project_name="prova_argomenti_diversi_tagged_e_patterns",
    corpus="mental_ling.txt",
    language="english",
    overwrite_project=True
)

results = extractor.extract(case_normalization=False, verbose=False)

results.nest_normalization(verbose=False)
results.regex_exclusion(verbose=False)
results.save_candidates("test.txt")

# Results can be inspected with the following methods:
#print(f"\nTerms: {results.terms()}")
#print(f"\nTagged Ngrams: {results.tagged_ngrams()}") 