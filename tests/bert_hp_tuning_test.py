from TBXTools.trainer import BertTrainer

trainer = BertTrainer(
    project_name="bert-train-medicine-5k-en",
    corpus="",
    overwrite_project=False,
    language="en",
    external_terms="nan", 
    labels="bio")

# distilbert = "distilbert/distilbert-base-multilingual-cased"
bert = "google-bert/bert-base-cased"
biobert = 'dmis-lab/biobert-base-cased-v1.2'

models = [bert, biobert]

trainer.hp_tuning(models=models, n_trials=10, lemmatize=False, output_file="hp-tuning-medicine-5k-en")

# lemm code
# trainer = BertTrainer(
#     project_name="bert-train-medicine-lemm-5k-en",
#     corpus="",
#     overwrite_project=False,
#     language="en",
#     external_terms="nan", 
#     labels="bio")

# trainer.hp_tuning(models=models, n_trials=10, lemmatize=True, output_file="hp-tuning-medicine-lemm-5k-en")