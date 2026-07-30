from TBXTools import Extractor
from TBXTools.methodology import LinguisticMethodology

evaluation_terms_en_eng = "terms-engitech-en.txt"
evaluation_terms_pl_eng = "terms-engitech-pl.txt"
evaluation_terms_en_med = "terms-medicine-en.txt"
evaluation_terms_pl_med = "terms-medicine-pl.txt"

corpus_pl_eng = "sample-mechanical-engineering-pl.txt"
corpus_en_eng = "sample-mechanical-engineering-en.txt"
corpus_pl_med = "sample-medicine-pl.txt"
corpus_en_med = "sample-medicine-en.txt"

corpus_grande_pl_med = "medicine-d2-pl.txt"
corpus_grande_pl_eng = "engitech-d2-pl.txt"
corpus_grande_en_eng = "engitech-d2-en.txt"
corpus_grande_en_med = "medicine-d2-en.txt"



print("\n--- ENGLISH ENGINEERING ---\n")
extractor = Extractor(
    methodology=LinguisticMethodology(nmin=1, nmax=4, is_corpus_tagged=False, evaluation_terms=evaluation_terms_en_eng),
    project_name="linguistic-example_task_en_eng_big",
    corpus=corpus_grande_en_eng,
    language="english",
    overwrite_project=True
)

results = extractor.extract(verbose=False)
results.nest_normalization(verbose=False)
results.save_candidates("wmt-ling_extraction-engitech-terms-en_grande.csv")

all_terms = results.terms(limit=None)
print(f"\nNumber of terms: {len(all_terms)}")
print(f"\nTerms: {results.terms()}")
print(f"\nTagged Ngrams: {results.tagged_ngrams()}")
del extractor

# # ----------

print("\n--- POLISH ENGINEERING ---\n")
extractor = Extractor(
    methodology=LinguisticMethodology(nmin=1, nmax=4, is_corpus_tagged=False, 
    evaluation_terms=evaluation_terms_pl_eng),
    project_name="linguistic-example_task_pl_eng_big",
    corpus=corpus_grande_pl_eng,
    language="polish",
    overwrite_project=True
)

results = extractor.extract(verbose=False)
results.nest_normalization(verbose=False)
results.save_candidates("wmt-ling_extraction-engitech-terms-pl_grande.csv")

all_terms = results.terms(limit=None)
print(f"\nNumber of terms: {len(all_terms)}")
print(f"\nTerms: {results.terms()}")
print(f"\nTagged Ngrams: {results.tagged_ngrams()}")
del extractor

# # ----------

print("\n--- ENGLISH MEDICINE ---\n")
extractor = Extractor(
    methodology=LinguisticMethodology(nmin=1, nmax=4, is_corpus_tagged=False, 
    evaluation_terms=evaluation_terms_en_med),
    project_name="linguistic-example_task_en_med_big",
    corpus=corpus_en_med,
    language="english",
    overwrite_project=True
)

results = extractor.extract(verbose=False)
results.nest_normalization(verbose=False)
results.save_candidates("wmt-ling_extraction-medicine-terms-en_grande.csv")

all_terms = results.terms(limit=None)
print(f"\nNumber of terms: {len(all_terms)}")
print(f"\nTerms: {results.terms()}")
print(f"\nTagged Ngrams: {results.tagged_ngrams()}")
del extractor

# # ----------

print("\n--- POLISH MEDICINE ---\n")
extractor = Extractor(
    methodology=LinguisticMethodology(nmin=1, nmax=4, is_corpus_tagged=False, 
    evaluation_terms=evaluation_terms_pl_med),
    project_name="linguistic-example_task_pl_med_big",
    corpus=corpus_pl_med,
    language="polish",
    overwrite_project=True
)

results = extractor.extract(verbose=False)
results.nest_normalization(verbose=False)
results.save_candidates("wmt-ling_extraction-medicine-terms-pl_grande.csv")

all_terms = results.terms(limit=None)
print(f"\nNumber of terms: {len(all_terms)}")
print(f"\nTerms: {results.terms()}")
print(f"\nTagged Ngrams: {results.tagged_ngrams()}")
del extractor


