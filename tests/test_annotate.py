from TBXTools.trainer import BertTrainer

trainer = BertTrainer(
    project_name="test-annotate",
    language="english",
    corpus="corpus-en/text-medicine-en.txt",
    external_terms="wmt26/terms/terms-medicine-en.txt"
    overwrite_project=True
)
trainer.annotate()