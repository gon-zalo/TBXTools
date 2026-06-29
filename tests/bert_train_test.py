from TBXTools import BertTrainer, TrainingArguments

biobert = 'dmis-lab/biobert-base-cased-v1.2'
herbert = "allegro/herbert-base-cased"
herbert_large = "allegro/herbert-large-cased"
polbert = "dkleczek/bert-base-polish-cased-v1"
polish_roberta = "sdadas/polish-roberta-base-v2"
distilbert = "distilbert/distilbert-base-multilingual-cased"
pl_distilbert = "Geotrend/distilbert-base-pl-cased"

corpus = "corpus-wmt-pl.txt"
corpus_small = "corpus-wmt-pl-small.txt"
corpus_mini = "corpus-wmt-pl-mini.txt"
corpus_nano = "corpus-wmt-pl-nano.txt"

trainer = BertTrainer(
    project_name="bert-train-small",
    corpus=corpus_small,
    overwrite_project=True,
    model=polbert,
    external_terms='pl_iate.txt', 
    labels="bio",
    split=False, 
    lr=5e-05,
    batch_size=16,
    epochs=6,
    weight_decay=0.03)

trainer.train(save_as='wmt-termlgy-test-polbert')