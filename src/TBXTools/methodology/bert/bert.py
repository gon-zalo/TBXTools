from ..base import BaseExtractor
from ...results import Results
import nltk

class BertExtractor(BaseExtractor):

    def __init__(self, model, labels):
        from transformers import AutoTokenizer

        # self.biobert = 'dmis-lab/biobert-base-cased-v1.2'
        self.model = model

        self.tokenizer = AutoTokenizer.from_pretrained(self.model, max_length=512, force_download=False, do_lower_case=False)

        self.labels = labels.lower()
        self.extractor_info = "bert"
        self._processor = None
        
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
    
    # def _tokenize(self, segments):
    #     data = []
    #     for segment in segments:
    #         tokenized_segment = self.tokenizer(segment)
    #         data.append(tokenized_segment)

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

    def extract(self, segments, verbose): 
        # get data
        # get terms
        # annotate data
        # fine tune model
        # use the model for predictions

        tokensFD = nltk.probability.FreqDist()
        tokenized_corpus = []
        token_ids = []
        for segment in segments:
            tokens = self.tokenizer.tokenize(segment)
            tokenized_corpus.append(tokens)
            for token in tokens:
                tokensFD[token] += 1

        tokens_output = []
        for token, freq in tokensFD.most_common():
            tokens_row = (token, freq)
            tokens_output.append(tokens_row)


        # print(tokens_output)
        return Results(tokens=tokens_output, extractor_info=self.extractor_info)

    def tag(self, labels):
        pass