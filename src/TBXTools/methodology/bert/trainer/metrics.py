class Metrics:

    def __init__(self):
        self.eval_data = None
        self.processor = None

    def score(self, pred_terms, true_terms): # my score func
        pred_terms = set(pred_terms)
        true_terms = set(true_terms)

        tp = len(pred_terms & true_terms) # common terms in both sets

        precision = tp / len(pred_terms) if len(pred_terms) > 0 else 0.0
        recall = tp / len(true_terms) if len(true_terms) > 0 else 0.0

        if precision + recall == 0:
            f1 = 0.0
        else: 
            f1 = 2 * precision * recall / (precision + recall)

        return precision, recall, f1

    def compute_metrics(self, p):
        import numpy as np
        prediction_logits, label_ids = p # label_ids are true padded label IDs from eval_data
        predictions = np.argmax(prediction_logits, axis=2)

        all_pred_terms = []
        all_true_terms = []

        for i in range(len(self.eval_data)):
            text = self.eval_data[i]["text"]
            offsets = self.eval_data[i]["offset_mapping"]
            predicted_ids = predictions[i]
            true_ids = label_ids[i]

            reconstructed_predicted_terms = self.processor._pred_labels_to_text(text, offsets, predicted_ids, self.processor._id2label)
            all_pred_terms.extend(reconstructed_predicted_terms)

            reconstructed_true_terms = self.processor._pred_labels_to_text(text, offsets, true_ids, self.processor._id2label)
            all_true_terms.extend(reconstructed_true_terms)

            # print(f"Segment {i}")
            # print("pred terms in segment:", reconstructed_predicted_terms)
            # print("true terms in segment:", reconstructed_true_terms)

        # print("\nPredicted terms that do not appear in the training corpus:")
        # unique_preds = [term for term in all_pred_terms if term not in all_true_terms]
        # print(unique_preds)
        # print("All unique predicted terms")
        # print(set(all_pred_terms))
        precision, recall, f1 = self.score(all_pred_terms, all_true_terms)

        return {"precision": precision, "recall": recall, "f1": f1}

    def compute_metrics_lemm(self, p):
        import numpy as np
        prediction_logits, label_ids = p # label_ids are true padded label IDs from eval_data
        predictions = np.argmax(prediction_logits, axis=2)
        all_pred_terms = []
        all_true_terms = []

        for i in range(len(self.eval_data)):
            tokens = self.eval_data[i]["tokens"]
            predicted_ids = predictions[i]
            true_ids = label_ids[i]
            reconstructed_predicted_terms = self.processor._bio_to_terms(tokens, predicted_ids)
            all_pred_terms.extend(reconstructed_predicted_terms)

            reconstructed_true_terms = self.processor._bio_to_terms(tokens, true_ids)

            all_true_terms.extend(reconstructed_true_terms)

            # print(f"Segment {i}")
            # print("pred terms in segment:", reconstructed_predicted_terms)
            # print("true terms in segment:", reconstructed_true_terms)
        
        precision, recall, f1 = self.score(all_pred_terms, all_true_terms)

        print(all_pred_terms)
        return {"precision": precision, "recall": recall, "f1": f1}