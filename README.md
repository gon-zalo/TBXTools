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

The `LinguisticMethodology` module allows you to extract terms based on different availability of pre-existing data. Below are the four main execution scenarios.

### Scenario A: Using Pre-existing Tagged Corpus and Linguistic Patterns
Use this scenario if you already have both a POS Tagged corpus and a set of predefined linguistic patterns.

```
from TBXTools import Extractor, LinguisticMethodology

extractor = Extractor(
    methodology=LinguisticMethodology(nmin=2, nmax=3, is_corpus_tagged=True, linguistic_patterns="example_patterns.txt"),
    project_name="linguistic-example",
    corpus="tagged-corpus.txt",
    language="english",
    overwrite_project=True
)

results = extractor.extract(verbose=False)

# Once the terms are extracted, we can perform other methods like the following:
results.nest_normalization(verbose=False)
results.save_candidates("linguistic-candidates.txt")

# Results can be inspected at any time with the following methods:
print(f"\nTerms: {results.terms()}")
print(f"\nTagged Ngrams: {results.tagged_ngrams()}")

```

### Scenario B: Using Pre-existing Tagged Corpus and Generating Linguistic Patterns from Scratch
Use this scenario if your corpus is already pos tagged, but you need the program to automatically extract new linguistic patterns using a list of evaluation terms.

```
from TBXTools import Extractor, LinguisticMethodology

extractor = Extractor(
    methodology=LinguisticMethodology(nmin=2, nmax=3, is_corpus_tagged=True, evaluation_terms="evaluation_terms.txt"),
    project_name="linguistic-example",
    corpus="tagged-corpus.txt",
    language="english",
    overwrite_project=True
)

results = extractor.extract(verbose=False)

# Once the terms are extracted, we can perform other methods like the following:
results.nest_normalization(verbose=False)
results.save_candidates("linguistic-candidates.txt")

# Results can be inspected at any time with the following methods:
print(f"\nTerms: {results.terms()}")
print(f"\nTagged Ngrams: {results.tagged_ngrams()}")

```

### Scenario C: Using Pre-existing Linguistic Patterns and Generating Tagged Corpus from Scratch
Use this scenario if you already have a fixed set of linguistic patterns, but you need to process a raw, untagged corpus to generate its tagged version.

```
from TBXTools import Extractor, LinguisticMethodology

extractor = Extractor(
    methodology=LinguisticMethodology(nmin=2, nmax=3, is_corpus_tagged=False, linguistic_patterns="example_patterns.txt" ),
    project_name="linguistic-example",
    corpus="raw_corpus.txt",
    language="english",
    overwrite_project=True
)

results = extractor.extract(verbose=False)

# Once the terms are extracted, we can perform other methods like the following:
results.nest_normalization(verbose=False)
results.save_candidates("linguistic-candidates.txt")

# Results can be inspected at any time with the following methods:
print(f"\nTerms: {results.terms()}")
print(f"\nTagged Ngrams: {results.tagged_ngrams()}")

```

### Scenario D: Generating Corpus and Patterns from Scratch
Use this scenario when starting completely from raw inputs. Both assets are generated automatically:
* **Tagged Corpus:** Generated from a raw, untagged corpus.
* **Linguistic Patterns:** Generated using a list of evaluation terms.

```
from TBXTools import Extractor, LinguisticMethodology

extractor = Extractor(
    methodology=LinguisticMethodology(nmin=2, nmax=3, is_corpus_tagged=False, evaluation_terms="evaluation_terms.txt"),
    project_name="linguistic-example",
    corpus="raw_corpus.txt",
    language="english",
    overwrite_project=True
)

results = extractor.extract(verbose=False)

# Once the terms are extracted, we can perform other methods like the following:
results.nest_normalization(verbose=False)
results.save_candidates("linguistic-candidates.txt")

# Results can be inspected at any time with the following methods:
print(f"\nTerms: {results.terms()}")
print(f"\nTagged Ngrams: {results.tagged_ngrams()}")

```
