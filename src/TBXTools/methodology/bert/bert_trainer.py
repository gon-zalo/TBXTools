from transformers import Trainer, TrainingArguments, BertForTokenClassification, DataCollatorForTokenClassification, AutoTokenizer, set_seed
import torch
from sklearn.model_selection import train_test_split
from datasets import Dataset
import numpy as np
set_seed(123)

class BertTrainer:

    def __init__(self, model=None, external_terms=None, lr=None, batch_size=None, epochs=None, weight_decay=None, labels=None):

        self.model_name = model
        self.model = BertForTokenClassification.from_pretrained(self.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, max_length=512, force_download=False, do_lower_case=False)
        self.external_terms = external_terms
        self.labels = labels.lower()

        self.lr = lr or 5e-05 # learning rate
        self.batch_size = batch_size or 16
        self.epochs = epochs or 3
        self.weight_decay = weight_decay or 0.03

    def prepare_data(self, data):
        import pandas as pd
        df = pd.read_json(data, orient='records', lines=True)

        return df

    def prepare_pretokenized_inputs(self, batch):
        from transformers import BertTokenizer

        tokenizer = self.tokenizer

        bio_labels = ['O', 'B', 'I']
        label2id = {l: i for i, l in enumerate(bio_labels)}
        id2label = {i: l for l, i in label2id.items()}

        max_length = 512
        input_ids = []
        attention_masks = []
        labels = []

        for tokens, token_labels in zip(batch['abstract_tokens'], batch['abstract_labels']):

            tokens = tokens[:max_length]
            token_labels = token_labels[:max_length]

            pad_length = max_length - len(tokens)
            tokens += ['[PAD]'] * pad_length
            token_labels += [-100] * pad_length

            # tokens to input ids
            input_ids.append(tokenizer.convert_tokens_to_ids(tokens))

            # attention mask
            attention_masks.append([1 if token != '[PAD]' else 0 for token in tokens])

            # bio labels to ids
            ignore_tokens = {"[CLS]", "[SEP]", "[PAD]"}

            num_labels = []
            for token, label in zip(tokens, token_labels):
                if token in ignore_tokens:
                    num_labels.append(-100)
                elif label == -100:
                    num_labels.append(-100)
                else:
                    numeric_id = label2id.get(label, -100)
                    num_labels.append(numeric_id)

            labels.append(num_labels)

        batch['input_ids'] = input_ids
        batch['attention_mask'] = attention_masks
        batch['labels'] = labels

        return batch

    def train(self):
        print('Not splitting data. Training model on the full training data.')
        train_df = self.prepare_data(train_data)

        train_data = Dataset.from_pandas(train_df) # huggingface format
        train_data = train_data.map(self.prepare_pretokenized_inputs, batched=True)

        print(f'\nInitializing model:  {self.model_name}')
        tokenizer = self.tokenizer
        bio_labels = ['O', 'B', 'I']
        label2id = {l: i for i, l in enumerate(bio_labels)}
        id2label = {i: l for l, i in label2id.items()}

        device = torch.device("cuda")
        model = BertForTokenClassification.from_pretrained(
            self.model_name,
            num_labels=len(bio_labels),
            id2label=id2label,
            label2id=label2id).to(device)

        training_args = TrainingArguments(
            eval_strategy="no",
            learning_rate=self.lr,
            per_device_train_batch_size=self.batch_size,
            num_train_epochs=self.epochs,
            weight_decay=self.weight_decay
        )

        data_collator = DataCollatorForTokenClassification(tokenizer=tokenizer)

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_data,
            data_collator=data_collator # needed to pad the sentences
        )

        print('Fine-tuning model on full training data...')
        trainer.train()
        trainer.save_model('../biobert_detech_run2/')