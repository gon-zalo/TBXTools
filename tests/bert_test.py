from TBXTools import Extractor, BertExtractor

corpus = 'bert-corpus.txt'

extractor = Extractor(
    project_name="bert-test",
    methodology=BertExtractor(model='dmis-lab/biobert-base-cased-v1.2',labels="BIO"),
    corpus=corpus,
    language="english",
    overwrite_project=True
)

results = extractor.extract(verbose=False)

print(results._tokens)