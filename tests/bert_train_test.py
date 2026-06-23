from TBXTools import Extractor, BertMethodology, BertTrainer

model = 'dmis-lab/biobert-base-cased-v1.2'

trainer = BertTrainer(
    model=model, 
    external_terms='external_terms.txt', 
    labels="bio",
    lr=5e-05,
    batch_size=16,
    epochs=3,
    weight_decay=0.03)

extractor = Extractor(
    methodology=None,
    project_name="bert-train-test",
    corpus="bert-corpus.txt",
    language="en",
    overwrite_project=True
)

extractor.train_bert(trainer=trainer)