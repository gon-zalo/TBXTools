from TBXTools import Extractor
from TBXTools.methodology import StatisticalMethodology

regexes = [".+ health"]
tsr_terms="tsr_terms.txt"
corpus_ca = "Trastorn_mental.txt"

extractor = Extractor(methodology=StatisticalMethodology(
        nmin=2,
        nmax=3,
        case_normalization=False,
        lemmatization=True
    ),
    project_name="statistical-example_lemmatization_catalan",
    corpus=corpus_ca,
    language="catalan",
    overwrite_project=True)
    

results = extractor.extract(verbose=False)

results.nest_normalization(verbose=False)
results.regex_exclusion(regexes=regexes, verbose=False)
#results.save_candidates("statistical-candidates.txt")

# Results can be inspected with the following methods:
all_terms = results.terms(limit=None)
print(f"\nNumber of terms: {len(all_terms)}. Expected number: 239") 
print(f"\nTerms: {results.terms()}")
print(f"\nNgrams: {results.ngrams()}")
print(f"\nTokens: {results.tokens()}") 


from TBXTools import Extractor, StatisticalMethodology

regexes = [".+ health"]
tsr_terms="tsr_terms.txt"
corpus_es = "Trastorno_mental.txt"

extractor = Extractor(methodology=StatisticalMethodology(
        nmin=2,
        nmax=3,
        case_normalization=False,
        lemmatization=True
    ),
    project_name="statistical-example_lemmatization_spanish",
    corpus=corpus_es,
    language="spanish",
    overwrite_project=True)
    

results = extractor.extract(verbose=False)

results.nest_normalization(verbose=False)
results.regex_exclusion(regexes=regexes, verbose=False)
#results.save_candidates("statistical-candidates.txt")

# Results can be inspected with the following methods:
all_terms = results.terms(limit=None)
print(f"\nNumber of terms: {len(all_terms)}. Expected number: 239") 
print(f"\nTerms: {results.terms()}")
print(f"\nNgrams: {results.ngrams()}")
print(f"\nTokens: {results.tokens()}") 


from TBXTools import Extractor, StatisticalMethodology

regexes = [".+ health"]
tsr_terms="tsr_terms.txt"
corpus_fr = "Trouble_psychique.txt"

extractor = Extractor(methodology=StatisticalMethodology(
        nmin=2,
        nmax=3,
        case_normalization=False,
        lemmatization=True
    ),
    project_name="statistical-example_lemmatization_catalan",
    corpus=corpus_fr,
    language="french",
    overwrite_project=True)
    

results = extractor.extract(verbose=False)

results.nest_normalization(verbose=False)
results.regex_exclusion(regexes=regexes, verbose=False)
#results.save_candidates("statistical-candidates.txt")

# Results can be inspected with the following methods:
all_terms = results.terms(limit=None)
print(f"\nNumber of terms: {len(all_terms)}. Expected number: 239") 
print(f"\nTerms: {results.terms()}")
print(f"\nNgrams: {results.ngrams()}")
print(f"\nTokens: {results.tokens()}") 





