from ...processor.bert import BertProcessor
from ...sqlite import SQLite

class BertTrainer:

    def __init__(self, project_name, corpus, model, external_terms, labels=None, lr=None, batch_size=None, epochs=None, weight_decay=None):

        self.model_name = model

        self.external_terms = external_terms
        self.labels = labels.lower()
        self.lr = lr or 5e-05 # learning rate
        self.batch_size = batch_size or 16
        self.epochs = epochs or 3
        self.weight_decay = weight_decay or 0.03

        self._processor = BertProcessor(model_name=self.model_name)
        self._sqlite = SQLite(project_name=project_name, corpus=corpus, overwrite_project=True)

    def train(self, save_as=None):
        from transformers import Trainer, TrainingArguments, BertForTokenClassification, DataCollatorForTokenClassification, AutoTokenizer, set_seed
        import torch
        from sklearn.model_selection import train_test_split
        from datasets import Dataset
        set_seed(123)

        dataframe = self._prepare_data()
        dataframe = Dataset.from_pandas(dataframe)
        dataframe = dataframe.map(self._processor.prepare_pretokenized_inputs, batched=True)

        print(f'\nInitializing model:  {self.model_name}', flush=True)
        tokenizer = self._processor.tokenizer
        labels = self._processor.choose_labels(labels=self.labels)
        label2id = {l: i for i, l in enumerate(labels)}
        id2label = {i: l for l, i in label2id.items()}

        device = torch.device("cuda")
        model = BertForTokenClassification.from_pretrained(
            self.model_name,
            num_labels=len(labels),
            id2label=id2label,
            label2id=label2id).to(device)

        training_args = TrainingArguments(
            eval_strategy="no",
            logging_strategy="no", # disable the trainer_output folder?
            learning_rate=self.lr,
            per_device_train_batch_size=self.batch_size,
            num_train_epochs=self.epochs,
            weight_decay=self.weight_decay
        )

        data_collator = DataCollatorForTokenClassification(tokenizer=tokenizer)

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=dataframe,
            data_collator=data_collator # needed to pad the sentences
        )

        print('Fine-tuning model', flush=True)
        trainer.train()
        if not save_as:
            save_as = './fine-tuned-bert'

        trainer.save_model(f'{save_as}')
        print(f"Model saved as '{save_as}'")

    def _prepare_data(self):
        import pandas as pd
        from datasets import Dataset
        print("\nBertTrainer initialized")

        self._sqlite.load_external_terms(self.external_terms)
        self._processor.load_transformers()
        tokens_output, tokenized_corpus_for_sqlite, dataframe = self._processor.preprocess(segments=self._sqlite.get_segments())

        self._sqlite.insert_segments(data=tokenized_corpus_for_sqlite, tagged=False, tokenized=True)
        self._sqlite.insert_tokens(data=tokens_output)

        print(f"\nAnnotating segments with {self.labels.upper()} labels", flush=True)
        dataframe["segment_labels"] = dataframe.apply(
            lambda row: self._processor.bio_tag(
                row["tokenized_segment"],
                tokenizer=self._processor.tokenizer,
                external_terms=self._sqlite.get_external_terms()
            ),
            axis=1)
        print("Annotation finished")
        return dataframe
        