from .._processor.bert import BertProcessor
from .._sqlite.sqlite import SQLite
from .metrics import Metrics

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

    def __init__(self, project_name, corpus, external_terms,model=None, overwrite_project=False, labels=None, lr=None, batch_size=None, epochs=None, weight_decay=None):

        self.model_name = model or "distilbert/distilbert-base-multilingual-cased"
        self.name = "BertTrainer"

        self._labels = labels.lower() or "bio"

        self._processor = None
        # self._labeling_scheme = self._processor.choose_labels(labels=labels.lower() or "bio")
        self._seed = 123

        self._metrics = Metrics()
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

    def train(self, sample=None, save_as=None, split=False, lemmatize=False, expand_labels=True):
        '''
        Fine-tunes the chosen model for automatic terminology extraction. It annotates the data with the chosen labels and then fine-tunes the model on said data. The model is saved to disk afterwards.

        Args:
            sample (int, optional): Number of sentences to randomly sample out of the corpus. Useful for testing purposes.
            save_as (str, optional): Path of the model to save to disk.
            split (bool, optional): If True, it splits the data in train and eval.
        '''
        from transformers import Trainer, set_seed
        from datasets import Dataset
        from transformers import TrainingArguments
        set_seed(self._seed)
        print(f'\nInitializing model:  {self.model_name}', flush=True)
        self._processor = BertProcessor(model_name=self.model_name, labels=self._labels)
        self._processor._load_model()
        self._processor._load_tokenizer_and_data_collator()
        # tokenizer = self._processor.tokenizer
        model = self._processor.model
        data_collator = self._processor.data_collator
        
        if self._sqlite.overwrite_project == False:
            dataframe = self._fetch_data_from_db(lemmatize=lemmatize)
            dataframe = self._processor.preprocess_annotated(df=dataframe, lemmatize=lemmatize)
            
        else:
            dataframe = self._prepare_train_data(sample=sample, label2id=self._processor._label2id, lemmatize=lemmatize, expand_labels=expand_labels)

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
            from sklearn.model_selection import train_test_split
            print("\nSplitting training data into train (0.7) and eval (0.3)")
            train_df, eval_df = train_test_split(dataframe, test_size=0.3, random_state=self._seed)

            # train_df.to_csv(f"train_df_{self._sqlite.project_name}.csv")
            # eval_df.to_csv(f"eval_df_{self._sqlite.project_name}.csv")

            train_data = Dataset.from_pandas(train_df)
            eval_data = Dataset.from_pandas(eval_df)

            training_args = TrainingArguments(
            eval_strategy="epoch",
            learning_rate=self.lr,
            per_device_train_batch_size=self.batch_size,
            num_train_epochs=self.epochs,
            weight_decay=self.weight_decay,
            seed=self._seed,
            data_seed=self._seed)

            self._metrics.eval_data= eval_data
            self._metrics.processor = self._processor
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_data,
                eval_dataset=eval_data,
                compute_metrics=self._metrics.compute_metrics_lemm if lemmatize else self._metrics.compute_metrics,
                data_collator=data_collator
            )

        print('Fine-tuning model', flush=True)
        trainer.train()
        if save_as:
            trainer.save_model(f'{save_as}')
            print(f"Model saved as '{save_as}'")
        
    def _prepare_train_data(self, sample, label2id, lemmatize=False, expand_labels=False):
        import random
        random.seed(self._seed)
        print("\nBertTrainer initialized")

        segments = self._sqlite.get_segments()
        external_terms = self._sqlite.get_external_terms()

        if isinstance(sample, int):
            print(f"Sampling {sample} random sentences")
            segments = random.sample(segments, sample)

        if not lemmatize:
            tokens_FD, df = self._processor.preprocess_train(
                segments=segments, 
                external_terms=external_terms, 
                expand_labels=expand_labels)

        if lemmatize:
            print("Running lemmatization")
            #################
            import spacy
            nlp = spacy.load("en_core_web_sm")
            #################
            tokens_FD, df = self._processor.preprocess_train(
                segments=segments, 
                external_terms=external_terms, 
                nlp=nlp, 
                lemmatize=lemmatize)

            self._sqlite.insert_lemmatized_corpus(data=df["lemmas"].tolist())

        #no se esta insertando nada, ni se esta eliminando el corpus, con lematizacion si
        self._sqlite.insert_tokens(data=tokens_FD)
        self._sqlite.insert_segment_labels(data=df["labels"])
        self._sqlite.delete("corpus")
        self._sqlite.insert_segments(data=df["text"].tolist(), tagged=False, tokenized=False, in_list_of_lists=False)
        self._sqlite.insert_segments(data=df["tokens"].tolist(), tagged=False, tokenized=True, in_list_of_lists=True) # inserting segments used in training
        
        # self._sqlite.insert_bert_data(df=df, lemmatize=lemmatize) # probably not necessary

        return df
    
    def _fetch_data_from_db(self, lemmatize=False):
        import pandas as pd
        print("\nFetching existing data from database", flush=True)

        segment_labels = self._sqlite.get_segment_labels()
        segments = self._sqlite.get_segments(tagged=False, tokenized=False, to_list=False)
        if lemmatize:
            segment_lemmas = self._sqlite.get_lemmatized_corpus()
            tokenized_segments = self._sqlite.get_segments(tagged=False, tokenized=True, to_list=True) # not whole corpus but (annotated) segments with word tokens

        if segment_labels:
            data = {
                "text": pd.Series(segments),
                "tokens": pd.Series(tokenized_segments) if lemmatize else None, 
                "lemmas": pd.Series(segment_lemmas) if lemmatize else None,
                "labels": pd.Series(segment_labels)
                }
            
            dataframe = pd.DataFrame(data=data)
            return dataframe
        else:
            raise RuntimeError("Necessary data not found in database. Create another project or overwrite the existing one using 'overwrite_project=True'")   

    def _model_init(self, model_name):
        from transformers import BertForTokenClassification
        return BertForTokenClassification.from_pretrained(
            model_name,
            num_labels=len(self._processor._labeling_scheme),
            id2label=self._processor._id2label,
            label2id=self._processor._label2id)

    def hp_tuning(self, models, lr_range=(1e-6, 5e-5), epoch_range=(3, 16), batch_sizes=(8, 16, 32), weight_decay_range=(0.0, 0.5), n_trials=30, lemmatize=False):
        from transformers import Trainer, TrainingArguments
        import pandas as pd
        from sklearn.model_selection import train_test_split
        from datasets import Dataset

        results = []
        print("\nRunning hyperparameter tuning", flush=True)

        if isinstance(models, str):
            models = [models]

        for model_name in models:
            self._processor = BertProcessor(model_name=model_name, labels=self._labels)
            self._processor._load_tokenizer_and_data_collator()

            dataframe = self._fetch_data_from_db(lemmatize=lemmatize)
            dataframe = self._processor.preprocess_annotated(df=dataframe, lemmatize=lemmatize)
            train_df, eval_df = train_test_split(dataframe, test_size=0.3, random_state=self._seed)
            train_data = Dataset.from_pandas(train_df)
            eval_data = Dataset.from_pandas(eval_df)

            def hp_space(trial):
                return {
                    "learning_rate": trial.suggest_float("learning_rate", lr_range[0], lr_range[1], log=True),
                    "num_train_epochs": trial.suggest_int("num_train_epochs", epoch_range[0], epoch_range[1]),
                    "per_device_train_batch_size": trial.suggest_categorical("per_device_train_batch_size", batch_sizes),
                    "weight_decay": trial.suggest_float("weight_decay", weight_decay_range[0], weight_decay_range[1])}

            training_args = TrainingArguments(
                eval_strategy="epoch",
                learning_rate=self.lr,
                per_device_train_batch_size=self.batch_size,
                num_train_epochs=self.epochs,
                weight_decay=self.weight_decay,
                seed=self._seed,
                data_seed=self._seed)
            
            self._metrics.eval_data= eval_data
            self._metrics.processor = self._processor
            
            trainer = Trainer(
                model_init=self._processor._model_init,
                args=training_args,
                train_dataset=train_data,
                eval_dataset=eval_data,
                compute_metrics=self._metrics.compute_metrics_lemm if lemmatize else self._metrics.compute_metrics,
                data_collator=self._processor.data_collator)

            print(f"\nFine-tuning {self._processor.model_name}")
            best_run = trainer.hyperparameter_search(
                direction="maximize",
                backend="optuna",
                hp_space=hp_space,
                n_trials=n_trials)

            results.append({
                "model": model_name,
                "best_score": best_run.objective,
                "hyperparameters": best_run.hyperparameters})
            
        results = pd.DataFrame(results)

        results.to_csv("hp-tuning-results.csv",index=False)