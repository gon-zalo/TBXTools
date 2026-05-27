from TBXTools import Extractor, LinguisticExtractor

tagged_corpus = ["mental_ling.txt"]

#linguistic_pat = ["|#|NOUN |#|NOUN"]


extractor = Extractor(
    methodology=LinguisticExtractor(nmin=2, nmax=3),
    project_name="linguistic_provissima",
    tagged_corpus=tagged_corpus,
    language="english",
    linguistic_patterns= "ling_pat-en.txt",
    overwrite_project=True
)

results = extractor.extract(case_normalization=True, verbose=False)

results.nest_normalization(verbose=False)
results.regex_exclusion(verbose=False)
results.save_candidates("test.txt")

# Results can be inspected with the following methods:
#print(f"\nTerms: {results.terms()}")
print(f"\nTagged Ngrams: {results.tagged_ngrams()}") #attenta che questo non stampa
