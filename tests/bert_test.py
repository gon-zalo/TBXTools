from TBXTools import Extractor, BertMethodology

corpus = 'bert_eval.txt'
model = 'biobert_detech_run2'
test_model = 'bert-model-test'

methodology = BertMethodology(
    model=model, 
    labels="bio"
)

extractor = Extractor(
    project_name="bert-eval-test-detech",
    methodology=methodology,
    corpus=corpus,
    language="english",
    overwrite_project=True
)

results = extractor.extract(verbose=False)

print(results.terms())