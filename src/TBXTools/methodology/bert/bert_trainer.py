from ...processor.bert import BertProcessor
from ...sqlite import SQLite
from transformers import TrainingArguments

class BertTrainer:
    '''
    Trains a BERT model for automatic terminology extraction.

    Attributes:
        project_name (str): The unique name identifier for the current project, which also determines the filename of the generated SQLite database.
        corpus: The text corpus used as the training data.
        model (str, optional): The BERT model to be fine-tuned. Defaults to distilbert-base-multilingual-cased.
        external_terms: File path to the terms that will be used in the data annotation process.
        labels (str, optional): The labels to annotate the data with. Defaults to BIO.
        lr (int, optional): Learning rate of the model. Defaults to 5e-05.
        batch_size (int, optional): Defaults to 16.
        epochs (int, optional): Defaults to 3.
        weight_decay (int, optional): Defaults to 0.01.
    '''

    def __init__(self, project_name, corpus, model, external_terms, overwrite_project=False, labels=None, lr=None, batch_size=None, epochs=None, weight_decay=None):

        self.model_name = model or "distilbert/distilbert-base-multilingual-cased"
        self.name = "BertTrainer"
        self._labels = labels.lower() or "bio"
        self._processor = BertProcessor(model_name=self.model_name)
        self._labels_list = self._processor.choose_labels(labels=self._labels)
        self._seed = 123

        self._label2id = {l: i for i, l in enumerate(self._labels_list)}
        self._id2label = {i: l for l, i in self._label2id.items()}
        # self.training_args = training_args or self.default_args
        # self.default_args = {"lr": 5e-05, "batch_size": 16, "epochs": 3, "weight_decay": 0.03}

        self.lr = lr or 5e-05 # learning rate
        self.batch_size = batch_size or 16
        self.epochs = epochs or 3
        self.weight_decay = weight_decay or 0.01

        self._sqlite = SQLite(
            project_name=project_name, 
            corpus=corpus, 
            overwrite_project=overwrite_project, 
            external_terms=external_terms)
        
        self._eval_data = None

    def train(self, sample, save_as=None, split=False):
        '''
        Fine-tunes the chosen model for automatic terminology extraction. It annotates the data with the chosen labels and then fine-tunes the model on said data. The model is saved to disk afterwards.

        Args:
            sample (int, optional): Number of sentences to randomly sample out of the corpus. Useful for testing purposes
            save_as (str, optional): Path of the model to save to disk. Defaults to 'fine-tuned-bert'
            split (bool, optional): If True, it splits the data in train and eval.
        '''
        from transformers import Trainer, BertForTokenClassification, DataCollatorForTokenClassification, set_seed
        import torch
        from sklearn.model_selection import train_test_split
        from datasets import Dataset
        from pathlib import Path
        set_seed(self._seed)

        print(f'\nInitializing model:  {self.model_name}', flush=True)
        self._processor.load_transformers()
        tokenizer = self._processor.tokenizer
        # labels = self._processor.choose_labels(labels=self._labels)

        # if not overwrite,
        # need to fix this, it wont work now
        if self._sqlite.overwrite_project == False:
            dataframe = self._fetch_data_from_db()

        else:
            dataframe = self._prepare_train_data(sample=sample, label2id=self._label2id, split=split)

        device = torch.device("cuda")
        model = BertForTokenClassification.from_pretrained(
            self.model_name,
            num_labels=len(self._labels_list),
            id2label=self._id2label,
            label2id=self._label2id).to(device)

        data_collator = DataCollatorForTokenClassification(tokenizer=tokenizer)

        if not split:
            train_data = Dataset.from_pandas(dataframe)

            training_args = TrainingArguments(
            eval_strategy="no",
            logging_strategy="no", # this disables the trainer_output folder?
            learning_rate=self.lr,
            per_device_train_batch_size=self.batch_size,
            num_train_epochs=self.epochs,
            weight_decay=self.weight_decay,
            seed=self._seed,
            data_seed=self._seed
            )

            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_data,
                data_collator=data_collator # needed to pad the sentences
            )
        
        elif split:
            print("\nSplitting training data into train (0.7) and eval (0.3)")
            train_df, eval_df = train_test_split(dataframe, test_size=0.3, random_state=self._seed)

            train_data = Dataset.from_pandas(train_df)
            eval_data = Dataset.from_pandas(eval_df)

            # train_data = train_df.map(self._processor.preprocess_train, batched=True)
            # eval_data = eval_df.map(self._processor.preprocess_eval, batched=True)

            training_args = TrainingArguments(
            eval_strategy="epoch",
            learning_rate=self.lr,
            per_device_train_batch_size=self.batch_size,
            num_train_epochs=self.epochs,
            weight_decay=self.weight_decay,
            seed=self._seed,
            data_seed=self._seed
            )

            self._eval_data = eval_data
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_data,
                eval_dataset=eval_data,
                compute_metrics=self._compute_metrics,
                data_collator=data_collator
            )

        print('Fine-tuning model', flush=True)
        trainer.train()
        if not save_as:
            save_as = './fine-tuned-bert'

        trainer.save_model(f'{save_as}')
        print(f"Model saved as '{save_as}'")
        
    def _prepare_train_data(self, sample, label2id, split=False):
        from tqdm import tqdm
        import random
        import pandas as pd
        random.seed(self._seed)
        print("\nBertTrainer initialized")

        segments = self._sqlite.get_segments()

        if isinstance(sample, int):
            print(f"Sampling {sample} random sentences")
            segments = random.sample(segments, sample)

        tokens_FD, dataframe = self._processor.preprocess_train(segments=segments)

        self._sqlite.insert_tokens(data=tokens_FD)

        tokenized_terms = self._processor.tokenize_and_tag_terms(external_terms=self._sqlite.get_external_terms())

        dataframe = self.annotate_and_filter_segments(dataframe, tokenized_terms)
        self._sqlite.insert_segment_labels(data=dataframe["labels"])
        
        # need to transform annotated labels into integers for the model training
        labels_int = []
        for sequence in dataframe["labels"]:
            label_ids = []

            for label in sequence:
                label_ids.append(label2id[label])

            labels_int.append(label_ids)

        dataframe["labels"] = labels_int

        print(f"Remaining segments: {len(dataframe)}")

        self._sqlite.insert_segments(data=dataframe["tokens"].tolist(), tagged=False, tokenized=True)

        print("Annotation finished")
        return dataframe
    
    def annotate_and_filter_segments(self, dataframe, tokenized_terms):
        from tqdm import tqdm
        print(f"\nStarting segment annotation", flush=True)
        segment_labels = []
        for segment in tqdm(
            dataframe["tokens"], 
            desc=f"Annotating segments with {self._labels.upper()} labels", 
            total=len(dataframe)):
            labels = self._processor.annotate(
                segment,
                tokenized_terms=tokenized_terms,
            )
            segment_labels.append(labels)
        dataframe["labels"] = segment_labels

        print(f"\nFiltering out segments that only contain '{labels[0]}' labels", flush=True)
        # only keeping rows that contain B or I labels
        filter = dataframe["labels"].apply(lambda seg_labels: any(label in ["B", "I"] for label in seg_labels))
        dataframe = dataframe[filter]
        
        return dataframe
    
    def _fetch_data_from_db(self):
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

            return dataframe
        else:
            raise RuntimeError("Tokenized segments and/or segment labels not found in database. Create another project or overwrite the existing one using 'overwrite_project=True'")

    def _compute_metrics(self, p):
        import numpy as np
        prediction_logits, label_ids = p # label_ids are true padded label IDs from eval_data
        predictions = np.argmax(prediction_logits, axis=2)

        all_pred_terms = []
        all_true_terms = []

        for i in range(len(self._eval_data)):
            text = self._eval_data[i]["text"]
            offsets = self._eval_data[i]["offset_mapping"]
            pred_ids = predictions[i]
            print(pred_ids)
            true_ids = label_ids[i]
            print(true_ids)
            reconstructed_predicted_terms = self._processor.pred_labels_to_text(text, offsets, pred_ids, self._id2label)
            all_pred_terms.extend(reconstructed_predicted_terms)

            reconstructed_true_terms = self._processor.pred_labels_to_text(text, offsets, true_ids, self._id2label)
            all_true_terms.extend(reconstructed_true_terms)

        print(all_pred_terms)
        print(all_true_terms)
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