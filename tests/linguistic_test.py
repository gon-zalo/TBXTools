from TBXTools import Extractor, LinguisticMethodology

patterns = ["|#|NOUN |#|ADJ", "|#|NOUN |#|NOUN", "|#|ADJ |#|NOUN"]
fr_corpus = "Trouble_psychique.txt"

extractor = Extractor(
    methodology=LinguisticMethodology(nmin=2, nmax=3, is_corpus_tagged=True, linguistic_patterns="ling_pat-en.txt", tsr_terms="tsr_terms.txt"),
    project_name="english_example",
    corpus="tagged_corpus.txt",
    language="english",
    overwrite_project=True
)

results = extractor.extract(verbose=False)

results.nest_normalization(verbose=False)
# results.save_candidates("linguistic-candidates.txt")

print(f"\nTerms: {results.terms()}")
