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
    method=StatisticalExtractor(nmin=2,nmax=3),
    project_name="example-project",
    corpus="example-corpus.txt"
)

extractor.extract()

# Can be inspected this way
print(extractor.terms()) 
print(extractor.tokens())

extractor.save_candidates("candidates_test.txt")
```
