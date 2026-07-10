from TBXTools import Extractor, StatisticalMethodology

regexes = [".+ health"]
tsr_terms="tsr_terms.txt"
tsr_terms_lista= ["bipolar disorder", "substance use", "sleep apnea"]

extractor = Extractor(
    methodology=StatisticalMethodology(
        nmin=2,
        nmax=3,
        case_normalization=True,
    ),
    project_name="statistical-example_lower",
    corpus="Mental_disorder.txt",
    language="english",
    overwrite_project=True,
)

results = extractor.extract(verbose=False)

results.regex_exclusion(regexes=regexes, verbose=False)
results.nest_normalization(verbose=False)
results.lemmatization(verbose=False)
#results.save_candidates("statistical-candidates.txt")

# Results can be inspected with the following methods:
all_terms = results.terms(limit=None)
print(f"\nNumber of terms: {len(all_terms)}. Expected number: 239") 
print(f"\nTerms: {results.terms()}")
print(f"\nNgrams: {results.ngrams()}")
print(f"\nTokens: {results.tokens()}") 

# ----------
# Linguistic

from TBXTools import Extractor, LinguisticMethodology

evaluation_terms = "evaluation_terms.txt"
linguistic_patterns="ling_pat-en.txt"
tagged_corpus = "tagged-corpus.txt"
corpus = "Mental_disorder.txt"
tsr_terms = "tsr_terms.txt"

# Scenario A
print("--- SCENARIO A ---\n")
extractor = Extractor(
    methodology=LinguisticMethodology(nmin=2, nmax=3, is_corpus_tagged=True, linguistic_patterns=linguistic_patterns),
    project_name="linguistic-example",
    corpus=tagged_corpus,
    language="english",
    overwrite_project=True
)

results = extractor.extract(verbose=False)

results.nest_normalization(verbose=False)
results.lemmatization(verbose=False)
#results.tsr(tsr_terms=tsr_terms, type="strict", max_iterations=10, verbose=False)
all_terms = results.terms(limit=None)
print(f"\nNumber of terms: {len(all_terms)}. Expected number: 114") 
print(f"\nTerms: {results.terms()}")
print(f"\nTagged Ngrams: {results.tagged_ngrams()}")
del extractor
