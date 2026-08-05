from TBXTools import Extractor
from TBXTools.methodology import StatisticalMethodology
regexes = [".+ health"]

extractor = Extractor(
    methodology=StatisticalMethodology(
        nmin=2, 
        nmax=3,
        case_normalization=True
    ),
    project_name="regexes-test",
    corpus="Mental_disorder.txt",
    language="english",
    overwrite_project=True
)

results = extractor.extract(verbose=False)
results.regex_exclusion(regexes=regexes, verbose=True)

print(results.terms(limit=50))