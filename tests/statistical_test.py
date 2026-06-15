from TBXTools import Extractor, StatisticalMethodology

corpus = ["Mental_disorder.txt"]
regexes = [".+ health"]

methodology = StatisticalMethodology(
    nmin=2,
    nmax=3,
    exclusion_regexes=regexes,
    case_normalization=True
)

extractor = Extractor(
    methodology=methodology,
    project_name="statistical-example",
    corpus=corpus,
    language="english",
    overwrite_project=True,
)

results = extractor.extract(verbose=False)

results.nest_normalization(verbose=False)
results.regex_exclusion(verbose=False)
results.save_candidates("statistical-candidates.txt")

# Results can be inspected with the following methods:
print(f"\nTerms: {results.terms()}")
print(f"\nNgrams: {results.ngrams()}")
print(f"\nTokens: {results.tokens()}") 