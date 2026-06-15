from TBXTools import Extractor, LinguisticMethodology

patterns = ["|#|NOUN |#|ADJ", "|#|NOUN |#|NOUN", "|#|ADJ |#|NOUN"]
fr_corpus = "Trouble_psychique.txt"

extractor = Extractor(
    methodology=LinguisticMethodology(nmin=2, nmax=3, is_corpus_tagged=False, linguistic_patterns=patterns),
    project_name="linguistic-example-fr",
    corpus=fr_corpus,
    language="french",
    overwrite_project=True
)

results = extractor.extract(verbose=False)

results.nest_normalization(verbose=False)
# results.save_candidates("linguistic-candidates.txt")

print(f"\nTerms: {results.terms()}")