from ..base import BaseMethodology
from ..._results.results import Results
from ..._processor.bert import BertProcessor
from transformers import logging
from collections import Counter

logging.set_verbosity_error()

class BertMethodology(BaseMethodology):
    '''
    Manages terminology extraction with a BERT model.

    Attributes:
        model (str): Fine-tuned model for terminology extraction using labels.
        labels (str): The labels used in the fine-tuning of the model.
    '''

    def __init__(self, model, labels=None):
        self.name = "BertMethodology"
        self.model_name = model

        self.processor = BertProcessor(model_name=self.model_name)
        self.labels = labels.lower() if labels else None

        
    def extract(self, segments, verbose, lemmatize=False):
        '''
        Extracts candidate terms using BERT. This methodology uses a previously fine-tuned model on automatically annotated data to predict labels for each token of the evaluation data.

        Args:
            segments: A list of segments to process.
            verbose (bool, optional): If True, enables detailed logging. Defaults to False.
        
        Returns:
            Results: An object containing the tokens, candidate terms. It also returns separately the tokenized corpus.
        '''
        from datasets import Dataset
        import numpy as np

        print(f'\nInitializing model:  {self.model_name}', flush=True)
        self.processor.load_transformers()

        dataframe = self.processor.preprocess_eval(segments=segments, lemmatize=lemmatize)
        
        labels = self.processor.choose_labels(self.labels)
        label2id = {l: i for i, l in enumerate(labels)}
        id2label = {i: l for l, i in label2id.items()}

        eval_data = Dataset.from_pandas(dataframe)

        print("\nPredicting terms")
        trainer = self.processor.trainer
        prediction_logits, _ , _ = trainer.predict(eval_data)
        predictions = np.argmax(prediction_logits, axis=2)
        predicted_terms = []

        if not lemmatize:
            for i in range(len(eval_data)):
                text = eval_data[i]["text"]
                offsets = eval_data[i]["offset_mapping"]
                predicted_ids = predictions[i]

                reconstructed = self.processor._pred_labels_to_text(
                    text=text,
                    offsets=offsets,
                    predicted_ids=predicted_ids,
                    id2label=id2label)
                
                predicted_terms.append(reconstructed)
                
        if lemmatize:
            for i in range(len(eval_data)):
                tokens = eval_data[i]['tokens']
                predicted_ids = predictions[i]
                reconstructed = self.processor._bio_to_terms(
                    tokens=tokens,
                    labels=predicted_ids)

                predicted_terms.append(reconstructed)

        clean_terms = self.processor.process_predictions(predicted_terms)

        dataframe['predicted_terms'] = clean_terms
        #check
        # dataframe.to_csv('./evaluation_dataframe.csv', index=False)

        #i dont remember why im doing this, but keep for now, otherwise it wont work
        clean_terms = dataframe['predicted_terms'].tolist() # this line i can remove i think
        clean_terms = self.processor._flatten_list(clean_terms)

        # output for tbxtools, calculating count of each term
        candidate_terms = []
        term_counts = Counter(clean_terms)
        term_counts = dict(sorted(term_counts.items(), key=lambda item: item[1], reverse=True))
        for term, count in term_counts.items():
            n = len(term.split(" "))
            candidate_terms.append((term, n, "count", count))
        tokenized_segments = []
        # print(candidate_terms)
        return Results(terms=candidate_terms), tokenized_segments  