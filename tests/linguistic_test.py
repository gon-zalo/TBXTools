from TBXTools import Extractor, LinguisticExtractor

corpus = ["Trastorno_mental.txt"]

#linguistic_pat = ["|#|NOUN |#|NOUN"]


extractor = Extractor(
    methodology=LinguisticExtractor(nmin=2, nmax=3),
    project_name="prova_raw_corpus_spanish",
    corpus=corpus,
    language="spanish",
    linguistic_patterns= "ling_pat-es.txt",
    input_is_tagged= False,
    overwrite_project=True
)

results = extractor.extract(case_normalization=True, verbose=False)

results.nest_normalization(verbose=False)
results.regex_exclusion(verbose=False)
results.save_candidates("test.txt")

# Results can be inspected with the following methods:
#print(f"\nTerms: {results.terms()}")
print(f"\nTagged Ngrams: {results.tagged_ngrams()}") 
