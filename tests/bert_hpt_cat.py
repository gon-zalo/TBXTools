from TBXTools.trainer import BertTrainer

trainer = BertTrainer(
    project_name="bert-train-dret-ca",
    corpus="",
    overwrite_project=False,
    language="ca",
    external_terms="nan", 
    labels="bio")

roberta = "projecte-aina/roberta-base-ca-v2"
bert = "BSC-LT/MrBERT-ca"
longformer = "projecte-aina/longformer-base-4096-ca-v2"

models = [roberta, bert, longformer]

trainer.hp_tuning(
    models=models, 
    n_trials=15, 
    lemmatize=True, 
    output_file="bert-hpt-ca",
    lr_range=(1e-5, 5e-5), batch_sizes=(8,16,32), epoch_range=(3,8))