from ..base import BaseMethodology
from ..._results.results import Results
from ..._processor.bert import BertProcessor
from collections import Counter
#
class BertMethodology(BaseMethodology):
    '''
    Manages terminology extraction with a BERT model.

    Attributes:
        model (str): Fine-tuned model for terminology extraction using labels.
        labels (str): The labels used in the fine-tuning of the model.
    '''

    def __init__(self, model, labeling_scheme="BIO"):
        from transformers import logging
        logging.set_verbosity_error()
        self.name = "BertMethodology"
        self.model_name = model

        self.labeling_scheme = labeling_scheme.lower()
        self.processor = BertProcessor()
        self.extractor = None

    def run(self, segments, verbose=False):
        '''
        Extracts candidate terms using BERT. This methodology uses a previously fine-tuned model on automatically annotated data to predict terms.

        Args:
            segments: A list of segments to process.
        
        Returns:
            Results: An object containing the tokens, candidate terms. It also returns separately the tokenized corpus.
        '''
        # verbose (bool, optional): If True, enables detailed logging. Defaults to False.
        # by_segment (bool, optional): If True, outputs candidate terms grouped by segment.
        
        from datasets import Dataset
        import numpy as np

        print(f'\nInitializing model:  {self.model_name}', flush=True)
        self.processor.model_name = self.model_name
        self.processor.labeling_scheme = self.labeling_scheme.lower()
        self.processor._load_model()
        self.processor._load_trainer()
        self.processor._load_tokenizer_and_data_collator()

        dataframe = self.processor.preprocess_test(segments=segments)
        eval_data = Dataset.from_pandas(dataframe)

        print("\nPredicting terms")
        trainer = self.processor.trainer
        prediction_logits, _ , _ = trainer.predict(eval_data)
        predictions = np.argmax(prediction_logits, axis=2)
        predicted_terms = []
                
        for i in range(len(eval_data)):
            tokens = eval_data[i]['tokens']
            predicted_ids = predictions[i]
            reconstructed = self.processor._bio_to_terms(
                tokens=tokens,
                labels=predicted_ids)

            predicted_terms.append(reconstructed)

        clean_terms = self.processor.process_predictions(predicted_terms)

        dataframe['predicted_terms'] = clean_terms

        #i dont remember why im doing this, but keep for now, otherwise it wont work
        clean_terms = dataframe['predicted_terms'].tolist()
        clean_terms = self.processor._flatten_list(clean_terms)

        # output for tbxtools, calculating count of each term
        candidate_terms = []
        term_counts = Counter(clean_terms)
        term_counts = dict(sorted(term_counts.items(), key=lambda item: item[1], reverse=True))
        for term, count in term_counts.items():
            if term:
                n = len(term.split(" "))
                candidate_terms.append((term, n, "count", count))
        tokenized_segments = []

        results = Results(terms=candidate_terms)

        self.extractor._sqlite.insert_segments(data=tokenized_segments, tagged=False, tokenized=True)
        # old line, im not inserting tokens rn, need to check
        # self.extractor._sqlite.insert_tokens(data=results._tokens)

        return results