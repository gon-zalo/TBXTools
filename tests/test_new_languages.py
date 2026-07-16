from TBXTools import Extractor
from TBXTools.methodology import LinguisticMethodology

evaluation_terms = "evaluation_terms_spanish.txt"
linguistic_patterns="ling_pat-es.txt"
corpus = "Trastorno_mental.txt"
# ----------
# Scenario D
print("")
print("\n--- SCENARIO D ---\n")
extractor = Extractor(
    methodology=LinguisticMethodology(nmin=2, nmax=3, is_corpus_tagged=False, 
    evaluation_terms=evaluation_terms),
    project_name="linguistic-example",
    corpus=corpus,
    language="spanish",
    overwrite_project=True
)

results = extractor.extract(verbose=False)
results.nest_normalization(verbose=False)
results.lemmatization(verbose=False)
#results.tsr(tsr_terms=tsr_terms, type="strict", max_iterations=10, verbose=False)
all_terms = results.terms(limit=None)
print(f"\nNumber of terms: {len(all_terms)}. Expected number: 130")
print(f"\nTerms: {results.terms()}")
print(f"\nTagged Ngrams: {results.tagged_ngrams()}")
del extractor


