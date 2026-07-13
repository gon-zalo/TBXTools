from TBXTools import Extractor
from TBXTools.methodology import StatisticalMethodology

methodology = StatisticalMethodology(nmin=2, nmax=2, case_normalization=True)

extractor = Extractor("test_error", methodology=methodology, corpus="Mental_health.txt", language="en")

results = extractor.extract()