# How to install (beta version)

1. Clone the repository:

`git clone https://github.com/gon-zalo/TBXTools.git`

2. Create your own virtual or conda environment using Python 3.11 and activate it.
3. Inside the repository folder type:

`pip install .`

4. Now you can use the package.


# Term extraction methodologies
## Statistical methodology
The `StatisticalMethodology` class from the the `methodology` module allows you to extract terms from a corpus using statistical methods. Below you can find an example script.
```python
from TBXTools import Extractor
from TBXTools.methodology import StatisticalMethodology

methodology = StatisticalMethodology(nmin=2, nmax=3, case_normalization=True)
extractor = Extractor(
    methodology=methodology,
    project_name="statistical-example",
    corpus="example-corpus.txt",
    language="english",
    overwrite_project=True
)

results = extractor.extract(verbose=False)
```

## Linguistic methodology

The `LinguisticMethodology` class from the `methodology` module allows you to extract terms based on different availability of pre-existing data. Below are the four main execution scenarios.

### Scenario A: Using Pre-existing Tagged Corpus and Linguistic Patterns
Use this scenario if you already have both a POS tagged corpus and a set of predefined linguistic patterns.

```python
from TBXTools import Extractor
from TBXTools.methodology import LinguisticMethodology

methodology = LinguisticMethodology(
    nmin=2, 
    nmax=3, 
    is_corpus_tagged=True, 
    linguistic_patterns="example_patterns.txt")

extractor = Extractor(
    methodology=methodology,
    project_name="linguistic-example",
    corpus="tagged-corpus.txt",
    language="english",
    overwrite_project=True
)

results = extractor.extract(verbose=False)
```

### Scenario B: Using Pre-existing Tagged Corpus and Generating Linguistic Patterns from Scratch
Use this scenario if your corpus is already POS tagged, but you need the program to automatically extract new linguistic patterns using a list of evaluation terms.

```python
from TBXTools import Extractor
from TBXTools.methodology import LinguisticMethodology

methodology = LinguisticMethodology(
    nmin=2, 
    nmax=3, 
    is_corpus_tagged=True, 
    evaluation_terms="evaluation_terms.txt")

extractor = Extractor(
    methodology=methodology,
    project_name="linguistic-example",
    corpus="tagged-corpus.txt",
    language="english",
    overwrite_project=True
)

results = extractor.extract(verbose=False)
```

### Scenario C: Using Pre-existing Linguistic Patterns and Generating Tagged Corpus from Scratch
Use this scenario if you already have a fixed set of linguistic patterns, but you need to process a raw, untagged corpus to generate its tagged version.

```python
from TBXTools import Extractor
from TBXTools.methodology import LinguisticMethodology

methodology = LinguisticMethodology(
    nmin=2, 
    nmax=3, 
    is_corpus_tagged=False, 
    linguistic_patterns="example_patterns.txt")

extractor = Extractor(
    methodology=methodology,
    project_name="linguistic-example",
    corpus="raw_corpus.txt",
    language="english",
    overwrite_project=True
)

results = extractor.extract(verbose=False)
```

### Scenario D: Generating Corpus and Patterns from Scratch
Use this scenario when starting completely from raw inputs. Both assets are generated automatically:
* **Tagged Corpus:** Generated from a raw, untagged corpus.
* **Linguistic Patterns:** Generated using a list of evaluation terms.

```python
from TBXTools import Extractor
from TBXTools.methodology import LinguisticMethodology

methodology = LinguisticMethodology(
    nmin=2, 
    nmax=3, 
    is_corpus_tagged=False, 
    evaluation_terms="evaluation_terms.txt")

extractor = Extractor(
    methodology=methodology,
    project_name="linguistic-example",
    corpus="raw_corpus.txt",
    language="english",
    overwrite_project=True
)

results = extractor.extract(verbose=False)
```

## Bert methodology (WORK IN PROGRESS)
The `BertMethodology` class from the `methodology` module allows you to extract terms using a BERT model. To use this methodology, you need a fine-tuned model on terminology extraction using BIO labels.
You may fine-tune such a model using the `BertTrainer` class from the `trainer` module. For this, you only need two things: a list of external terms and a corpus. The tool will automatically annotate the corpus based on the external terms list and will fine-tune your model of choice on that corpus. Below you can find an example of the whole process.

```python
from TBXTools import Extractor
from TBXTools.methodology import BertMethodology
from TBXTools.trainer import BertTrainer

distilbert = "distilbert/distilbert-base-multilingual-cased"

trainer = BertTrainer(
    project_name="bert-train-example",
    corpus="example-train-corpus.txt",
    model=distilbert,
    external_terms="example_terms.txt"
    lr=5e-05,
    batch_size=16,
    epochs=3,
    weight_decay=0.03
)

trainer.train(save_as="bert-model-example", split=False)

fine_tuned_model = "bert-model-example"
methodology = BertMethodology(model="bert-model-example")
extractor = Extractor(
    project_name=fine_tuned_model,
    methodology=methodology,
    corpus="example-eval-corpus.txt",
    language="en",
)

results = extractor.extract(verbose=False)
```

# Results postprocessing

Once the terms have been extracted, we can perform other methods like the following:

```python
results.nest_normalization(verbose=False)

results.lemmatization(verbose=False)

results.regex_exclusion(exclusion_regexes="regexes.txt", verbose=False)
# The 'exclusion_regexes' arg accepts a text file or a Python list, e.g. regexes = [".+ health", ".+ diseases"]

results.tsr(tsr_terms="tsr.txt", type="strict", max_iteration=10, verbose=False)
# The 'tsr_terms' arg accepts a text file or a Python list, e.g. tsr_terms = ["bipolar disorder", "mental health"]
# In 'type' you may choose between: strict, flexible, and combined
# In 'max_iteration' you may introduce any integer

results.save_candidates("candidates.txt")
# Candidates can be saved in .txt, .csv, and .xlsx changing the file extension

# Results can also  be inspected at any time with the following methods, depending on the methodology:
print(results.terms())
print(results.ngrams())
print(results.tokens())
print(results.tagged_ngrams())
```