from TBXTools.trainer import BertTrainer

corpus = "./bert_pat/corpus-dret-wiki.txt"
terms = "./bert_pat/terms-dret.txt"

bert = "BSC-LT/MrBERT-ca"
longformer = "projecte-aina/longformer-base-4096-ca-v2"
roberta = "projecte-aina/roberta-base-ca-v2"

trainer = BertTrainer(
    project_name="bert-train-dret-ca",
    corpus=corpus,
    overwrite_project=False,
    language="ca",
    model=bert,
    external_terms=terms,
    labels="bio",
    epochs=10,
    lr=3e-5, batch_size=8, gradient_accumulation_steps=2, warmup_ratio=0.1)

trainer.train(split=True, lemmatize=True, expand_labels=False, only_annotate=False)
