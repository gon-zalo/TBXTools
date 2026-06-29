from ...processor.bert import BertProcessor
from ...sqlite import SQLite
from transformers import TrainingArguments

class BertTrainer:

    def __init__(self, project_name, corpus, model, external_terms, overwrite_project=False, labels=None, split=False, training_args=None, lr=None, batch_size=None, epochs=None, weight_decay=None):

        self.model_name = model

        self.external_terms = external_terms
        self.labels = labels.lower()
        self.split = split

        # self.training_args = training_args or self.default_args
        # self.default_args = {"lr": 5e-05, "batch_size": 16, "epochs": 3, "weight_decay": 0.03}

        self.lr = lr or 5e-05 # learning rate
        self.batch_size = batch_size or 16
        self.epochs = epochs or 3
        self.weight_decay = weight_decay or 0.03

        self._processor = BertProcessor(model_name=self.model_name)
        self._sqlite = SQLite(project_name=project_name, corpus=corpus, overwrite_project=overwrite_project)

    def train(self, save_as=None):
        from transformers import Trainer, BertForTokenClassification, DataCollatorForTokenClassification, set_seed
        import torch
        from sklearn.model_selection import train_test_split
        from datasets import Dataset
        from pathlib import Path
        set_seed(123)

        print(f'\nInitializing model:  {self.model_name}', flush=True)
        tokenizer = self._processor.tokenizer
        labels = self._processor.choose_labels(labels=self.labels)
        label2id = {l: i for i, l in enumerate(labels)}
        id2label = {i: l for l, i in label2id.items()}
        self._processor.load_transformers()

        if self._sqlite.overwrite_project == False and Path(self._sqlite.project_name).exists():
            import pandas as pd
            print("\nExisting database found. Accessing data", flush=True)

            tokenized_segments = self._sqlite.get_segments(tagged=False, tokenized=True)
            segment_labels = self._sqlite.get_segment_labels()

            if tokenized_segments and segment_labels:
                print("Tokenized segments and labels found in database")
                data = { 
                    "tokenized_segment": pd.Series(tokenized_segments), 
                    "segment_labels": pd.Series(segment_labels)
                    }
                
                dataframe = pd.DataFrame(data=data)
            else:
                raise RuntimeError("Tokenized segments and/or segment labels not found in database. Create another project or overwrite the existing one using 'overwrite_project=True'")

        else:
            dataframe = self._prepare_data()

        if not self.split:
            dataframe = Dataset.from_pandas(dataframe)
            dataframe = dataframe.map(self._processor.prepare_pretokenized_inputs, batched=True)
        
        elif self.split:
            print("\nSplitting training data into train (0.7) and eval (0.3)")
            train_df, eval_df = train_test_split(dataframe, test_size=0.3, random_state=123)

            train_df = Dataset.from_pandas(train_df)
            eval_df = Dataset.from_pandas(eval_df)

            train_data = train_df.map(self._processor.prepare_pretokenized_inputs, batched=True)
            eval_data = eval_df.map(self._processor.prepare_pretokenized_inputs, batched=True)

        device = torch.device("cuda")
        model = BertForTokenClassification.from_pretrained(
            self.model_name,
            num_labels=len(labels),
            id2label=id2label,
            label2id=label2id).to(device)

        training_args = TrainingArguments(
            eval_strategy="no",
            logging_strategy="no", # this disables the trainer_output folder?
            learning_rate=self.lr,
            per_device_train_batch_size=self.batch_size,
            num_train_epochs=self.epochs,
            weight_decay=self.weight_decay,
            seed=123,
            data_seed=123
        )

        data_collator = DataCollatorForTokenClassification(tokenizer=tokenizer)

        if self.split:
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_data,
                eval_dataset=eval_data,
                compute_metrics=self._compute_metrics,
                data_collator=data_collator # needed to pad the sentences
            )
        else:
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

    def _compute_metrics(self, p, eval_data, id2label):
        import numpy as np
        prediction_logits, label_ids = p # label_ids are true padded label IDs from eval_data
        predictions = np.argmax(prediction_logits, axis=2)

        all_pred_terms = []
        all_true_terms = []

        for i in range(len(eval_data)):
            original_tokens = eval_data[i]['abstract_tokens']

            pred_ids = predictions[i]
            true_ids = label_ids[i]

            reconstructed_predicted_terms = self._processor.pred_labels_to_tokens(original_tokens, pred_ids, id2label)
            all_pred_terms.extend(reconstructed_predicted_terms)

            reconstructed_true_terms = self._processor.pred_labels_to_tokens(original_tokens, true_ids, id2label)
            all_true_terms.extend(reconstructed_true_terms)

        precision, recall, f1 = self.score(all_pred_terms, all_true_terms)

        return {"precision": precision, "recall": recall, "f1": f1}

    def score(self, pred_terms, true_terms): # my score func
        pred_terms = set(pred_terms)
        true_terms = set(true_terms)

        tp = len(pred_terms & true_terms) # common terms in both sets

        precision = tp / len(pred_terms)
        recall = tp / len(true_terms)
        f1 = 2 * precision * recall / (precision + recall)

        return precision, recall, f1

    def _prepare_data(self):
        from tqdm import tqdm
        print("\nBertTrainer initialized")

        self._sqlite.load_external_terms(self.external_terms)
        tokens_output, tokenized_segments, dataframe = self._processor.preprocess(segments=self._sqlite.get_segments())

        self._sqlite.insert_segments(data=tokenized_segments, tagged=False, tokenized=True)
        self._sqlite.insert_tokens(data=tokens_output)

        external_terms = self._sqlite.get_external_terms()

        print(f"\nStarting segment annotation", flush=True)

        tokenized_terms = self._processor.tokenize_terms(external_terms=external_terms)

        segment_labels = []
        for segment in tqdm(
            dataframe["tokenized_segment"], 
            desc=f"Annotating segments with {self.labels.upper()} labels", 
            total=len(dataframe)
            ):
            labels = self._processor.bio_tag(
                segment,
                tokenized_terms=tokenized_terms,
            )
            segment_labels.append(labels)

        self._sqlite.insert_segment_labels(segment_labels)

        dataframe["segment_labels"] = segment_labels

        print("Annotation finished")
        return dataframe
        