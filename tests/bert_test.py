from TBXTools import Extractor, BertMethodology

corpus = 'bert-corpus.txt'
# model_name = 'dmis-lab/biobert-base-cased-v1.2'
model = 'biobert_detech_run2'
methodology = BertMethodology(model=model)

extractor = Extractor(
    project_name="bert-test",
    methodology=methodology,
    corpus=corpus,
    language="english",
    overwrite_project=True
)

results = extractor.extract(verbose=False)

print(results.terms())