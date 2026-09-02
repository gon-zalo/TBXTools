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
    corpus="Mental_disorder.txt",
    language="english",
    overwrite_project=True,
)

results = extractor.extract(verbose=False)

results.nest_normalization(verbose=False)
results.regex_exclusion(regexes=regexes, verbose=False)
#results.save_candidates("statistical-candidates.txt")
results.summary()

# Results can be inspected with the following methods:
all_terms = [row[0] for row in results._terms]
print(f"\nNumber of terms: {len(all_terms)}. Expected number: 223") 
results.print_candidates(limit=20)

print(f"\nNgrams: {results.ngrams()}")
print(f"\nTokens: {results.tokens()}") 

# ----------
# Scenario TSR
print("")
print("--- SCENARIO TSR ---\n")

extractor = Extractor(
    methodology=StatisticalMethodology(
        nmin=2,
        nmax=3,
        case_normalization=True
    ),
    project_name="statistical-example-tsr",
    corpus="Mental_disorder.txt",
    language="english",
    overwrite_project=True,
)

results = extractor.extract(verbose=False)

results.nest_normalization(verbose=False)
results.regex_exclusion(regexes=regexes, verbose=False)
results.tsr(tsr_terms=tsr_terms, type="flexible", max_iterations=10, verbose=False)

# Results can be inspected with the following methods:
all_terms = [row[0] for row in results._terms]
print(f"\nNumber of terms: {len(all_terms)}. Expected number: 121") 
results.print_candidates(limit=20)

print(f"\nNgrams: {results.ngrams()}")
print(f"\nTokens: {results.tokens()}") 