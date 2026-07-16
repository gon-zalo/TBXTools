from TBXTools import Extractor
from TBXTools.methodology import StatisticalMethodology

regexes = [".+ health"]
tsr_terms="tsr_terms.txt"

extractor = Extractor(
    methodology=StatisticalMethodology(
        nmin=2,
        nmax=3,
        case_normalization=True
    ),
    project_name="statistical-example",
    corpus="corpus_derivatsUE_ca.txt",
    language="catalan",
    overwrite_project=True,
)

results = extractor.extract(verbose=False)

results.nest_normalization(verbose=False)
results.lemmatization(verbose=False)
#results.regex_exclusion(regexes=regexes, verbose=False)
#results.save_candidates("statistical-candidates.txt")

# Results can be inspected with the following methods:
all_terms = results.terms(limit=None)
print(f"\nNumber of terms: {len(all_terms)}") 
print(f"\nTerms: {results.terms()}")
print(f"\nNgrams: {results.ngrams()}")
print(f"\nTokens: {results.tokens()}") 
