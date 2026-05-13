# How to install (beta version)

1. Clone the repository:

`git clone https://github.com/gon-zalo/TBXTools.git`

2. Create your own virtual or conda environment and activate it.
2. Inside the repository folder type:

`pip install . `

4. Now you can use the package.

## Code example (will change)
```
from TBXTools import Extractor, StatisticalExtractor

extractor = Extractor(
    method=StatisticalExtractor(
        nmin=2,
        nmax=3),
    project_name="example",
    corpus="example-corpus.txt"
)

results = extractor.extract(case_normalization=True, verbose=False)

results.nest_normalization()
results.regex_exclusion()
results.save_candidates("save-example.txt")

# Results can be inspected with the following methods:
print(results.terms())
print(results.ngrams())
print(results.tokens())
```
