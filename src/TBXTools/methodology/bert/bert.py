from ..base import BaseMethodology
from ...results import Results
from ...processor.bert import BertProcessor
import nltk
from transformers import logging
from collections import Counter

logging.set_verbosity_error()

class BertMethodology(BaseMethodology):

    def __init__(self, model, labels=None, external_terms=None):
        from transformers import AutoTokenizer, BertForTokenClassification, DataCollatorForTokenClassification, Trainer

        self.name = "BertMethodology"
        self.model_name = model

        self.processor = BertProcessor(model_name=self.model_name)

        self.external_terms = external_terms
        self.labels = labels.lower() if labels else None

        
    def extract(self, segments, verbose):
        from datasets import Dataset
        import numpy as np

        tokens_output, tokenized_corpus, dataframe = self.processor.preprocess(segments=segments, verbose=verbose)

        labels = self.processor.choose_labels(self.labels)
        label2id = {l: i for i, l in enumerate(labels)}
        id2label = {i: l for l, i in label2id.items()}

        # need to check this nonsense
        eval_hf = Dataset.from_pandas(dataframe)
        prepared_data = self.processor.prepare_data(self.processor.tokenizer)
        eval_data = eval_hf.map(prepared_data, batched=True)

        # df = eval_data.to_pandas()
        # print(df.head())
        # df.to_csv("ins.csv", index=False)

        print("Predicting terms")
        trainer = self.processor.trainer
        prediction_logits, _, _ = trainer.predict(eval_data)
        predictions = np.argmax(prediction_logits, axis=2)

        predicted_tokens = []
        for i in range(len(eval_data)):
            tokens = eval_data[i]['tokenized_segment']
            predicted_ids = predictions[i]
            reconstructed = self.processor.pred_labels_to_tokens(tokens, predicted_ids, id2label)
            predicted_tokens.append(reconstructed)

        print("Predictions finalized")

        dataframe['predicted_tokens'] = predicted_tokens
        dataframe['predicted_terms'] = dataframe['predicted_tokens'].apply(self.processor.merge_tokens)

        #check
        # dataframe.to_csv('./evaluation_dataframe.csv', index=False)

        predicted_terms = dataframe['predicted_terms'].tolist()
        predicted_terms = self.processor.flatten_list(predicted_terms)

        candidate_terms = []
        term_counts = Counter(predicted_terms)
        term_counts = dict(sorted(term_counts.items(), key=lambda item: item[1], reverse=True))

        for term, count in term_counts.items():
            n = len(term.split(" "))
            candidate_terms.append((term, n, "count", count))

        return Results(tokens=tokens_output, 
                       terms=candidate_terms), tokenized_corpus   
    
