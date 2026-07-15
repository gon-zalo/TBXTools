from TBXTools.trainer import BertTrainer

biobert = 'dmis-lab/biobert-base-cased-v1.2'
herbert = "allegro/herbert-base-cased"
herbert_large = "allegro/herbert-large-cased"
polbert = "dkleczek/bert-base-polish-cased-v1"
polish_roberta = "sdadas/polish-roberta-base-v2"
distilbert = "distilbert/distilbert-base-multilingual-cased"
pl_distilbert = "Geotrend/distilbert-base-pl-cased"

bert = "google-bert/bert-base-cased"

engineering_en = "wmt26/corpora/corpus-engineering-and-technology-en.txt"
terms_engineering_en = "wmt26/terms/terms-engineering-and-technology-en.txt"

medicine_en = "wmt26/corpora/corpus-medicine-en.txt"
terms_medicine_en = "wmt26/terms/terms-medicine-en.txt"

trainer = BertTrainer(
    project_name="bert-train-test-lemmatize",
    corpus=medicine_en,
    overwrite_project=False,
    model=bert,
    external_terms=terms_medicine_en, 
    labels="bio",
    lr=5e-05,
    batch_size=16,
    epochs=6,
    weight_decay=0.03)

trainer.train(sample=100, save_as=None, split=True, lemmatize=True)
