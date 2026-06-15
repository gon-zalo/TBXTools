from TBXTools import BertTrainer
model = 'dmis-lab/biobert-base-cased-v1.2'
trainer = BertTrainer(model=model, external_terms='external_terms.txt', labels="bio")