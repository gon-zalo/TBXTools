from TBXTools import Extractor, LinguisticExtractor

#patterns= ["|#|ADJ |#|NOUN"]

methodology = LinguisticExtractor(
    nmin=2,
    nmax=3,
    corpus_is_tagged=True,
    evaluation_terms="evaluation_terms.txt"
)

extractor = Extractor(
    methodology=methodology,
    project_name="prova",
    corpus="tagged_corpus.txt",
    language="english",
    overwrite_project=True
)

results = extractor.extract(verbose=False)

results.nest_normalization(verbose=False)
results.save_candidates("test.txt")

# print(f"\nTerms: {results.terms()}")