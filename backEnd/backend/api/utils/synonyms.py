
import random
# import torch
# import numpy as np
# from transformers import AutoModel, AutoTokenizer
# from scipy.spatial.distance import cosine

# phobert = AutoModel.from_pretrained("vinai/phobert-base").eval()
# tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base")

# def get_word_vector(word):
#     inputs = tokenizer(word, return_tensors="pt", padding=True, truncation=True)
#     with torch.no_grad():
#         outputs = phobert(**inputs)
#     token_vectors = outputs.last_hidden_state[:, 1:-1, :].squeeze(0)
#     word_vector = token_vectors.mean(dim=0).numpy()
    
#     return word_vector

def synonyms(text1,text2):
    return random.randint(1, 10)
    vec1 = get_word_vector(text1)
    vec2 = get_word_vector(text2)
    return 1 - cosine(vec1, vec2)