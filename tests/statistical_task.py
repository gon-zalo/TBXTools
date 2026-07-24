from TBXTools import Extractor
from TBXTools.methodology import StatisticalMethodology

corpus_pl_eng = "sample-mechanical-engineering-pl.txt"
corpus_en_eng = "sample-mechanical-engineering-en.txt"
corpus_pl_med = "sample-medicine-pl.txt"
corpus_en_med = "sample-medicine-en.txt"


print("\n--- ENGLISH ENGINEERING ---\n")

extractor = Extractor(
    methodology=StatisticalMethodology(
        nmin=1,
        nmax=4,
        case_normalization=True
    ),
    project_name="statistical-example_task_en_eng",
    corpus=corpus_en_eng,
    language="english",
    overwrite_project=True,
)

results = extractor.extract(verbose=False)

results.nest_normalization(verbose=False)
results.save_candidates("wmt-stat_extraction-engitech-en.csv")
#results.regex_exclusion(regexes=regexes, verbose=False)
#results.save_candidates("statistical-candidates.txt")

# Results can be inspected with the following methods:
all_terms = results.terms(limit=None)
print(f"\nNumber of terms: {len(all_terms)}.") 
print(f"\nTerms: {results.terms()}")
print(f"\nNgrams: {results.ngrams()}")
print(f"\nTokens: {results.tokens()}") 

# # ----------

print("\n--- POLISH ENGINEERING ---\n")

extractor = Extractor(
    methodology=StatisticalMethodology(
        nmin=1,
        nmax=4,
        case_normalization=True
    ),
    project_name="statistical-example_task_pl_eng",
    corpus=corpus_pl_eng,
    language="polish",
    overwrite_project=True,
)

results = extractor.extract(verbose=False)

results.nest_normalization(verbose=False)
results.save_candidates("wmt-stat_extraction-engitech-pl.csv")
#results.regex_exclusion(regexes=regexes, verbose=False)
#results.save_candidates("statistical-candidates.txt")

# Results can be inspected with the following methods:
all_terms = results.terms(limit=None)
print(f"\nNumber of terms: {len(all_terms)}.") 
print(f"\nTerms: {results.terms()}")
print(f"\nNgrams: {results.ngrams()}")
print(f"\nTokens: {results.tokens()}") 


# # ----------

print("\n--- ENGLISH MEDICINE ---\n")

extractor = Extractor(
    methodology=StatisticalMethodology(
        nmin=1,
        nmax=4,
        case_normalization=True
    ),
    project_name="statistical-example_task_en_med",
    corpus=corpus_en_med,
    language="english",
    overwrite_project=True,
)

results = extractor.extract(verbose=False)

results.nest_normalization(verbose=False)
results.save_candidates("wmt-stat_extraction-medicine-en.csv")
#results.regex_exclusion(regexes=regexes, verbose=False)
#results.save_candidates("statistical-candidates.txt")

# Results can be inspected with the following methods:
all_terms = results.terms(limit=None)
print(f"\nNumber of terms: {len(all_terms)}.") 
print(f"\nTerms: {results.terms()}")
print(f"\nNgrams: {results.ngrams()}")
print(f"\nTokens: {results.tokens()}") 

# # ----------

print("\n--- POLISH MEDICINE ---\n")

extractor = Extractor(
    methodology=StatisticalMethodology(
        nmin=1,
        nmax=4,
        case_normalization=True
    ),
    project_name="statistical-example_task_pl_med",
    corpus=corpus_pl_med,
    language="polish",
    overwrite_project=True,
)

results = extractor.extract(verbose=False)

results.nest_normalization(verbose=False)
results.save_candidates("wmt-stat_extraction-medicine-pl.csv")
#results.regex_exclusion(regexes=regexes, verbose=False)


# Results can be inspected with the following methods:
all_terms = results.terms(limit=None)
print(f"\nNumber of terms: {len(all_terms)}.") 
print(f"\nTerms: {results.terms()}")
print(f"\nNgrams: {results.ngrams()}")
print(f"\nTokens: {results.tokens()}") 
del extractor


