import pandas as pd

class BertProcessor():

    def __init__(self, model_name):
        self.model_name = model_name
        self.stopwords = None
        self.inner_stopwords = None
        self._lang_code = None

        self.model = None
        self.tokenizer = None
        self.data_collator = None
        self.trainer = None
        self.labels = None
    
    def load_transformers(self):
        from transformers import AutoTokenizer, BertForTokenClassification, DataCollatorForTokenClassification, Trainer

        self.model = BertForTokenClassification.from_pretrained(self.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, max_length=512, force_download=False, do_lower_case=False, use_fast=True)
        self.data_collator = DataCollatorForTokenClassification(tokenizer=self.tokenizer)
        self.trainer = Trainer(model=self.model, data_collator=self.data_collator)

    def choose_labels(self, labels):
        if not labels: # default
            return ['O', 'B', 'I']
            
        if labels == "bio":
            return ['O', 'B', 'I']

    def annotate(self, tokenized_segment, tokenized_terms):
        # initializing labels
        labels = ["O"] * len(tokenized_segment)
        n_tokens_in_segment = len(tokenized_segment)

        # tagging abstracts
        for term in tokenized_terms:
            term_tokens = term["tokens"]
            term_labels = term["labels"]

            tokens_in_term = len(term_tokens)
        
            for start_idx in range(n_tokens_in_segment - tokens_in_term + 1):
                
                token_window = tokenized_segment[start_idx:start_idx + tokens_in_term]

                if token_window == term_tokens and labels[start_idx] == "O":

                    labels[start_idx:start_idx + tokens_in_term] = term_labels

        return labels
    
    def tokenize_and_tag_terms(self, external_terms, expand_labels=True):
        tokenized_terms = []

        for term in external_terms:
            labels = []

            if expand_labels: # expand B tags accordingly
                tokens = []
                subwords = term.split()

                for i, subword in enumerate(subwords):
                    encoding = self.tokenizer(subword, add_special_tokens=False,)
                    pieces = self.tokenizer.convert_ids_to_tokens(encoding["input_ids"][0])
                    tokens.extend(pieces)

                    if i == 0:
                        labels.extend(["B"] * len(pieces))
                    else:
                        labels.extend(["I"] * len(pieces))

            if not expand_labels: # only tag with B the first subword, i.e. the start of the term
                encoding = self.tokenizer(term, add_special_tokens=False)
                tokens = self.tokenizer.convert_ids_to_tokens(encoding["input_ids"][0])

                for i, token in enumerate(tokens):

                    if i == 0:
                        labels.append("B")
                    else:
                        labels.append("I")

            tokenized_terms.append({
                "tokens": tokens,
                "labels": labels})

        tokenized_terms.sort(key=lambda x: len(x["tokens"]), reverse=True) # sorting by length in descending order

        return tokenized_terms

    def merge_predictions(self, text, tokens, predictions, offsets):

        entities = []
        current_start = None
        current_end = None

        for token, label, offset in zip(tokens, predictions, offsets):

            start, end = offset

            # Ignore special tokens ([CLS], [SEP], padding)
            if start == end:
                continue

            if label == "B":
                # Save previous entity if one exists
                if current_start is not None:
                    entities.append(text[current_start:current_end])

                # Start new entity
                current_start = start
                current_end = end

            elif label == "I":
                # Continue current entity
                if current_start is not None:
                    current_end = end

            else:  # O
                if current_start is not None:
                    entities.append(text[current_start:current_end])

                    current_start = None
                    current_end = None

        # Catch entity at the end
        if current_start is not None:
            entities.append(text[current_start:current_end])

        return entities

    # this tokenization can be better with encoding
    def old_preprocess(self, segments, verbose=False):
        import nltk
        tokensFD = nltk.probability.FreqDist()
        tokenized_segments = []
        offset_mappings = []
        for segment in segments:
            tokenization_table = self.tokenizer(segment, return_offsets_mapping=True) # add offsets for token reconstruction, THIS IS ONLY FOR EVALUATION, NEED TO SPLIT THIS PREPROCESSING IN TWO
            tokens = self.tokenizer.convert_ids_to_tokens(tokenization_table["input_ids"])
            offsets = tokenization_table["offset_mapping"]

            tokenized_segments.append(tokens)
            offset_mappings.append(offsets)

            for token in tokens:
                tokensFD[token] += 1

        tokens_output = []
        for token, freq in tokensFD.most_common():
            tokens_row = (token, freq)
            tokens_output.append(tokens_row)

        data = {"tokenized_segments": pd.Series(tokenized_segments),
                "offset_mapping": pd.Series(offset_mappings),
                "text": pd.Series(segments)}
        
        dataframe = pd.DataFrame(data=data)

        return tokens_output, dataframe

    def _preprocess(self, segments, verbose=False):
        import nltk

        tokensFD = nltk.probability.FreqDist()

        encoding = self.tokenizer(
            segments,
            truncation=True,
            padding="max_length",
            max_length=512,
            return_offsets_mapping=True)

        input_ids = encoding["input_ids"]
        attention_masks = encoding["attention_mask"]
        offset_mappings = encoding["offset_mapping"]

        tokenized_segments = self.tokenize_segments(encoding)
        tokens_FD = self.calculate_tokens_FD(tokenized_segments)

        # for tokens in tokenized_segments:
        #     tokensFD.update(tokens)
        # tokens_output = list(tokensFD.most_common())

        dataframe = pd.DataFrame({
            "text": segments,
            "tokenized_segments": tokenized_segments,
            "input_ids": input_ids,
            "attention_mask": attention_masks,
            "offset_mapping": offset_mappings,
        })

        return tokens_FD, dataframe

    def preprocess_train(self, segments):
        encoding = self._encode(segments, return_offsets=True, return_tokens=True)

        tokens_FD = self.calculate_tokens_FD(encoding["tokenized_segments"])

        df = pd.DataFrame({
            "text": segments,
            "tokens": encoding["tokenized_segments"],
            "input_ids": encoding["input_ids"],
            "attention_mask": encoding["attention_mask"],
            "offset_mapping": encoding["offset_mapping"]})

        return tokens_FD, df
    
    def tokenize_segments(self, encoding_data):
        tokenized_segments = []
        for ids in encoding_data["input_ids"]:
            tokenized_segments.append(self.tokenizer.convert_ids_to_tokens(ids))

        return tokenized_segments
    
    def calculate_tokens_FD(self, tokenized_segments):
        import nltk

        tokensFD = nltk.probability.FreqDist()
        
        for tokens in tokenized_segments:
            tokensFD.update(tokens)

        tokens_output = list(tokensFD.most_common())

        return tokens_output

    def preprocess_eval(self, segments):
        encoding = self._encode(segments, return_offsets=True, return_tokens=True)

        df = pd.DataFrame({
            "text": segments,
            "input_ids": encoding["input_ids"],
            "attention_mask": encoding["attention_mask"],
            "tokenized_segments": encoding["tokenized_segments"],
            "offset_mapping": encoding["offset_mapping"]})

        return df
    
    def _encode(self, segments, return_offsets=False, return_tokens=False):
        encoding = self.tokenizer(
            segments,
            truncation=True,
            padding="max_length",
            max_length=512,
            return_offsets_mapping=return_offsets,
        )

        if return_tokens:
            encoding["tokenized_segments"] = [
                self.tokenizer.convert_ids_to_tokens(ids)
                for ids in encoding["input_ids"]
            ]

        return encoding

    def pred_labels_to_text(self, text, offsets, predicted_ids, id2label):
        entities = []
        start = None
        end = None

        for offset, pred_id in zip(offsets, predicted_ids):

            token_start, token_end = offset
            # ignore PAD
            if pred_id == -100:
                continue

            label = id2label[pred_id]

            # ignore CLS SEP
            if token_start == token_end:
                continue

            if label == "B":
                # also taking into account subwords with B tag
                if start is not None and token_start == end:
                    end = token_end

                else:
                    if start is not None:
                        entities.append(text[start:end])
                    start = token_start
                    end = token_end

            elif label == "I":
                if start is not None:
                    end = token_end

            else:  # 0 tag
                if start is not None:
                    entities.append(text[start:end])

                start = None
                end = None

        if start is not None:
            entities.append(text[start:end])

        return entities

    #
    def prepare_unlabeled_inputs(self, batch):
        max_length = 512
        input_ids = []
        attention_masks = []

        for tokens in batch['tokenized_segments']:
            # tokens = tokens.split(" ")

            tokens = tokens[:max_length]

            pad_length = max_length - len(tokens)
            tokens += ['[PAD]'] * pad_length
            # tokens to input ids
            input_ids.append(self.tokenizer.convert_tokens_to_ids(tokens))

            # attention mask
            attention_masks.append([1 if token != '[PAD]' else 0 for token in tokens])

        batch['input_ids'] = input_ids
        batch['attention_mask'] = attention_masks

        return batch

    def prepare_pretokenized_inputs(self, batch):

        bio_labels = ['O', 'B', 'I']
        label2id = {l: i for i, l in enumerate(bio_labels)}
        id2label = {i: l for l, i in label2id.items()}

        max_length = 512
        input_ids = []
        attention_masks = []
        labels = []

        for tokenized_segment, segment_labels in zip(batch['tokenized_segments'], batch['segment_labels']):

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

##########################

    def _old_bio_tag(self, tokenized_segment, tokenized_terms): # annotates data
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
    
    def old_tokenize_terms(self, external_terms):
        tokenized_terms = []
        for term in external_terms:
            tokenized_terms.append(self.tokenizer.tokenize(term))

        tokenized_terms = sorted(tokenized_terms, reverse=True, key=len) # sorting by length in descending order

        return tokenized_terms
    
    def merge_tokens(self, predicted_terms):
        # a mess that works but could be optimized
        import re

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

            if token.lower() in self.stopwords or token == "" or len(token) == 1: # might want to remove len(token) == 1
                continue

            merged_terms.append(token)
            
        return merged_terms
    

        # works with BIO labels, will need to expand if another labels are used
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