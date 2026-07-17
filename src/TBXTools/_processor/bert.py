import pandas as pd
from tqdm import tqdm
from .._utils.utils import get_model_from_code

class BertProcessor():

    def __init__(self, model_name, labels):
        self.model_name = model_name
        self.stopwords = None
        self.inner_stopwords = None
        self._lang_code = None

        self.model = None
        self.tokenizer = None
        self.data_collator = None
        self.trainer = None
        self.labels = labels
        self._labeling_scheme = None
        self._label2id = None
        self._id2label = None

        self.trie_root = None
        self.tokenized_terms = None

        self.choose_labels()

    def _load_model(self):
        from transformers import BertForTokenClassification
        import torch
        device = torch.device("cuda")

        self.model = BertForTokenClassification.from_pretrained(
            self.model_name,
            num_labels=len(self._labeling_scheme),
            id2label=self._id2label,
            label2id=self._label2id).to(device)
        
    def _load_tokenizer_and_data_collator(self):
        from transformers import AutoTokenizer, DataCollatorForTokenClassification

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, max_length=512, force_download=False, do_lower_case=False, use_fast=True)

        self.data_collator = DataCollatorForTokenClassification(tokenizer=self.tokenizer)

        # self.trainer = Trainer(model=self.model, data_collator=self.data_collator)

    def _model_init(self): #unify with _load_model
        from transformers import BertForTokenClassification
        import torch
        device = torch.device("cuda")
        print(f"Loading model {self.model_name}", flush=True)
        return BertForTokenClassification.from_pretrained(self.model_name, num_labels=len(self._labeling_scheme), id2label=self._id2label, label2id=self._label2id).to(device)
    
    def choose_labels(self):

        if not self.labels: # default
            self.labels = "BIO"
            self._labeling_scheme = ['O', 'B', 'I']

        elif self.labels.lower() == "bio":
            self.labels = "BIO"
            self._labeling_scheme = ['O', 'B', 'I']

        elif self.labels.lower() == "bilou":
            self.labels = "BILOU"
            self._labeling_scheme = ['O', 'B', 'I', 'L', 'U']

        else:
            raise RuntimeError(f"{self.labels.upper()} labels not supported. Current labeling schemes supported: BIO, BILOU.")

        self._label2id = {l: i for i, l in enumerate(self._labeling_scheme)}
        self._id2label = {i: l for l, i in self._label2id.items()}
            
    def preprocess_train(self, df, expand_labels=False, balanced_dataset_size=None, dataset_negative_ratio=None):
        encoding = self._encode(
            df["word_tokens"].tolist(),
            return_offsets=False,
            is_split_into_words=True)
        
        tokenized_segments = self._tokenize_segments(encoding) # with bert

        df["tokens"] = tokenized_segments
        df["input_ids"] = encoding["input_ids"]
        df["attention_mask"] = encoding["attention_mask"]

        tokens_FD = self._calculate_tokens_FD(df["tokens"])

        df["labels"] = self._align_labels(encoding, df["labels"].tolist(), is_split_into_words=True, expand_labels=expand_labels)

        df = self._build_balanced_dataset(dataframe=df,target_size=balanced_dataset_size, negative_ratio=dataset_negative_ratio)

        df["labels"] = self._transform_labels_into_ints(df["labels"])

        return tokens_FD, df
    
    def annotate_data(self, segments, external_terms):
        import spacy
        spacy_model = get_model_from_code(self.lang_code)
        nlp = spacy.load(spacy_model)

        word_tokens, lemmas = self._lemmatize_segments(nlp, segments) # with spacy

        tagged_terms = self._lemmatize_and_tag_terms(nlp, external_terms=external_terms)

        df = pd.DataFrame({
            "text": segments,
            "word_tokens": word_tokens, 
            "lemmas": lemmas})

        df["labels"] = self._annotate(df["lemmas"], tokenized_terms=tagged_terms)

        return df

    def preprocess_eval(self, segments, lemmatize=False):
        if not lemmatize:
            encoding = self._encode(segments, return_offsets=True, is_split_into_words=False)

            tokenized_segments = self._tokenize_segments(encoding)

            df = pd.DataFrame({
                "text": segments,
                "tokens": tokenized_segments,
                "input_ids": encoding["input_ids"],
                "attention_mask": encoding["attention_mask"],
                "offset_mapping": encoding["offset_mapping"]
                })

        if lemmatize:
            import spacy
            spacy_model = get_model_from_code(self.lang_code)
            nlp = spacy.load(spacy_model)

            # nlp = spacy.load("en_core_web_sm")

            seg_tokens = self._tokenize_segments(nlp, segments)

            encoding = self._encode(seg_tokens, return_offsets=False, is_split_into_words=True)
            df = pd.DataFrame({
                "tokens": seg_tokens,
                "input_ids": encoding["input_ids"],
                "attention_mask": encoding["attention_mask"]
                })

        return df
    
    # unify with preprocess_train
    def preprocess_annotated(self, df, expand_labels=False):
        encoding = self._encode(
            df["word_tokens"].tolist(),
            return_offsets=False,
            is_split_into_words=True)

        tokenized_segments = self._tokenize_segments(encoding) # with bert
        
        df["tokens"] = tokenized_segments
        df["input_ids"] = encoding["input_ids"]
        df["attention_mask"] = encoding["attention_mask"]

        df["labels"] = self._align_labels(encoding, df["labels"].tolist(), is_split_into_words=True, expand_labels=expand_labels)

        df = self._build_balanced_dataset(dataframe=df,target_size=30000, negative_ratio=0.15)

        df["labels"] = self._transform_labels_into_ints(df["labels"])

        return df
            
    def _encode(self, segments, return_offsets=False, is_split_into_words=False):
        encoding = self.tokenizer(
            segments,
            is_split_into_words=is_split_into_words,
            truncation=True,
            padding="max_length",
            max_length=512,
            return_offsets_mapping=return_offsets)

        return encoding
    
    def process_predictions(self, predicted_candidates):
        '''Light postprocessing that removes terms that contain stopwords at the beginning or end. Terms that are solely quotation marks ("") are also removed.
        
        The function takes a list of lists of terms.'''
        clean_terms = []

        for list_of_terms in predicted_candidates:
            cleaned = []
            for term in list_of_terms:

                if all(char == '"' for char in term):
                    continue

                split_term = term.lower().split()

                if split_term[0] in self.stopwords or split_term[-1] in self.stopwords:
                    continue
                
                else:
                    cleaned.append(term)

            clean_terms.append(cleaned)

        return clean_terms
    
    def _annotate(self, tokenized_segments, tokenized_terms):
        print(f"\nStarting segment annotation", flush=True)
        terms_by_len = self._order_terms_by_len(tokenized_terms)
        # use with bpe tokenizers
        # self._processor.tokenized_terms = tokenized_terms
        labels = []

        for tokenized_segment in tqdm(tokenized_segments, 
                            desc=f"Annotating segments with {self.labels} labels", total=len(tokenized_segments)):

            # unaligned labels fix
            segment = [token for token in tokenized_segment if token not in ["[CLS]", "[SEP]", "[PAD]"]]

            segment_labels = ["O"] * len(segment)

            for length, terms in terms_by_len.items():
            # for length, terms in terms_by_len:

                # if terms length is longer than n tokens in segment skip
                if length > len(segment):
                    continue

                max_start = len(segment) - length + 1

                for start_idx in range(max_start):

                    # if already labelled
                    if segment_labels[start_idx] != "O":
                        continue

                    for term in terms:
                        term_tokens = term["tokens"]
                        # if first element is not the same as the first token of term, skip
                        if segment[start_idx] != term_tokens[0]:
                            continue
                        
                        # better than slicing like previously
                        match = True
                        for num in range(length):
                            if segment[start_idx + num] != term_tokens[num].lower():
                                match = False
                                break

                        if match:
                            segment_labels[start_idx:start_idx + length] = term["labels"]

            labels.append(segment_labels)

        return labels

    def _build_balanced_dataset(self, dataframe, target_size=30000, negative_ratio=0.15):
            
        print(f"\nBuilding a dataset of {target_size} segments with {negative_ratio * 100}% negative examples from a dataframe of {len(dataframe)} segments", flush=True)
        
        # filter
        with_terms = dataframe["labels"].apply(lambda seg_labels: any(label in ["B", "I"] for label in seg_labels))
        
        # 2 dfs, one with terms and another without
        df_with_terms = dataframe[with_terms]
        df_without_terms = dataframe[~with_terms]
        print(f"Total segments with terms: {len(df_with_terms)}")

        if target_size > len(df_with_terms):
            print("\nWARNING: Specified target size is bigger than identified segments with terms.")

            n_segments_with_terms = len(df_with_terms)
            n_negative_examples = int(len(df_with_terms) * negative_ratio)
            n_negative_examples = min(n_negative_examples, len(df_without_terms))

            print(f"Building a dataset of all identified positive examples ({n_segments_with_terms}) and {negative_ratio * 100}% negative examples ({n_negative_examples})")

            df_with_terms = df_with_terms.sample(n=n_segments_with_terms, random_state=123)
            df_without_terms = df_without_terms.sample(n=n_negative_examples, random_state=123)

        else: 
            n_negative_examples = int(target_size * negative_ratio)
            n_segments_with_terms = target_size - n_negative_examples
            
            n_segments_with_terms = min(n_segments_with_terms, len(df_with_terms))
            n_negative_examples = min(n_negative_examples, len(df_without_terms))
            
            df_with_terms = df_with_terms.sample(n=n_segments_with_terms, random_state=123)
            df_without_terms = df_without_terms.sample(n=n_negative_examples, random_state=123)
        
        # concat and merge
        full = pd.concat([df_with_terms, df_without_terms])
        full = full.sample(frac=1, random_state=123).reset_index(drop=True)
        
        print(f"\nRemaining segments with terms:{len(df_with_terms)}")
        print(f"Remaining segments without terms:  {len(df_without_terms)}")
        print(f"Remaining total segments: {len(full)}")
        
        return full

    def _order_terms_by_len(self, tokenized_terms):
        from collections import defaultdict
        terms_by_len = defaultdict(list)

        for term in tokenized_terms:
            length = len(term["tokens"])
            terms_by_len[length].append(term)

        return terms_by_len
    
    def _tokenize_and_tag_terms(self, external_terms, expand_labels=False):
        tokenized_terms = []

        for term in tqdm(external_terms, desc=f"Annotating terms with {self.labels} labels", total=len(external_terms)):
            labels = []

            if expand_labels: # expand B tags accordingly
                tokens = []
                words_in_term = term.split()
                num_words = len(words_in_term)

                for i, word in enumerate(words_in_term):

                    encoding = self.tokenizer(word, add_special_tokens=False)
                    pieces = self.tokenizer.convert_ids_to_tokens(encoding["input_ids"])
                    tokens.extend(pieces)

                    if self.labels == "BIO":
                        if i == 0:
                            labels.extend(["B"] * len(pieces))
                        else:
                            labels.extend(["I"] * len(pieces))

                    elif self.labels == "BILOU":
                        if num_words == 1:
                            labels.extend(["B"] * len(pieces))

                        if i == 0:
                            labels.extend(["U"] * len(pieces))

                        elif i == num_words - 1: # last
                            labels.extend(["L"] * len(pieces))

                        else:
                            labels.extend(["I"] * len(pieces))

            if not expand_labels: # only tag with B the first subword, i.e. the start of the term

                encoding = self.tokenizer(term, add_special_tokens=False)
                tokens = self.tokenizer.convert_ids_to_tokens(encoding["input_ids"])

                for i, token in enumerate(tokens):

                    if self.labels == "BIO":
                        if i == 0:
                            labels = ["B"]
                        else:
                            labels = ["I"]
                
                    elif self.labels == "BILOU":
                        num_of_tokens = len(tokens)
                        
                        if num_of_tokens == 1:
                            labels = ["U"]

                        else:
                            labels = ["B"] + ["I"] * (num_of_tokens - 2) + ["L"]

            tokenized_terms.append({
                "tokens": tokens,
                "labels": labels})

        tokenized_terms.sort(key=lambda x: len(x["tokens"]), reverse=True) # sorting by length in descending order
        
        return tokenized_terms
    
    def _transform_labels_into_ints(self, labels):
        labels_ints = []
        for sequence in labels:
            label_ids = []

            for label in sequence:
                if label == -100:
                    label_ids.append(-100)
                else:
                    label_ids.append(self._label2id[label])

            labels_ints.append(label_ids)

        return labels_ints

    def _lemmatize_and_tag_terms(self, nlp, external_terms):
        term_lemmas = {}

        for term in tqdm(external_terms, desc="Lemmatizing external terms", total=len(external_terms)):

            doc = nlp(term)

            lemmas = [t.lemma_.lower() for t in doc]

            # fix in order to stop tagging things like IS
            if len(lemmas) == 1 and lemmas[0] in self.stopwords:
                continue

            term_lemmas[term] = lemmas

        annotated_terms = []
        for term, lemmas in tqdm(term_lemmas.items(), desc=f"Annotating terms with {self.labels} labels", total=len(term_lemmas)):
            
            num_of_lemmas = len(lemmas) #same logic as in tokenize and tag terms func

            if self.labels == "BILOU":
                if num_of_lemmas == 1:
                    labels = ["U"]
                else:
                    labels = ["B"] + ["I"] * (num_of_lemmas - 2) + ["L"]
                    
            elif self.labels == "BIO":
                labels = ["B"] + ["I"] * (num_of_lemmas - 1)

            annotated_terms.append({
                "tokens": lemmas,
                "labels": labels
            })
            
        annotated_terms.sort(key=lambda x: len(x["tokens"]), reverse=True) # sorting by length in descending order

        return annotated_terms
            
    def _lemmatize_segments(self, nlp, segments):
        # spacy tokenizer/lemmatizer
        tokens_list = []
        lemmas_list = []

        for segment in tqdm(segments, desc="Tokenizing and lemmatizing segments", total=len(segments)):

            doc = nlp(segment)
            tokens = [t.text for t in doc]
            tokens_list.append(tokens)
            lemmas = [t.lemma_.lower() for t in doc]
            lemmas_list.append(lemmas)

        return tokens_list, lemmas_list
    
    def _tokenize_segments(self, encoding_data):
        # bert tokenizer
        tokenized_segments = []
        for ids in encoding_data["input_ids"]:
            tokenized_segments.append(self.tokenizer.convert_ids_to_tokens(ids))

        return tokenized_segments
    
    def _calculate_tokens_FD(self, tokenized_segments):
        import nltk

        tokensFD = nltk.probability.FreqDist()
        
        for tokens in tokenized_segments:
            tokensFD.update(tokens)

        tokens_output = list(tokensFD.most_common())

        return tokens_output

    def _align_labels(self, encoding, unaligned_labels, is_split_into_words=False, expand_labels=False):
        aligned_labels = []

        if is_split_into_words: # if input is pre-tokenized

            for i, labels in enumerate(unaligned_labels):
                word_ids = encoding.word_ids(batch_index=i)
                aligned_segment = []
                previous_word_id = None
                
                for word_id in word_ids:
                    if word_id is None:
                        aligned_segment.append(-100)

                    elif word_id != previous_word_id:
                        aligned_segment.append(labels[word_id])
                    else:

                        label = labels[word_id]
                        
                        if not expand_labels and label.startswith(("B", "L", "U")):
                            aligned_segment.append(label.replace("B", "I", 1)) #for bio tags
                            # aligned_segment.append("I" + label[1:]) # for bilou

                        else: # expanding labels
                            aligned_segment.append(label)
                            
                    previous_word_id = word_id
                        
                aligned_labels.append(aligned_segment)

        else:

            for i, labels in enumerate(unaligned_labels):
                word_ids = encoding.word_ids(batch_index=i)
                
                aligned_segment = []
                label_idx = 0
                
                for word_id in word_ids:
                    if word_id is None:
                        aligned_segment.append(-100)
                    else:
                        if label_idx < len(labels):
                            aligned_segment.append(labels[label_idx])
                            label_idx += 1
                        else:
                            aligned_segment.append(-100)
                            
                aligned_labels.append(aligned_segment)
            
        return aligned_labels

    def _pred_labels_to_text(self, text, offsets, predicted_ids, id2label):
        terms = []
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
                        terms.append(text[start:end])
                    start = token_start
                    end = token_end

            elif label == "I":
                if start is not None:
                    end = token_end

            else:  # 0 tag
                if start is not None:
                    terms.append(text[start:end])

                start = None
                end = None

        if start is not None:
            terms.append(text[start:end])

        return terms
    
    def _bio_to_terms(self, tokens, labels):
        # use with spacy tokenization
        terms = []
        current = []

        for token, label in zip(tokens, labels):
            if label == 1: # B
                if current:
                    terms.append(" ".join(current))
                current = [token]

            elif label == 2 and current:
                current.append(token)

            # elif label == 2:  # I
            #     if current:
            #         current.append(token)
            #     else: # if there is no B token, i.e. I is alone, treat as B?
            #         current = [token]
            
            else: # 0
                if current:
                    terms.append(" ".join(current))
                    current = []

        if current:
            terms.append(" ".join(current))

        return terms
    
    def _flatten_list(self, list_of_lists): #needed for bio_tag_bert

        output = [token for sublist in list_of_lists for token in sublist]
        return output

####
    # to use with herbert (it uses BPE tokenizer not WordPiece)
    def annotate_trie(self, tokenized_segment):
        # move this to BertTrainer inside an if trie=True, create trie once not every loop
        self.trie_root = TrieNode.build_trie(self.tokenized_terms)
        trie_root = self.trie_root
        # -------------------------
        # remove padding
        # -------------------------

    
        try:
            n = tokenized_segment.index("[PAD]")
        except ValueError:
            n = len(tokenized_segment)

        seg = tokenized_segment[:n]
        labels = ["O"] * n

        length = n

        # -------------------------
        # scan each start position
        # -------------------------
        for i in range(length):

            node = trie_root
            j = i

            # walk down trie
            while j < length and seg[j] in node.children:
                node = node.children[seg[j]]

                # found a full term
                if node.term_id is not None:

                    term = self.tokenized_terms[node.term_id]
                    L = len(term["tokens"])

                    # assign BIO labels
                    labels[i:i + L] = term["labels"]

                j += 1

        return labels

class TrieNode:
    def __init__(self):
        self.children = {}
        self.term_id = None  # store index if this is end of a term

    def build_trie(tokenized_terms):
        root = TrieNode()

        for idx, term in enumerate(tokenized_terms):
            node = root

            for tok in term["tokens"]:
                if tok not in node.children:
                    node.children[tok] = TrieNode()
                node = node.children[tok]

            node.term_id = idx

        return root