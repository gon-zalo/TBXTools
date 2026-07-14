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
    project_name="bert-train-medicine-lemm-5k-en",
    corpus=medicine_en,
    overwrite_project=True,
    language="en",
    model=bert,
    external_terms=terms_medicine_en, 
    labels="bio",
    lr=5e-05,
    batch_size=16,
    epochs=3,
    weight_decay=0.03)

trainer.train(sample=5000, split=True, lemmatize=True, expand_labels=False)
