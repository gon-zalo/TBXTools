from transformers import AutoTokenizer
# from .base import BaseExtractor

class BertExtractor:

    def __init__(self, model=None, tokenizer=None, external_terms=None, lr=None, batch_size=None, epochs=None, weight_decay=None):
        self.model = model or 'distilbert/distilbert-base-uncased'
        self.tokenizer = tokenizer or AutoTokenizer.from_pretrained(model, max_length=512, force_download=True, do_lower_case=False)
        self.external_terms = external_terms

        self.lr = lr or 5e-05 # learning rate
        self.batch_size = batch_size or 16
        self.epochs = epochs or 3
        self.weight_decay = weight_decay or 0.03
        self.tokens = None
        self.labels = None
        
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

    def _merge_tokens(predicted_terms):
        import re
        import pandas as pd
        stop_words = pd.read_table('./ATE_BERT/resources/stop-eng.txt', header=None)
        stop_words = stop_words[0].tolist()
        stop_words = set(stop_words)

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

    def _train(self):
        pass

    def _preprocess(self, text, external_terms):
        tokenized_external_terms = self._tokenize_terms(external_terms)

    def extract(self, segments): 
        # from datasets import Dataset
        # from transformers import BertTokenizer, Trainer, BertForTokenClassification, DataCollatorForTokenClassification


        for segment in segments[:5]:
            print(segment)