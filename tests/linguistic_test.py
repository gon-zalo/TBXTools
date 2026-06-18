from TBXTools import Extractor, LinguisticMethodology

evaluation_terms = "evaluation_terms.txt"
linguistic_patterns="ling_pat-en.txt"
tagged_corpus = "tagged_corpus.txt"
corpus = "Mental_disorder.txt"
tsr_terms = "tsr_terms.txt"
# Scenario A
print("--- SCENARIO A ---\n")
extractor = Extractor(
    methodology=LinguisticMethodology(nmin=2, nmax=3, is_corpus_tagged=True, linguistic_patterns=linguistic_patterns, tsr_terms=tsr_terms),
    project_name="linguistic-example",
    corpus=tagged_corpus,
    language="english",
    overwrite_project=True
)

results = extractor.extract(verbose=False)

results.nest_normalization(verbose=False)
results.tsr(type="strict", max_iterations=10, verbose=False)
all_terms = results.terms(limit=None)
print(f"\nNumber of terms: {len(all_terms)}. Expected number: 114") #questa vedi come cambiarla
print(f"\nTerms: {results.terms()}")
print(f"\nTagged Ngrams: {results.tagged_ngrams()}")
del extractor

# # ----------
# Scenario B
print("")
print("\n--- SCENARIO B ---\n")
extractor = Extractor(
    methodology=LinguisticMethodology(nmin=2, nmax=3, is_corpus_tagged=True, 
    evaluation_terms=evaluation_terms, tsr_terms=tsr_terms),
    project_name="linguistic-example",
    corpus=tagged_corpus,
    language="english",
    overwrite_project=True
)

results = extractor.extract(verbose=False)
results.nest_normalization(verbose=False)
results.tsr(type="strict", max_iterations=10, verbose=False)
all_terms = results.terms(limit=None)
print(f"\nNumber of terms: {len(all_terms)}. Expected number: 134")
print(f"\nTerms: {results.terms()}")
print(f"\nTagged Ngrams: {results.tagged_ngrams()}")
del extractor

# ----------
# Scenario C
print("")
print("\n--- SCENARIO C ---\n")
extractor = Extractor(
    methodology=LinguisticMethodology(nmin=2, nmax=3, is_corpus_tagged=False, 
    linguistic_patterns=linguistic_patterns, tsr_terms=tsr_terms),
    project_name="linguistic-example",
    corpus=corpus,
    language="english",
    overwrite_project=True
)

results = extractor.extract(verbose=False)
results.nest_normalization(verbose=False)
results.tsr(type="strict", max_iterations=10, verbose=False)
all_terms = results.terms(limit=None)
print(f"\nNumber of terms: {len(all_terms)}. Expected number: 114")
print(f"\nTerms: {results.terms()}")
print(f"\nTagged Ngrams: {results.tagged_ngrams()}")
del extractor

# ----------
# Scenario D
print("")
print("\n--- SCENARIO D ---\n")
extractor = Extractor(
    methodology=LinguisticMethodology(nmin=2, nmax=3, is_corpus_tagged=False, 
    evaluation_terms=evaluation_terms, tsr_terms=tsr_terms),
    project_name="linguistic-example",
    corpus=corpus,
    language="english",
    overwrite_project=True
)

results = extractor.extract(verbose=False)
results.nest_normalization(verbose=False)
results.tsr(type="strict", max_iterations=10, verbose=False)
all_terms = results.terms(limit=None)
print(f"\nNumber of terms: {len(all_terms)}. Expected number: 135")
print(f"\nTerms: {results.terms()}")
print(f"\nTagged Ngrams: {results.tagged_ngrams()}")
del extractor
