from TBXTools import Extractor, StatisticalMethodology

extractor = Extractor(
    methodology=StatisticalMethodology(
        nmin=2,
        nmax=3,
        case_normalization=True
    ),
    project_name= "nest-test",
    corpus="Mental_disorder.txt",
    language= "english"
)

results = extractor.extract(verbose=False)
results.nest_normalization(verbose=True)

print(results.terms(limit=50))