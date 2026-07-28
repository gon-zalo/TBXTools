from TBXTools.trainer import BertTrainer

xlm_roberta = "FacebookAI/xlm-roberta-base"
xlm_roberta_large = "FacebookAI/xlm-roberta-large"
# roberta = "sdadas/polish-roberta-base-v2"

trainer = BertTrainer(
    project_name="wmt-bert-train-allpositive-ate",
    corpus="",
    overwrite_project=False,
    language="en",
    model=xlm_roberta_large,
    external_terms="nan", # code to handle this if everything is already in db 
    labels="bio",
    lr=4.5e-5,
    batch_size=32,
    epochs=1,
    weight_decay=0.028,
    warmup_ratio=0.016)

trainer.train(save_as="wmt-robertalarge-allpositive-ate", split=False, lemmatize=True, expand_labels=False, only_annotate=False)

# parameters both lang, both domains
# Parameters: lr = 4.52034259861242e-05, epochs = 5, batch_size = 16, weight_decay = 0.028099146321555947, warmup_ratio = 0.01668312545962061