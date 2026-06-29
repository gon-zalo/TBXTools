class BertProcessor():

    def __init__(self, model_name):
        self.model_name = model_name
        
        self.model = None
        self.tokenizer = None
        self.data_collator = None
        self.trainer = None

        self.labels = None
    
    def load_transformers(self):
        from transformers import AutoTokenizer, BertForTokenClassification, DataCollatorForTokenClassification, Trainer

        self.model = BertForTokenClassification.from_pretrained(self.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, max_length=512, force_download=False, do_lower_case=False)
        self.data_collator = DataCollatorForTokenClassification(tokenizer=self.tokenizer)
        self.trainer = Trainer(model=self.model, data_collator=self.data_collator)

    def flatten_list(self, list_of_lists): # needed for bio_tag

        output = [element for sublist in list_of_lists for element in sublist]
        return output

    def bio_tag(self, tokenized_segment, tokenized_terms): # annotates data
        # initializing labels
        bio_labels = ["O"] * len(tokenized_segment)
        n_tokens_in_segment = len(tokenized_segment)

        # tagging abstracts
        for term in tokenized_terms:

            tokens_in_term = len(term)
        
            for start_idx in range(n_tokens_in_segment - tokens_in_term + 1):

                # window to check tokens
                token_window = tokenized_segment[start_idx:start_idx + tokens_in_term]

                # comparing terms with what's found in token window that's going through the tokenized_text
                if token_window == term and bio_labels[start_idx] == "O":

                    bio_labels[start_idx] = "B" # tagging the match with a B

                    for remaining_tokens in range(1, tokens_in_term): # label remaining tokens in the term
                        bio_labels[start_idx + remaining_tokens] = "I"

        return bio_labels

    def tokenize_terms(self, external_terms):
        tokenized_terms = []
        for term in external_terms:
            tokenized_terms.append(self.tokenizer.tokenize(term))

        tokenized_terms = sorted(tokenized_terms, reverse=True, key=len) # sorting by length in descending order

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

    def preprocess(self, segments, verbose=False):
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

        # tokenized_corpus_for_sqlite = [" ".join(segment) for segment in tokenized_segments] #list to str to introduce in sqlite

        data = {"tokenized_segment": pd.Series(tokenized_segments)}
        dataframe = pd.DataFrame(data=data)

        return tokens_output, tokenized_segments, dataframe

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
    def prepare_pretokenized_inputs(self, batch):

        bio_labels = ['O', 'B', 'I']
        label2id = {l: i for i, l in enumerate(bio_labels)}
        id2label = {i: l for l, i in label2id.items()}

        max_length = 512
        input_ids = []
        attention_masks = []
        labels = []

        for tokenized_segment, segment_labels in zip(batch['tokenized_segment'], batch['segment_labels']):

            tokenized_segment = tokenized_segment[:max_length]
            segment_labels = segment_labels[:max_length]

            pad_length = max_length - len(tokenized_segment)
            tokenized_segment += ['[PAD]'] * pad_length
            segment_labels += [-100] * pad_length

            # tokens to input ids
            input_ids.append(self.tokenizer.convert_tokens_to_ids(tokenized_segment))

            # attention mask
            attention_masks.append([1 if token != '[PAD]' else 0 for token in tokenized_segment])

            # bio labels to ids
            ignore_tokens = {"[CLS]", "[SEP]", "[PAD]"}

            num_labels = []
            for token, label in zip(tokenized_segment, segment_labels):
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