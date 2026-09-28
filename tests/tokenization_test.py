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



##############


def load_corpus(self, corpus, is_corpus_tagged=False, encoding="utf-8", compoundify=False, comp_symbol="▁"):
        from pathlib import Path

        if corpus:
            if type(corpus) == str and Path(corpus).is_file():
                self.read_corpus(
                corpus_file=corpus, 
                is_corpus_tagged=is_corpus_tagged, 
                encoding=encoding)
                print(f"Corpus loaded")

            elif isinstance(corpus, list):
                is_file = False
                try:
                    if Path(corpus[0]).is_file():
                        is_file = True
                except OSError:
                        is_file  = False

                if is_file:
                    for c in corpus:
                        if Path(c).is_file():
                            self.read_corpus(
                                corpus_file=c, 
                                is_corpus_tagged=is_corpus_tagged, 
                                encoding=encoding)
                    print(f"{len(corpus)} corpora loaded")

                else: # if not file, its separate segments
                    self.insert_segments(data=corpus, tagged=is_corpus_tagged)
                    print(f"Segments loaded")
            
            else:
                raise ValueError("Corpus file not found")