import numpy as np
import json
from sentence_transformers import SentenceTransformer
from scipy.optimize import linear_sum_assignment
from collections import defaultdict

class AlignWithTransformers:

    def __init__(self, model_name=None):
        self.model = SentenceTransformer(model_name)

    def align_words(self, sl_input_list, tl_input_list, output_file="aligned_terms.txt", output_json="aligned_terms.json", threshold=0.50, group_by_en=False): 
    
        with open(sl_input_list, "r", encoding="utf-8") as f:
            english_list = [line.strip() for line in f if line.strip()]

        with open(tl_input_list, "r", encoding="utf-8") as f:
            polish_list = [line.strip() for line in f if line.strip()]

        # Generate contextual embeddings for both language lists
        vectors_pl = self.model.encode(polish_list, convert_to_numpy=True, show_progress_bar=False)
        vectors_en = self.model.encode(english_list, convert_to_numpy=True, show_progress_bar=False)

        # Vector normalization
        vectors_pl = vectors_pl / np.linalg.norm(vectors_pl, axis=1, keepdims=True)
        vectors_en = vectors_en / np.linalg.norm(vectors_en, axis=1, keepdims=True)

        # Compute the similarity matrix
        matrix_sim = np.dot(vectors_pl, vectors_en.T)

        # ROUND 1: Strict (1-to-1)
        riga_ind, col_ind = linear_sum_assignment(-matrix_sim)

        aligned_output = []
        results_list = []
        json_data = []                                                                       

        chosen_pl_indices = set()
        chosen_en_indices = set()

        for r, c in zip(riga_ind, col_ind):
            score = float(matrix_sim[r, c])
            
            if score >= threshold:
                p_pl = polish_list[r]
                p_en = english_list[c]
                
                chosen_pl_indices.add(r)
                chosen_en_indices.add(c)

                output_line = f"{p_en}\t{p_pl}"
                aligned_output.append(output_line) 
               
                json_entry = {
                    "en": p_en,
                    "pl": p_pl
                }
                json_data.append(json_entry)
                results_list.append((p_en, p_pl))

        # ROUND 2: Rematch for Synonyms / Leftovers
        # index excluded from first round
        excluded_pl_idx = [i for i in range(len(polish_list)) if i not in chosen_pl_indices]
        excluded_en_idx = [i for i in range(len(english_list)) if i not in chosen_en_indices]

        for c in excluded_en_idx:
            r_best = np.argmax(matrix_sim[:, c])
            score = float(matrix_sim[r_best, c])
            
            if score >= threshold:
                p_pl = polish_list[r_best]
                p_en = english_list[c]
                chosen_en_indices.add(c) 

                aligned_output.append(f"{p_en}\t{p_pl}")
                json_data.append({
                    "status": "synonym_match",
                    "en": p_en,
                    "pl": p_pl
                })
                results_list.append((p_en, p_pl))

        for r in excluded_pl_idx:
            c_best = np.argmax(matrix_sim[r, :])
            score = float(matrix_sim[r, c_best])
            
            if score >= threshold:
                p_pl = polish_list[r]
                p_en = english_list[c_best]
                chosen_pl_indices.add(r) 

                aligned_output.append(f"{p_en}\t{p_pl}")
                json_data.append({
                    "status": "synonym_match",
                    "en": p_en,
                    "pl": p_pl
                })
                results_list.append((p_en, p_pl))

        # ROUND 3: Identify and handle unmatched terms- under threshold or unequal list

        final_excluded_pl = [polish_list[i] for i in range(len(polish_list)) if i not in chosen_pl_indices]
        final_excluded_en = [english_list[i] for i in range(len(english_list)) if i not in chosen_en_indices]

        # Polish terms remaining with absolutely no valid match
        if final_excluded_pl:
            for pl_word in final_excluded_pl:
                aligned_output.append(f"None\t{pl_word}")
                json_data.append({
                    "status": "unmatched_target",
                    "en": "None",
                    "pl": pl_word
                })

        # English terms remaining with absolutely no valid match
        if final_excluded_en:
            for en_word in final_excluded_en:
                aligned_output.append(f"{en_word}\tNone")
                json_data.append({
                    "status": "unmatched_source",
                    "en": en_word,
                    "pl": "None"
                })

        if group_by_en:
            # initialize a dictionary to store lists of Polish translations for each English key
            grouped_dict= defaultdict(list)

            # 
            for entry in json_data: 
                if entry["en"] != "None" and entry["pl"] != "None": #filters out None values (the unmatched from above)
                    grouped_dict[entry["en"]].append(entry["pl"])

            shared_map = {}
            for en_key, pl_list in grouped_dict.items():
                unique_translations = list(dict.fromkeys(pl_list))
                shared_map[en_key] = unique_translations

            keys = list(shared_map.keys())
            for i in range(len(keys)):
                for j in range(i + 1, len(keys)):
                    k1, k2 = keys[i], keys[j]

                    if set(shared_map[k1]) & set(shared_map[k2]):
                      unione = list(dict.fromkeys(shared_map[k1] + shared_map[k2]))
                      shared_map[k1] = unione
                      shared_map[k2] = unione

            final_json_output = {"proper": shared_map}
        else:
            final_json_output = json_data

        # Save files
        with open(output_file, "w", encoding="utf-8") as f:
            for line in aligned_output:
                f.write(line + "\n")

        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(final_json_output, f, indent=4, ensure_ascii=False)

        #print(results_list)
        return output_file, results_list, output_json


if __name__ == "__main__":
    aligner = AlignWithTransformers("sentence-transformers/LaBSE")

    aligner.align_words("list_engin_en.txt", "list_engin_pl.txt", group_by_en=False, threshold=0.75, output_json="align-75-no_punct_False.json")





