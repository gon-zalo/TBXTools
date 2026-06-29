from TBXTools import BertTrainer, TrainingArguments
from sklearn.model_selection import train_test_split

biobert = 'dmis-lab/biobert-base-cased-v1.2'
herbert = "allegro/herbert-base-cased"
herbert_large = "allegro/herbert-large-cased"
polbert = "dkleczek/bert-base-polish-cased-v1"
polish_roberta = "sdadas/polish-roberta-base-v2"

trainer = BertTrainer(
    project_name="bert-train-test",
    corpus="corpus-wmt-pl.txt",
    model=polbert,
    split=True, 
    external_terms='pl_iate.txt', 
    labels="bio",
    lr=5e-05,
    batch_size=16,
    epochs=6,
    weight_decay=0.03)

trainer.train(save_as='wmt-termlgy-test-1')