from TBXTools import Extractor
from TBXTools.methodology import StatisticalMethodology

regexes = [".+ health"]
tsr_terms="tsr_terms.txt"

corpus= "wikipedia-mental-health.txt"

extractor = Extractor(
    methodology=StatisticalMethodology(
        nmin=2,
        nmax=3,
        case_normalization=True
    ),
    project_name="statistical-example-tutorial",
    corpus=corpus,
    language="english",
    overwrite_project=True,
)

results = extractor.extract(verbose=False)



#results.regex_exclusion(regexes=regexes, verbose=True)
#results.nest_normalization(percent=40, verbose=True)
#results.lemmatization(verbose=False)

#results.tsr(tsr_terms=tsr_terms, type="flexible", max_iterations=10)

#results.save_candidates("statistical-candidates.txt")

# Results can be inspected with the following methods:
all_terms = [row[0] for row in results._terms]
print(f"\nNumber of terms: {len(all_terms)}. Expected number: ") 
#print(f"\nTerms:")
results.print_candidates(limit=20, n=2, verbose=True)
print(f"\nNgrams: {results.ngrams(20)}")
print(f"\nTokens: {results.tokens(20)}") 



