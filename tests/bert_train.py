from TBXTools.trainer import BertTrainer

xlm_roberta = "FacebookAI/xlm-roberta-base"

trainer = BertTrainer(
    project_name="wmt-bert-train-allpositive-ate",
    language="en")

trainer.train(
    model= xlm_roberta, 
    save_as="wmt-roberta-allpositive-2-ate", 
    split=False, 
    expand_labels=False, 
    lr=4.5e-5, 
    batch_size=32, 
    epochs=1.7, 
    weight_decay=0.028, 
    warmup_ratio=0.016)

# parameters both lang, both domains
# Parameters: lr = 4.52034259861242e-05, epochs = 5, batch_size = 16, weight_decay = 0.028099146321555947, warmup_ratio = 0.01668312545962061