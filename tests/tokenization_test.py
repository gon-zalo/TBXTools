from TBXTools import Extractor
from TBXTools.methodology import StatisticalMethodology

methodology = StatisticalMethodology(nmin=2, nmax=3, case_normalization=True)
dret = "bert_pat/corpus-dret-eval.txt"
tutorial = "../tutorial/wikipedia-mental-health.txt"

extractor = Extractor(
    project_name="tokenization",
    methodology=methodology,
    corpus="bert_pat/corpus_dretshumans_universal_ca.txt",
    language="ca",
    overwrite_project=True
)

results = extractor.extract(timer=False)
# results.regex_exclusion(["nacions \w+"], mode="flexible", verbose=False)

results.summary()