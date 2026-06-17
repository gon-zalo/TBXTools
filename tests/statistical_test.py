from TBXTools import Extractor, StatisticalMethodology

regexes = [".+ health"]

extractor = Extractor(
    methodology=StatisticalMethodology(
        nmin=2,
        nmax=3,
        exclusion_regexes=regexes,
        case_normalization=True
    ),
    project_name="statistical-example",
    corpus="Mental_disorder.txt",
    language="english",
    overwrite_project=True,
)

results = extractor.extract(verbose=False)

results.nest_normalization(verbose=False)
results.regex_exclusion(verbose=False)
# results.save_candidates("statistical-candidates.txt")

# Results can be inspected with the following methods:
all_terms = results.terms(limit=None)
print(f"\nNumber of terms: {len(all_terms)}. Expected number: 239")
print(f"\nTerms: {results.terms()}")
print(f"\nNgrams: {results.ngrams()}")
print(f"\nTokens: {results.tokens()}") 