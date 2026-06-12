from ..base import BaseExtractor
from ...results import Results
import nltk
from transformers import logging
from collections import Counter

logging.set_verbosity_error()

class BertExtractor(BaseExtractor):

    def __init__(self, model, labels=None, external_terms=None):
        from transformers import AutoTokenizer, BertForTokenClassification, DataCollatorForTokenClassification, Trainer

        self.model_name = model
        self.model = BertForTokenClassification.from_pretrained(self.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, max_length=512, force_download=False, do_lower_case=False)
        self.data_collator = DataCollatorForTokenClassification(tokenizer=self.tokenizer)
        self.trainer = Trainer(model=self.model, data_collator=self.data_collator)

        self.external_terms = external_terms
        self.stop_words = None
        self.labels = labels.lower() if labels else None
        self.extractor_info = "bert"
        self._processor = None
        
    def extract(self, segments, verbose):
        from datasets import Dataset
        import numpy as np
        print("Methodology: BERT")
        tokens_output, tokenized_corpus, dataframe = self.preprocess(segments=segments, verbose=verbose)

        labels = self._choose_labels(self.labels)
        label2id = {l: i for i, l in enumerate(labels)}
        id2label = {i: l for l, i in label2id.items()}

        # need to check this nonsense
        eval_hf = Dataset.from_pandas(dataframe)
        prepared_data = self.prepare_data(self.tokenizer)
        eval_data = eval_hf.map(prepared_data, batched=True)

        # df = eval_data.to_pandas()
        # print(df.head())
        # df.to_csv("ins.csv", index=False)

        print("Predicting terms")
        trainer = self.trainer
        prediction_logits, _, _ = trainer.predict(eval_data)
        predictions = np.argmax(prediction_logits, axis=2)

        predicted_tokens = []
        for i in range(len(eval_data)):
            tokens = eval_data[i]['tokenized_segment']
            predicted_ids = predictions[i]
            reconstructed = self.pred_labels_to_tokens(tokens, predicted_ids, id2label)
            predicted_tokens.append(reconstructed)

        print("Predictions finalized")

        dataframe['predicted_tokens'] = predicted_tokens
        dataframe['predicted_terms'] = dataframe['predicted_tokens'].apply(self._merge_tokens)

        #check
        # dataframe.to_csv('./evaluation_dataframe.csv', index=False)

        predicted_terms = dataframe['predicted_terms'].tolist()
        predicted_terms = self._flatten_list(predicted_terms)

        candidate_terms = []
        term_counts = Counter(predicted_terms)
        term_counts = dict(sorted(term_counts.items(), key=lambda item: item[1], reverse=True))

        for term, count in term_counts.items():
            n = len(term.split(" "))
            candidate_terms.append((term, n, "count", count))

        return Results(tokens=tokens_output, extractor_info=self.extractor_info, terms=candidate_terms, tokenized_corpus=tokenized_corpus)    
    
    def _flatten_list(self, list_of_lists): # needed for bio_tag

        output = [token for sublist in list_of_lists for token in sublist]
        return output

    def _bio_tag(self, text, tokenizer, terms=None, external_terms=None): # tokenizes and tags data

        tokenized_text = []
        token_ids = self.tokenizer(text)
        tokens = self.tokenizer.convert_ids_to_tokens(token_ids["input_ids"])
        tokenized_text.append(tokens)

        tokenized_text = self._flatten_list(tokenized_text)

        if terms:
            # tokenizing terms in terms column
            tokenized_terms = []
            for term in terms:
                tokenized_terms.append(tokenizer.tokenize(term))

            if external_terms is not None: 
                all_terms = tokenized_terms + external_terms
            else:
                all_terms = tokenized_terms
            
            all_terms  = sorted(all_terms, reverse=True, key=len) # sorting by length in descending order

            # initializing labels
            bio_labels = ["O"] * len(tokenized_text)
            n_tokens_in_sent = len(tokenized_text)

            # tagging abstracts
            for term in all_terms:

                tokens_in_term = len(term)
            
                for start_idx in range(n_tokens_in_sent - tokens_in_term + 1):

                    # window to check tokens
                    token_window = tokenized_text[start_idx:start_idx + tokens_in_term]

                    # comparing terms with what's found in token window that's going through the tokenized_text
                    if token_window == term and bio_labels[start_idx] == "O":

                        bio_labels[start_idx] = "B" # tagging the match with a B

                        for remaining_tokens in range(1, tokens_in_term): # label remaining tokens in the term
                            bio_labels[start_idx + remaining_tokens] = "I"

            bio_labels = bio_labels

            return tokenized_text, tokenized_terms, bio_labels
        
        else:
            return tokenized_text

    def _tokenize_terms(self, terms):
        tokenized_terms = []
        for term in terms:
            tokenized_terms.append(self.tokenizer.tokenize(term))

        return tokenized_terms

    def _merge_tokens(self, predicted_terms):
        import re
        import pandas as pd
        stop_words = []

        merged_terms = []

        for token in predicted_terms:
            if token in ['[SEP]', '[UNK]', '[CLS]']: # handling special tokens and UNK
                continue

            # handle bert tokenization
            token = token.replace(" ##", "")
            if token.startswith('##'):
                token = token[2:]

            # handle apostrohpes
            token = re.sub(r"(\w)\s+'\s+(\w)", r"\1' \2", token)
            token = re.sub(r"'\s+.\W", r"'s ", token)

            # handle parentheses
            token = re.sub(r"\(\s+", "(", token)
            token = re.sub(r"\s+\)", ")", token)
            token = re.sub(r"\[\s+", "[", token)
            token = re.sub(r"\s+\]", "]", token)

            # handle hyphenation
            token = re.sub(r"\s*-\s*", "-", token)
            token = re.sub(r"\s*_\s*", "_", token)

            # handle more stuff
            token = re.sub(r"\s+\.\s+", ". ", token) # e. coli
            token = re.sub(r"\s+\/\s+", "/", token)
            token = re.sub(r"\s+\+\s+", "+ ", token)
            token = re.sub(r'(.{2})\s+\+\s+(.{2})', '\1+\2', token) #V1+V2
            token = re.sub(r"\s+,\s+", ", ", token)

            # handling incorrect tokenization
            if token.endswith(')') and not token.startswith('('):
                token = '(' + token
            
            token = re.sub(r"\[UNK]", "", token)
            token = re.sub(r"\[SEP]", "", token)
            token = token.strip()

            if token.lower() in stop_words or token == "" or len(token) == 1: # might want to remove len(token) == 1
                continue

            merged_terms.append(token)
            
        return merged_terms

    def _choose_labels(self, labels):
        if not labels: # default
            return ['O', 'B', 'I']
            
        if labels == "bio":
            return ['O', 'B', 'I']

    def preprocess(self, segments, verbose):
        import pandas as pd
        tokensFD = nltk.probability.FreqDist()
        tokenized_segments = []

        for segment in segments:
            tokenization_table = self.tokenizer(segment)
            tokens = self.tokenizer.convert_ids_to_tokens(tokenization_table["input_ids"])

            tokenized_segments.append(tokens)

            for token in tokens:
                tokensFD[token] += 1

        # print(tokenized_segments)
        tokens_output = []
        for token, freq in tokensFD.most_common():
            tokens_row = (token, freq)
            tokens_output.append(tokens_row)

        tokenized_corpus_for_sqlite = [(" ".join(segment),) for segment in tokenized_segments] #list to str to introduce in sqlite

        # tokenized_corpus_for_dataframe = [" ".join(segment) for segment in tokenized_segments]

        data = {"segment": pd.Series(segments), "tokenized_segment": pd.Series(tokenized_segments)}
        dataframe = pd.DataFrame(data=data)

        return tokens_output, tokenized_corpus_for_sqlite, dataframe

    def prepare_data(self, tokenizer):
        def prepare_unlabeled_inputs(batch): # same func as above without labels

            max_length = 512
            input_ids = []
            attention_masks = []

            for tokens in batch['tokenized_segment']:
                # tokens = tokens.split(" ")

                tokens = tokens[:max_length]

                pad_length = max_length - len(tokens)
                tokens += ['[PAD]'] * pad_length
                # tokens to input ids
                input_ids.append(tokenizer.convert_tokens_to_ids(tokens))

                # attention mask
                attention_masks.append([1 if token != '[PAD]' else 0 for token in tokens])

            batch['input_ids'] = input_ids
            batch['attention_mask'] = attention_masks

            return batch
        return prepare_unlabeled_inputs

    def pred_labels_to_tokens(self, tokens, predicted_ids, id2label): # predicted labels to tokens func
        reconstructed_tokens = []
        current_term = []

        for token, pred_id in zip(tokens, predicted_ids):
            
            label = id2label[pred_id]
        
            if label == 'B':
                if current_term:
                    reconstructed_tokens.append(' '.join(current_term))
                current_term = [token]
            elif label == 'I':
                if current_term: # append I term if there is a B term
                    current_term.append(token)
                else: # if there is no B, treat it as B
                    current_term = [token]
            elif label == 'O': # if there is a B/BI sequence then end it, else dont add it to the current term
                if current_term:
                    reconstructed_tokens.append(' '.join(current_term))
                current_term = []

        if current_term:
            reconstructed_tokens.append(' '.join(current_term))

        return reconstructed_tokens
