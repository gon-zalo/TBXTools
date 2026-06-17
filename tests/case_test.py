from TBXTools import Extractor, StatisticalMethodology

extractor = Extractor(
    methodology=StatisticalMethodology(
        nmin=2,
        nmax=3,
        case_normalization=True
    ),
    project_name="case-test",
    corpus="Mental_disorder.txt",
    language= "english"
)

results = extractor.extract(verbose=True)

print(results.tokens(limit=50))