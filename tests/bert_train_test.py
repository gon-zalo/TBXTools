from TBXTools import Extractor, BertMethodology, BertTrainer
model = 'dmis-lab/biobert-base-cased-v1.2'

trainer = BertTrainer(model=model, external_terms='external_terms.txt', labels="bio")

corpus = "bert-corpus.txt"

# extractor = Extractor(
#     project_name="train-test",
#     methodology=None,
#     corpus="bert-corpus.txt",
#     language="en",
#     overwrite_project=True
# )

corpus_lines = []
with open(corpus, "r", encoding="utf-8") as f:
    for line in f:
        corpus_lines.append(line)

# print(corpus_lines)
trainer.train(train_data=corpus_lines)