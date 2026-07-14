from TBXTools.methodology.bert import BertTrainer

trainer = BertTrainer(
    project_name="bert-train-engitech-en",
    corpus="",
    overwrite_project=False,
    external_terms="nan", 
    labels="bio")

# distilbert = "distilbert/distilbert-base-multilingual-cased" # bad performance
bert = "google-bert/bert-base-cased"
biobert = 'dmis-lab/biobert-base-cased-v1.2'

models = [bert, biobert]

trainer.hp_tuning(models=models, n_trials=10, lemmatize=False)
