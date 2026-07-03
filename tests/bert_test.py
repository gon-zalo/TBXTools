from TBXTools import Extractor, BertMethodology

corpus = 'bert_eval.txt'
corpus_wmt = 'corpus-wmt-pl.txt'
model = 'biobert_detech_run2'
test_model = 'wmt-termlgy-test'

methodology = BertMethodology(
    model=test_model, 
    labels="bio"
)

extractor = Extractor(
    project_name="bert-eval-test",
    methodology=methodology,
    corpus=corpus,
    language="english",
    overwrite_project=True
)

results = extractor.extract(verbose=False)

print(results.terms())