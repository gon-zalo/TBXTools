# How to install (beta version)

1. Clone the repository:

`git clone https://github.com/gon-zalo/TBXTools.git`

2. Create your own virtual or conda environment and activate it.
2. Inside the repository folder type:
`pip install . `
3. Now you can use the package.

## Code example (will change)
```
from TBXTools import TerminologyExtractor

extractor = TerminologyExtractor()
extractor.create_project("example", overwrite=True)
extractor.load_corpus()
extractor.ngram_calculation(n_min=2, n_max=3)
extractor.load_stopwords()
extractor.load_innerstopwords()
extractor.statistical_term_extraction()
extractor.case_normalization(verbose=True)
extractor.nest_normalization(verbose=True)
extractor.load_exclusion_regexes()
extractor.regexp_exclusion(verbose=True)
extractor.save_candidates("candidates-example.txt")
```