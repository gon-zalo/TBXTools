from TBXTools.trainer import BertTrainer

trainer = BertTrainer(
    project_name="bert-train-medicine-100kto30k-en",
    corpus="",
    overwrite_project=False,
    language="en",
    external_terms="nan", 
    labels="bio")

biobert = 'dmis-lab/biobert-base-cased-v1.2'
bert = "google-bert/bert-base-cased"

models = [bert, biobert]

trainer.hp_tuning(
    models=models, 
    n_trials=15, 
    lemmatize=True, 
    output_file="bert-train-medicine-100kto30k-en",
    lr_range=(3e-5, 6e-5), batch_sizes=(8,8), epoch_range=(6,6), sample=15000)