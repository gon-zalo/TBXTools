from TBXTools import Extractor, LinguisticMethodology

evaluation_terms = "evaluation_terms.txt"
linguistic_patterns="ling_pat-en.txt"
learned_linguistic_patterns= "learned_linguistic_patterns.txt"
tagged_corpus = "tagged_corpus.txt"
corpus = "Mental_disorder.txt"
tsr_terms = "tsr_terms.txt"
corpus_es = "Trastorno_mental.txt"

print("\n--- SCENARIO C ---\n")
extractor = Extractor(
    methodology=LinguisticMethodology(nmin=2, nmax=3, is_corpus_tagged=False, 
    linguistic_patterns=learned_linguistic_patterns),
    project_name="linguistic-example_spanish",
    corpus=corpus_es,
    language="spanish",
    overwrite_project=True
)

results = extractor.extract(verbose=False)
results.nest_normalization(verbose=False)
#results.tsr(type="strict", max_iterations=10, verbose=False)
all_terms = results.terms(limit=None)
print(f"\nNumber of terms: {len(all_terms)}. Expected number: 114")
print(f"\nTerms: {results.terms()}")
print(f"\nTagged Ngrams: {results.tagged_ngrams()}")
del extractor
