from ..base import BaseMethodology
from ...results import Results
from ...processor.bert import BertProcessor
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

        self._processor = BertProcessor(model_name=self.model_name)
        self.labels = labels.lower() if labels else None

        
    def extract(self, segments, verbose):
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

        self._processor.load_transformers()
        tokens_output, tokenized_corpus_for_sqlite, dataframe = self._processor.preprocess(segments=segments, verbose=verbose)
        labels = self._processor.choose_labels(self.labels)
        label2id = {l: i for i, l in enumerate(labels)}
        id2label = {i: l for l, i in label2id.items()}

        # need to check this nonsense
        dataframe = Dataset.from_pandas(dataframe)
        eval_data = dataframe.map(self._processor.prepare_unlabeled_inputs, batched=True)

        # df = eval_data.to_pandas()
        # print(df.head())
        # df.to_csv("ins.csv", index=False)

        print("\nPredicting terms")
        trainer = self._processor.trainer
        prediction_logits, _, _ = trainer.predict(eval_data)
        predictions = np.argmax(prediction_logits, axis=2)
        predicted_tokens = []
        for i in range(len(eval_data)):
            tokens = eval_data[i]['tokenized_segment']
            predicted_ids = predictions[i]
            reconstructed = self._processor.pred_labels_to_tokens(tokens, predicted_ids, id2label)
            predicted_tokens.append(reconstructed)

        print("Predictions finalized")

        dataframe['predicted_tokens'] = predicted_tokens
        dataframe['predicted_terms'] = dataframe['predicted_tokens'].apply(self._processor.merge_tokens)

        #check
        # dataframe.to_csv('./evaluation_dataframe.csv', index=False)

        predicted_terms = dataframe['predicted_terms'].tolist()
        predicted_terms = self._processor.flatten_list(predicted_terms)

        candidate_terms = []
        term_counts = Counter(predicted_terms)
        term_counts = dict(sorted(term_counts.items(), key=lambda item: item[1], reverse=True))

        for term, count in term_counts.items():
            n = len(term.split(" "))
            candidate_terms.append((term, n, "count", count))

        return Results(tokens=tokens_output, 
                       terms=candidate_terms), tokenized_corpus_for_sqlite   
    
