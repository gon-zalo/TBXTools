from TBXTools import Extractor
from TBXTools.methodology import StatisticalMethodology

regexes = [".+ health"]
tsr_terms="tsr_terms"

corpus= "wikipedia-mental-health.txt"

extractor = Extractor(
    methodology=StatisticalMethodology(
        nmin=2,
        nmax=3,
        case_normalization=True
    ),
    project_name="tsr_example_1",
    corpus="Mental_disorder.txt",
    language="english",
    overwrite_project=True,
)

results = extractor.extract(verbose=False)

#results.regex_exclusion(regexes=regexes, verbose=False)
#results.nest_normalization(verbose=False)
#results.save_candidates("statistical-candidates.txt")

results.tsr(tsr_terms=tsr_terms, type="flexible", max_iterations=10)

# Results can be inspected with the following methods:
all_terms = [row[0] for row in results._terms]
#all_terms = results.terms(limit=None)
print(f"\nNumber of terms: {len(all_terms)}.") 
#print(f"\nTerms:")
results.print_candidates(limit=20)
#print(f"\nNgrams: {results.ngrams()}")
#print(f"\nTokens: {results.tokens()}") 

# ----------
# Scenario TSR for debug 
print("")
print("--- SCENARIO TSR 2 ---\n")

extractor = Extractor(
    methodology=StatisticalMethodology(
        nmin=2,
        nmax=3,
        case_normalization=True
    ),
    project_name="tsr_example_2",
    corpus=corpus,
    language="english",
    overwrite_project=True,
)

results = extractor.extract(verbose=False)

#results.nest_normalization(verbose=False)
#results.regex_exclusion(regexes=regexes, verbose=False)

terms_list= ["bipolar disorder", "mental health", "united states", "mental disorders", "new york", "mental illness", "golden rule", "mental disorder", "major depressive", "alcohol use", "nervous system", "depressive disorder", "major depression", "jacques lacan", "insanity defense", "wernicke's aphasia", "et al", "university press", "alcoholics anonymous", "depressive episodes"]

results._terms = [(term, len(term.split()), "frequency", 1) for term in terms_list] #frequency=1 just to try

results.tsr(tsr_terms=tsr_terms, type="flexible", max_iterations=10, verbose=True)

# Results can be inspected with the following methods:
all_terms = [row[0] for row in results._terms]
print(f"\nNumber of terms: {len(all_terms)}") 
#print(f"\nTerms:")
results.print_candidates(limit=20)
#print(f"\nNgrams: {results.ngrams()}")
#print(f"\nTokens: {results.tokens()}") 



