import numpy as np


def check_similarity(model, word_en, word_pl):
    # calculates embeddings
    vec_en = model.encode([word_en], convert_to_numpy=True)
    vec_pl = model.encode([word_pl], convert_to_numpy=True)

    
    vec_en = vec_en / np.linalg.norm(vec_en, axis=1, keepdims=True)
    vec_pl = vec_pl / np.linalg.norm(vec_pl, axis=1, keepdims=True)

    # Cosine Similarity
    score = float(np.dot(vec_pl, vec_en.T)[0][0])
    print(f"Punteggio tra '{word_en}' e '{word_pl}': {score:.4f}")
    return score


# how to use it
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/LaBSE')

s1 = check_similarity(model, "engine", "silnik")
s2 = check_similarity(model, "engine", "motorowy")
s3 = check_similarity(model, "engine", "sterownik silnika")
s4 = check_similarity(model, "automotive", "motorowy")