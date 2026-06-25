from TBXTools import BertTrainer

model = 'dmis-lab/biobert-base-cased-v1.2'

trainer = BertTrainer(
    project_name="bert-train-test",
    corpus="bert_train.txt",
    model=model, 
    external_terms='external_terms.txt', 
    labels="bio",
    lr=5e-05,
    batch_size=16,
    epochs=6,
    weight_decay=0.03)

trainer.train(save_as='bert-training-test')
