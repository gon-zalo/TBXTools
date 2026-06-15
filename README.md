# How to install (beta version)

1. Clone the repository:

`git clone https://github.com/gon-zalo/TBXTools.git`

2. Create your own virtual or conda environment and activate it.
2. Inside the repository folder type:

`pip install . `

4. Now you can use the package.

## Statistical methodology example
```
from TBXTools import Extractor, StatisticalMethodology

extractor = Extractor(
    methodology=StatisticalMethodology(
        nmin=2,
        nmax=3),
    project_name="statistical-example",
    corpus="example-corpus.txt",
    language="english",
    overwrite_project=True
)

results = extractor.extract(case_normalization=True, verbose=False)

# Once the terms are extracted, we can perform other methods like the following:
results.nest_normalization()
results.regex_exclusion()
results.save_candidates("save-example.txt")

# Results can be inspected at any time with the following methods:
print(results.terms())
print(results.ngrams())
print(results.tokens())
```

## Linguistic methodology example
```
from TBXTools import Extractor, LinguisticMethodology

```

### With tagged corpus...

### With patterns...

### Without tagged corpus...