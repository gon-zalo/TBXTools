from TBXTools import Extractor, LinguisticMethodology

#patterns= ["|#|ADJ |#|NOUN"]

methodology = LinguisticMethodology(
    nmin=2,
    nmax=3,
    is_corpus_tagged=True,
    evaluation_terms="evaluation_terms.txt"
)

extractor = Extractor(
    methodology=methodology,
    project_name="linguistic-example",
    corpus="tagged_corpus.txt",
    language="english",
    overwrite_project=True
)

results = extractor.extract(verbose=False)

results.nest_normalization(verbose=False)
# results.save_candidates("linguistic-candidates.txt")

print(f"\nTerms: {results.terms()}")