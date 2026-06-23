class BertProcessor():

    def __init__(self, model_name):
        from transformers import AutoTokenizer, BertForTokenClassification, DataCollatorForTokenClassification, Trainer

        self.model_name = model_name
        
        self.model = BertForTokenClassification.from_pretrained(self.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, max_length=512, force_download=False, do_lower_case=False)
        self.data_collator = DataCollatorForTokenClassification(tokenizer=self.tokenizer)
        self.trainer = Trainer(model=self.model, data_collator=self.data_collator)

        self.labels = None
    
    def flatten_list(self, list_of_lists): # needed for bio_tag

        output = [element for sublist in list_of_lists for element in sublist]
        return output

    def bio_tag(self, text, tokenizer, terms=None, external_terms=None): # tokenizes and tags data

        tokenized_text = []
        token_ids = self.tokenizer(text)
        tokens = self.tokenizer.convert_ids_to_tokens(token_ids["input_ids"])
        tokenized_text.append(tokens)

        tokenized_text = self.flatten_list(tokenized_text)

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

    def tokenize_terms(self, terms):
        tokenized_terms = []
        for term in terms:
            tokenized_terms.append(self.tokenizer.tokenize(term))

        return tokenized_terms

    def merge_tokens(self, predicted_terms):
        import re
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

    def choose_labels(self, labels):
        if not labels: # default
            return ['O', 'B', 'I']
            
        if labels == "bio":
            return ['O', 'B', 'I']

    def preprocess(self, segments, verbose):
        import pandas as pd
        import nltk
        tokensFD = nltk.probability.FreqDist()
        tokenized_segments = []

        for segment in segments:
            tokenization_table = self.tokenizer(segment)
            tokens = self.tokenizer.convert_ids_to_tokens(tokenization_table["input_ids"])

            tokenized_segments.append(tokens)

            for token in tokens:
                tokensFD[token] += 1

        tokens_output = []
        for token, freq in tokensFD.most_common():
            tokens_row = (token, freq)
            tokens_output.append(tokens_row)

        tokenized_corpus_for_sqlite = [" ".join(segment) for segment in tokenized_segments] #list to str to introduce in sqlite

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

# train processing

    def prepare_data(self, data):
        import pandas as pd
        df = pd.read_json(data, orient='records', lines=True)

        return df

    def prepare_pretokenized_inputs(self, batch):
        tokenizer = self.tokenizer

        bio_labels = ['O', 'B', 'I']
        label2id = {l: i for i, l in enumerate(bio_labels)}
        id2label = {i: l for l, i in label2id.items()}

        max_length = 512
        input_ids = []
        attention_masks = []
        labels = []

        for tokens, token_labels in zip(batch['abstract_tokens'], batch['abstract_labels']):

            tokens = tokens[:max_length]
            token_labels = token_labels[:max_length]

            pad_length = max_length - len(tokens)
            tokens += ['[PAD]'] * pad_length
            token_labels += [-100] * pad_length

            # tokens to input ids
            input_ids.append(tokenizer.convert_tokens_to_ids(tokens))

            # attention mask
            attention_masks.append([1 if token != '[PAD]' else 0 for token in tokens])

            # bio labels to ids
            ignore_tokens = {"[CLS]", "[SEP]", "[PAD]"}

            num_labels = []
            for token, label in zip(tokens, token_labels):
                if token in ignore_tokens:
                    num_labels.append(-100)
                elif label == -100:
                    num_labels.append(-100)
                else:
                    numeric_id = label2id.get(label, -100)
                    num_labels.append(numeric_id)

            labels.append(num_labels)

        batch['input_ids'] = input_ids
        batch['attention_mask'] = attention_masks
        batch['labels'] = labels

        return batch

    def prepare_fine_tuning(self, model, external_terms, labels, lr, batch_size, epochs, weight_decay):
        from transformers import Trainer, TrainingArguments, BertForTokenClassification, DataCollatorForTokenClassification, AutoTokenizer, set_seed
        import torch
        from sklearn.model_selection import train_test_split
        from datasets import Dataset
        set_seed(123)


        return model, training_args, data_collator, trainer