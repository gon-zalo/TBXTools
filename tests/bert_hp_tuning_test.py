from TBXTools import BertTrainer

trainer = BertTrainer(
    project_name="bert-train-engitech-en",
    corpus="",
    overwrite_project=False,
    external_terms="nan", 
    labels="bio")

distilbert = "distilbert/distilbert-base-multilingual-cased"
bert = "google-bert/bert-base-cased"
biobert = 'dmis-lab/biobert-base-cased-v1.2'

models = [distilbert, bert, biobert]

trainer.hp_tuning(models=models, n_trials=30, lemmatize=False)