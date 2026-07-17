class Metrics:

    def __init__(self):
        self.eval_data = None
        self.processor = None

    def _old_score(self, pred_terms, true_terms): # my score func
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
        import pandas as pd
        prediction_logits, label_ids = p # label_ids are true padded label IDs from eval_data
        predictions = np.argmax(prediction_logits, axis=2)

        all_pred_terms = []
        all_true_terms = []
        rows = []

        for i in range(len(self.eval_data)):
            tokens = self.eval_data[i]["tokens"]
            text = self.eval_data[i]["text"]
            offsets = self.eval_data[i]["offset_mapping"]
            predicted_ids = predictions[i]
            true_ids = label_ids[i]

            # for j, (token, true_id, pred_id) in enumerate(zip(tokens, true_ids, predicted_ids)):
            #     if token in ["[CLS]", "[SEP]", "[PAD]"] or true_id == -100:
            #         continue
                
            #     rows.append({
            #         "segment_id": i,
            #         "token_index": j,
            #         "token": token,
            #         "true_label": self.processor._id2label[true_id],
            #         "pred_label": self.processor._id2label[pred_id],
            #         "correct": true_id == pred_id
            #     })

            reconstructed_predicted_terms = self.processor._pred_labels_to_text(text, offsets, predicted_ids, self.processor._id2label)
            all_pred_terms.extend(reconstructed_predicted_terms)

            reconstructed_true_terms = self.processor._pred_labels_to_text(text, offsets, true_ids, self.processor._id2label)
            all_true_terms.extend(reconstructed_true_terms)

            # print(f"Segment {i}")
            # print("pred terms in segment:", reconstructed_predicted_terms)
            # print("true terms in segment:", reconstructed_true_terms)

        # df = pd.DataFrame(rows)
        # df.to_csv("debug_test.csv", index=False)

        # print("\nPredicted terms that do not appear in the training corpus:")
        # unique_preds = [term for term in all_pred_terms if term not in all_true_terms]
        # print(unique_preds)
        # print("All unique predicted terms")
        # print(set(all_pred_terms))
        precision, recall, f1 = self.score(all_pred_terms, all_true_terms)

        return {"precision": precision, "recall": recall, "f1": f1}

    def _old_compute_metrics_lemm(self, p):
        import numpy as np
        import pandas as pd
        prediction_logits, label_ids = p # label_ids are true padded label IDs from eval_data
        predictions = np.argmax(prediction_logits, axis=2)
        all_pred_terms = []
        all_true_terms = []

        rows = []
        for i in range(len(self.eval_data)):
            tokens = self.eval_data[i]["tokens"]
            predicted_ids = predictions[i]
            true_ids = label_ids[i]
            # for j, (token, true_id, pred_id) in enumerate(zip(tokens, true_ids, predicted_ids)):
            #     if token in ["[CLS]", "[SEP]", "[PAD]"] or true_id == -100:
            #         continue
                
            #     rows.append({
            #         "segment_id": i,
            #         "token_index": j,
            #         "token": token,
            #         "true_label": self.processor._id2label[true_id],
            #         "pred_label": self.processor._id2label[pred_id],
            #         "correct": true_id == pred_id
            #     })

            reconstructed_predicted_terms = self.processor._bio_to_terms(tokens, predicted_ids)
            all_pred_terms.extend(reconstructed_predicted_terms)
            reconstructed_true_terms = self.processor._bio_to_terms(tokens, true_ids)
            all_true_terms.extend(reconstructed_true_terms)

            # print(f"Segment {i}")
            # print("pred terms in segment:", reconstructed_predicted_terms)
            # print("true terms in segment:", reconstructed_true_terms)
        
        # df = pd.DataFrame(rows)
        # df.to_csv("debug_test.csv", index=False)

        precision, recall, f1 = self.score(all_pred_terms, all_true_terms)
        # print coincidences between preds and true terms to check what is being annotated as true terms, or check true terms, true terms are problematic since they are also automatically annotated not some golden labels... need to check asap

        # check label alignment, what is being appended to sqlite is bert tokens im pretty sure, check engitech
        
        # common = list(set(all_pred_terms) & set(all_true_terms))
        # print(common)
        # print(all_pred_terms)   

        return {"precision": precision, "recall": recall, "f1": f1}
    
    def compute_metrics_lemm(self, p):
        import numpy as np
        
        prediction_logits, label_ids = p
        predictions = np.argmax(prediction_logits, axis=2)
        
        pred_dict = {}
        true_dict = {}

        for segment_idx in range(len(self.eval_data)):
            tokens = self.eval_data[segment_idx]["tokens"]
            predicted_ids = predictions[segment_idx]
            true_ids = label_ids[segment_idx]

            pred_terms = self.processor._bio_to_terms(tokens, predicted_ids)
            true_terms = self.processor._bio_to_terms(tokens, true_ids)
            
            pred_dict[segment_idx] = pred_terms
            true_dict[segment_idx] = true_terms

        precision, recall, f1 = self.score(pred_dict, true_dict)

        return {"precision": precision, "recall": recall, "f1": f1}


    def score(self, pred_dict, true_dict):
        tp = 0
        total_preds = 0
        total_trues = 0
        
        for i in true_dict.keys():
            preds = pred_dict.get(i, [])
            trues = true_dict.get(i, [])
            
            total_preds += len(preds)
            total_trues += len(trues)
            
            true_pool = list(trues)
            
            for pred in preds:
                if pred in true_pool:
                    tp += 1
                    true_pool.remove(pred) # Remove match to avoid double-counting

        precision = tp / total_preds if total_preds > 0 else 0.0
        recall = tp / total_trues if total_trues > 0 else 0.0

        if precision + recall == 0:
            f1 = 0.0
        else: 
            f1 = 2 * precision * recall / (precision + recall)
            
        return precision, recall, f1