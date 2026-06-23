from ...processor.bert import BertProcessor
class BertTrainer:

    def __init__(self, model=None, corpus=None, external_terms=None, labels=None, lr=None, batch_size=None, epochs=None, weight_decay=None):

        self.model_name = model
        self.model = BertForTokenClassification.from_pretrained(self.model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, max_length=512, force_download=False, do_lower_case=False)
        self.external_terms = external_terms
        self.labels = labels.lower()

        self.lr = lr or 5e-05 # learning rate
        self.batch_size = batch_size or 16
        self.epochs = epochs or 3
        self.weight_decay = weight_decay or 0.03

        self.processor = BertProcessor(model_name=self.model_name)

    def train(self, train_data=None):

        self.processor.prepare_fine_tu

        train_df = self.prepare_data(train_data)
        # train_df = pd.DataFrame(train_data, index=None)

        train_data = Dataset.from_pandas(train_df) # huggingface format
        train_data = train_data.map(self.prepare_pretokenized_inputs, batched=True)

        print(f'\nInitializing model:  {self.model_name}')
        tokenizer = self.tokenizer
        bio_labels = ['O', 'B', 'I']
        label2id = {l: i for i, l in enumerate(bio_labels)}
        id2label = {i: l for l, i in label2id.items()}

        device = torch.device("cuda")
        model = BertForTokenClassification.from_pretrained(
            self.model_name,
            num_labels=len(bio_labels),
            id2label=id2label,
            label2id=label2id).to(device)

        training_args = TrainingArguments(
            eval_strategy="no",
            learning_rate=self.lr,
            per_device_train_batch_size=self.batch_size,
            num_train_epochs=self.epochs,
            weight_decay=self.weight_decay
        )

        data_collator = DataCollatorForTokenClassification(tokenizer=tokenizer)

        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_data,
            data_collator=data_collator # needed to pad the sentences
        )

        print('Fine-tuning model...')
        trainer.train()
        trainer.save_model('./bert-model-test/')