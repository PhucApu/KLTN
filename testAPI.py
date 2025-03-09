# import torch
# import safetensors.torch
# from transformers import PreTrainedTokenizerFast, AutoConfig, AutoModel
# from fastapi import FastAPI
# from pydantic import BaseModel
# import uvicorn
# import string
# import os

# # --- Mapping ---
# # Mapping cho relation mà mô hình học (hãy cập nhật theo dữ liệu huấn luyện của bạn)
# relation2id = {"0": 0, "1": 1, "2": 2}  
# # Nếu mô hình của bạn học được các từ relation cụ thể (ví dụ "rel_parent", "rel_child", …)
# # bạn có thể cập nhật như: relation2id = {"rel_none":0, "rel_parent":1, "rel_child":2}
# inv_relation2id = {v: k for k, v in relation2id.items()}

# # Mapping cho NER (concept)
# # Giả sử: 0 = O, 1 = B-CONCEPT, 2 = I-CONCEPT
# label_map = {0: "O", 1: "B-Concept", 2: "I-Concept"}
# # Mapping cho relation token (với cùng số lớp, ví dụ 0 = O, 1 = B-Relation, 2 = I-Relation)
# relation_label_map = {0: "O", 1: "B-Relation", 2: "I-Relation"}

# # --- Hàm tính concept spans từ nhãn (sử dụng cho concept grouping) ---
# def compute_concept_spans(labels):
#     spans = []
#     start = None
#     for i, label in enumerate(labels):
#         if label not in (-100, 0):
#             if start is None:
#                 start = i
#         else:
#             if start is not None:
#                 spans.append((start, i))
#                 start = None
#     if start is not None:
#         spans.append((start, len(labels)))
#     return spans

# # --- Hàm grouping token theo nhãn (cho cả concept và relation) ---
# def group_tokens(tokens, predictions, offset_mapping, label_map):
#     """
#     Nhóm các token liên tiếp có nhãn khác "O" thành một span.
#     Trả về danh sách các dict chứa:
#       - "text": substring trong văn bản,
#       - "start": offset start của span,
#       - "end": offset end của span,
#       - "token_range": (start_index, end_index) của token trong danh sách.
#     """
#     spans = []
#     current_span = None
#     current_token_range = None
#     for i, (token, pred, (start, end)) in enumerate(zip(tokens, predictions, offset_mapping)):
#         label = label_map.get(pred, "O")
#         if label.startswith("B-"):
#             if current_span is not None:
#                 spans.append({
#                     "text": None,  # sẽ được xác định sau
#                     "start": current_span["start"],
#                     "end": offset_mapping[i-1][1],
#                     "token_range": (current_token_range[0], i)
#                 })
#             current_span = {"start": start, "end": end}
#             current_token_range = (i, i+1)
#         elif label.startswith("I-") and current_span is not None:
#             # Nếu khoảng cách giữa token hiện tại và token trước vượt quá gap_threshold thì tách mới (bạn có thể điều chỉnh nếu cần)
#             current_span["end"] = end
#             current_token_range = (current_token_range[0], i+1)
#         else:
#             if current_span is not None:
#                 spans.append({
#                     "text": None,
#                     "start": current_span["start"],
#                     "end": offset_mapping[i-1][1],
#                     "token_range": (current_token_range[0], i)
#                 })
#                 current_span = None
#                 current_token_range = None
#     if current_span is not None:
#         spans.append({
#             "text": None,
#             "start": current_span["start"],
#             "end": offset_mapping[-1][1],
#             "token_range": (current_token_range[0], len(tokens))
#         })
#     return spans

# # --- Mô hình ---
# # Lớp mô hình joint cho NER và relation extraction.
# # Ở chế độ inference, chúng ta sẽ sử dụng:
# #  - concept_classifier để dự đoán nhãn concept
# #  - token_relation_classifier để dự đoán nhãn relation cho từng token
# #  - relation_pair_classifier để dự đoán mối quan hệ giữa cặp concept
# class PhoBERTJointModel(torch.nn.Module):
#     def __init__(self, config, num_labels, num_relation_token_labels, relation2id, lambda_relation=0.1):
#         super().__init__()
#         self.num_labels = num_labels                      # cho concept (token classification)
#         self.num_relation_token_labels = num_relation_token_labels  # cho relation (token classification)
#         self.relation2id = relation2id                    
#         self.num_relation_pair_labels = len(relation2id)
#         self.lambda_relation = lambda_relation

#         self.phobert = AutoModel.from_pretrained("vinai/phobert-base", config=config)
#         hidden_size = config.hidden_size
#         self.dropout = torch.nn.Dropout(config.hidden_dropout_prob)
#         # Các head được huấn luyện:
#         self.concept_classifier = torch.nn.Linear(hidden_size, num_labels)
#         self.token_relation_classifier = torch.nn.Linear(hidden_size, num_relation_token_labels)
#         self.relation_pair_classifier = torch.nn.Sequential(
#             torch.nn.Linear(2 * hidden_size, hidden_size),
#             torch.nn.ReLU(),
#             torch.nn.Linear(hidden_size, self.num_relation_pair_labels)
#         )
#         self.loss_fct = torch.nn.CrossEntropyLoss(ignore_index=-100)

#     @classmethod
#     def from_pretrained(cls, pretrained_model_dir, **kwargs):
#         config = kwargs.get("config", AutoConfig.from_pretrained("vinai/phobert-base"))
#         num_labels = kwargs.get("num_labels", 3)
#         num_relation_token_labels = kwargs.get("num_relation_token_labels", 3)
#         relation2id = kwargs.get("relation2id", {})
#         lambda_relation = kwargs.get("lambda_relation", 0.1)
#         model = cls(config, num_labels, num_relation_token_labels, relation2id, lambda_relation)
#         safetensors_path = os.path.join(pretrained_model_dir, "model.safetensors")
#         if not os.path.exists(safetensors_path):
#             raise FileNotFoundError(f"Không tìm thấy file model.safetensors tại: {safetensors_path}")
#         state_dict = safetensors.torch.load_file(safetensors_path, device="cpu")
#         # Loại bỏ các key không cần (ví dụ: nếu có token_relation_classifier key khác tên)
#         for key in list(state_dict.keys()):
#             if key.startswith("token_relation_classifier."):
#                 # Nếu mô hình huấn luyện có key này nhưng bạn muốn loại bỏ, thì pop nó
#                 state_dict.pop(key)
#         model.load_state_dict(state_dict, strict=False)
#         return model

#     def forward(self, input_ids, attention_mask, labels=None, concept_spans_subword=None, relation_pairs=None):
#         outputs = self.phobert(input_ids=input_ids, attention_mask=attention_mask)
#         sequence_output = outputs.last_hidden_state
#         sequence_output = self.dropout(sequence_output)
#         concept_logits = self.concept_classifier(sequence_output)
#         # Chúng ta không dùng forward để dự đoán relation token và pair, ta gọi chúng trực tiếp trong inference
#         total_loss = None
#         if labels is not None:
#             loss_token = self.loss_fct(concept_logits.view(-1, self.num_labels), labels.view(-1))
#             total_loss = loss_token
#         return TokenClassifierOutput(loss=total_loss, logits=concept_logits)

# # --- Load mô hình & Tokenizer ---
# model_path = "phobert-joint-finetuned"  # Thư mục chứa model.safetensors
# config = AutoConfig.from_pretrained("vinai/phobert-base")
# model = PhoBERTJointModel.from_pretrained(model_path, config=config, num_labels=3, 
#                                             num_relation_token_labels=3, relation2id=relation2id)
# model.eval()
# tokenizer = PreTrainedTokenizerFast.from_pretrained("vinai/phobert-base")

# # --- Hàm trích xuất ---
# def extract_concepts_relations(text: str, gap_threshold: int = 3):
#     """
#     Quá trình:
#       1. Tokenize văn bản, lấy offset.
#       2. Dự đoán nhãn cho từng token cho cả concept và relation:
#          - Sử dụng concept_classifier để dự đoán nhãn concept.
#          - Sử dụng token_relation_classifier để dự đoán nhãn relation.
#       3. Nhóm các token thành các concept và relation span (theo offset).
#          Mỗi concept có: "text", "start", "end".
#          Mỗi relation span có: "text", "start", "end".
#       4. Dự đoán mối quan hệ giữa các concept (C1_R_C2) bằng relation_pair_classifier.
#     Trả về dict gồm:
#       - concepts: mảng các concept.
#       - relations: mảng các relation (dựa trên token-level relation).
#       - C1_R_C2: mảng chứa { "concept1": <text>, "relation": <text>, "concept2": <text> }.
#     """
#     encoding = tokenizer(text, return_offsets_mapping=True, return_tensors="pt", truncation=True)
#     input_ids = encoding["input_ids"]
#     attention_mask = encoding["attention_mask"]
#     offsets = encoding["offset_mapping"][0].tolist()
    
#     with torch.no_grad():
#         outputs = model.phobert(input_ids=input_ids, attention_mask=attention_mask)
#     sequence_output = outputs.last_hidden_state[0]  # (seq_len, hidden_size)
    
#     # Dự đoán NER (concept)
#     concept_logits = model.concept_classifier(model.dropout(sequence_output))
#     concept_preds = torch.argmax(concept_logits, dim=1).tolist()
#     # Dự đoán relation token
#     relation_logits = model.token_relation_classifier(model.dropout(sequence_output))
#     relation_preds = torch.argmax(relation_logits, dim=1).tolist()
    
#     tokens = tokenizer.convert_ids_to_tokens(input_ids[0])
    
#     # Loại bỏ token đặc biệt ở đầu và cuối
#     if tokens and tokens[0] in tokenizer.all_special_tokens:
#         tokens = tokens[1:]
#         offsets = offsets[1:]
#         concept_preds = concept_preds[1:]
#         relation_preds = relation_preds[1:]
#     if tokens and tokens[-1] in tokenizer.all_special_tokens:
#         tokens = tokens[:-1]
#         offsets = offsets[:-1]
#         concept_preds = concept_preds[:-1]
#         relation_preds = relation_preds[:-1]
    
#     # Nhóm token thành concept
#     concept_spans = group_tokens(tokens, concept_preds, offsets, label_map)
#     # Sau khi nhóm, gán text cho mỗi span dựa trên offset
#     concepts_out = []
#     for span in concept_spans:
#         span["text"] = text[span["start"]: span["end"]]
#         concepts_out.append({
#             "text": span["text"],
#             "start": span["start"],
#             "end": span["end"],
#             "token_range": span["token_range"]
#         })
    
#     # Nhóm token thành relation span (cho các token có nhãn relation)
#     relation_spans = group_tokens(tokens, relation_preds, offsets, relation_label_map)
#     relations_out = []
#     for span in relation_spans:
#         span["text"] = text[span["start"]: span["end"]]
#         relations_out.append({
#             "text": span["text"],
#             "start": span["start"],
#             "end": span["end"],
#             "token_range": span["token_range"]
#         })
    
#     # Dự đoán mối quan hệ giữa các concept (C1_R_C2) dùng relation_pair_classifier
#     C1_R_C2 = []
#     if len(concept_spans) > 1:
#         for i in range(len(concept_spans)):
#             for j in range(len(concept_spans)):
#                 if i != j:
#                     # Dùng token_range của mỗi span để lấy vector trung bình từ sequence_output
#                     span_i = concept_spans[i]["token_range"]
#                     span_j = concept_spans[j]["token_range"]
#                     if span_i[1] > span_i[0] and span_j[1] > span_j[0]:
#                         rep_i = sequence_output[span_i[0]:span_i[1]].mean(dim=0)
#                         rep_j = sequence_output[span_j[0]:span_j[1]].mean(dim=0)
#                         pair_rep = torch.cat([rep_i, rep_j], dim=-1)
#                         with torch.no_grad():
#                             logits_pair = model.relation_pair_classifier(pair_rep)
#                         rel_pred_id = torch.argmax(logits_pair).item()
#                         rel_text = inv_relation2id.get(rel_pred_id, "N/A")
#                         C1_R_C2.append({
#                             "concept1": text[concept_spans[i]["start"]:concept_spans[i]["end"]],
#                             "relation": rel_text,
#                             "concept2": text[concept_spans[j]["start"]:concept_spans[j]["end"]]
#                         })
    
#     return {"concepts": concepts_out, "relations": relations_out, "C1_R_C2": C1_R_C2}

# # --- API ---
# app = FastAPI()

# class TextInput(BaseModel):
#     text: str

# @app.post("/extract")
# def extract_endpoint(text_input: TextInput):
#     result = extract_concepts_relations(text_input.text)
#     return result

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)






# import torch
# import torch.nn as nn
# from transformers import AutoModel, PreTrainedTokenizerFast, logging

# # Tắt cảnh báo không cần thiết của Transformers
# logging.set_verbosity_error()

# # Định nghĩa mapping cho nhãn
# NUM_ENTITY_LABELS = 3    # O, B-Concept, I-Concept
# NUM_RELATION_LABELS = 3  # O, B-Relation, I-Relation

# # Mapping nhãn
# id2label_concept = {0: "O", 1: "B-Concept", 2: "I-Concept"}
# id2label_relation = {0: "O", 1: "B-Relation", 2: "I-Relation"}

# # Hàm giải mã thực thể từ dự đoán token-level (định dạng BIO)
# def decode_entities(tokens, preds, offsets, text):
#     entities = []
#     current_entity = None
#     for idx, (token, pred, offset) in enumerate(zip(tokens, preds, offsets)):
#         label = id2label_concept[pred]
#         if label.startswith("B-"):
#             if current_entity is not None:
#                 entities.append({
#                     "text": current_entity["text"],
#                     "start": current_entity["start"],
#                     "end": current_entity["end"],
#                     "token_indices": current_entity["token_indices"]
#                 })
#             current_entity = {"text": text[offset[0]:offset[1]], "start": offset[0], "end": offset[1], "token_indices": [idx]}
#         elif label.startswith("I-") and current_entity is not None:
#             current_entity["text"] += " " + text[offset[0]:offset[1]]
#             current_entity["end"] = offset[1]
#             current_entity["token_indices"].append(idx)
#         else:
#             if current_entity is not None:
#                 entities.append({
#                     "text": current_entity["text"],
#                     "start": current_entity["start"],
#                     "end": current_entity["end"],
#                     "token_indices": current_entity["token_indices"]
#                 })
#                 current_entity = None
#     if current_entity is not None:
#         entities.append({
#             "text": current_entity["text"],
#             "start": current_entity["start"],
#             "end": current_entity["end"],
#             "token_indices": current_entity["token_indices"]
#         })
#     return entities

# # Hàm giải mã token-level relation từ dự đoán (định dạng BIO)
# def decode_relation_tokens(tokens, preds, offsets, text):
#     relations = []
#     current_relation = None
#     for idx, (token, pred, offset) in enumerate(zip(tokens, preds, offsets)):
#         label = id2label_relation[pred]
#         if label.startswith("B-"):
#             if current_relation is not None:
#                 relations.append({
#                     "text": current_relation["text"],
#                     "start": current_relation["start"],
#                     "end": current_relation["end"],
#                     "token_indices": current_relation["token_indices"]
#                 })
#             current_relation = {"text": text[offset[0]:offset[1]], "start": offset[0], "end": offset[1], "token_indices": [idx]}
#         elif label.startswith("I-") and current_relation is not None:
#             current_relation["text"] += " " + text[offset[0]:offset[1]]
#             current_relation["end"] = offset[1]
#             current_relation["token_indices"].append(idx)
#         else:
#             if current_relation is not None:
#                 relations.append({
#                     "text": current_relation["text"],
#                     "start": current_relation["start"],
#                     "end": current_relation["end"],
#                     "token_indices": current_relation["token_indices"]
#                 })
#                 current_relation = None
#     if current_relation is not None:
#         relations.append({
#             "text": current_relation["text"],
#             "start": current_relation["start"],
#             "end": current_relation["end"],
#             "token_indices": current_relation["token_indices"]
#         })
#     return relations

# # Mô hình đa nhiệm sử dụng PhoBERT
# class PhoBERTMultiTaskModel(nn.Module):
#     def __init__(self, num_entity_labels, num_relation_labels):
#         super(PhoBERTMultiTaskModel, self).__init__()
#         self.phobert = AutoModel.from_pretrained("vinai/phobert-base", cache_dir="D:/Cache-hunging-face")
#         hidden_size = self.phobert.config.hidden_size
#         self.entity_classifier = nn.Linear(hidden_size, num_entity_labels)
#         self.token_relation_classifier = nn.Linear(hidden_size, num_relation_labels)
#         # Các thành phần cho triple extraction
#         self.head_extractor = nn.Linear(hidden_size, hidden_size)
#         self.tail_extractor = nn.Linear(hidden_size, hidden_size)
#         self.biaffine = nn.Bilinear(hidden_size, hidden_size, num_relation_labels)
    
#     def forward(self, input_ids, attention_mask):
#         outputs = self.phobert(input_ids=input_ids, attention_mask=attention_mask)
#         sequence_output = outputs.last_hidden_state  # (batch, seq_len, hidden_size)
#         entity_logits = self.entity_classifier(sequence_output)  # (batch, seq_len, num_entity_labels)
#         token_relation_logits = self.token_relation_classifier(sequence_output)  # (batch, seq_len, num_relation_labels)
        
#         # Triple extraction
#         head_repr = self.head_extractor(sequence_output)
#         tail_repr = self.tail_extractor(sequence_output)
#         batch_size, seq_len, hidden_size = head_repr.size()
#         head_exp = head_repr.unsqueeze(2).expand(batch_size, seq_len, seq_len, hidden_size)
#         tail_exp = tail_repr.unsqueeze(1).expand(batch_size, seq_len, seq_len, hidden_size)
#         triple_logits = self.biaffine(head_exp, tail_exp)  # (batch, seq_len, seq_len, num_relation_labels)
        
#         return {
#             "entity_logits": entity_logits,
#             "token_relation_logits": token_relation_logits,
#             "triple_logits": triple_logits
#         }

# # Hàm lấy text quan hệ (đơn giản hóa)
# def get_relation_text():
#     return "là"  # Có thể cải thiện với mapping cụ thể nếu cần

# # Hàm inference để dự đoán và in kết quả
# def run_inference(model, tokenizer, text, device):
#     # Mã hóa văn bản
#     encoded = tokenizer(text, return_offsets_mapping=True, return_tensors="pt", truncation=True)
#     input_ids = encoded["input_ids"].to(device)
#     attention_mask = encoded["attention_mask"].to(device)
#     offset_mapping = encoded["offset_mapping"][0].tolist()
#     tokenized_tokens = tokenizer.convert_ids_to_tokens(input_ids[0])
    
#     model.eval()
#     with torch.no_grad():
#         outputs = model(input_ids, attention_mask)
    
#     entity_logits = outputs["entity_logits"]
#     token_relation_logits = outputs["token_relation_logits"]
#     triple_logits = outputs["triple_logits"]
    
#     entity_preds = torch.argmax(entity_logits, dim=-1)[0].tolist()
#     relation_preds = torch.argmax(token_relation_logits, dim=-1)[0].tolist()
    
#     # Lọc bỏ token đặc biệt (offset [0, 0])
#     filtered_tokens = []
#     filtered_offsets = []
#     filtered_entity_preds = []
#     filtered_relation_preds = []
#     for token, offset, e_pred, r_pred in zip(tokenized_tokens, offset_mapping, entity_preds, relation_preds):
#         if offset[0] == offset[1]:
#             continue
#         filtered_tokens.append(token)
#         filtered_offsets.append(offset)
#         filtered_entity_preds.append(e_pred)
#         filtered_relation_preds.append(r_pred)
    
#     # Giải mã entities và relation tokens
#     entities = decode_entities(filtered_tokens, filtered_entity_preds, filtered_offsets, text)
#     relation_tokens = decode_relation_tokens(filtered_tokens, filtered_relation_preds, filtered_offsets, text)
    
#     # Triple extraction
#     triple_preds = torch.argmax(triple_logits, dim=-1)[0].tolist()
    
#     # Ghép nối triples
#     triples = []
#     for subj in entities:
#         for obj in entities:
#             found_relation = None
#             for i in subj["token_indices"]:
#                 for j in obj["token_indices"]:
#                     if triple_preds[i][j] != 0:
#                         found_relation = get_relation_text()
#                         break
#                 if found_relation is not None:
#                     break
#             if found_relation is not None:
#                 triples.append({
#                     "subject": subj["text"],
#                     "relation": found_relation,
#                     "object": obj["text"]
#                 })
    
#     # In kết quả
#     print("\nExtracted Entities:")
#     for ent in entities:
#         print(ent)
#     print("\nExtracted Relation Tokens:")
#     for rel in relation_tokens:
#         print(rel)
#     print("\nExtracted Triples (Concept - Relation - Concept):")
#     if triples:
#         for triple in triples:
#             print(triple)
#     else:
#         print("Không phát hiện triple nào.")

# if __name__ == "__main__":
#     tokenizer = PreTrainedTokenizerFast.from_pretrained("vinai/phobert-base", cache_dir="D:/Cache-hunging-face")
#     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#     model = PhoBERTMultiTaskModel(num_entity_labels=NUM_ENTITY_LABELS, num_relation_labels=NUM_RELATION_LABELS)
#     checkpoint_path = "phobert_multitask_model.pt"
#     model.load_state_dict(torch.load(checkpoint_path, map_location=device), strict=False)
#     model.to(device)
    
#     input_text = ("Người đại diện theo pháp luật của tổ chức trong nước, tổ chức kinh tế có vốn đầu tư nước ngoài; "
#                   "người đứng đầu của tổ chức nước ngoài có chức năng ngoại giao đối với việc sử dụng đất của tổ chức mình.")
    
#     run_inference(model, tokenizer, input_text, device)




######################################################


import torch
from transformers import AutoTokenizer, RobertaModel
from torch import nn
import re

# Định nghĩa lại lớp mô hình
class JointModel(nn.Module):
    def __init__(self, num_concept_labels=3, num_relation_labels=3, num_rel_types=1):
        super().__init__()
        self.phobert = RobertaModel.from_pretrained("vinai/phobert-base", cache_dir="D:/Cache-hunging-face")
        self.hidden_size = 768
        
        self.concept_head = nn.Linear(self.hidden_size, num_concept_labels)
        self.relation_head = nn.Linear(self.hidden_size, num_relation_labels)
        self.relation_classifier = nn.Linear(self.hidden_size * 3, num_rel_types)

    def forward(self, input_ids, attention_mask, relation_pairs=None):
        outputs = self.phobert(input_ids, attention_mask=attention_mask)
        sequence_output = outputs.last_hidden_state
        
        concept_logits = self.concept_head(sequence_output)
        relation_logits = self.relation_head(sequence_output)
        
        if relation_pairs is not None and len(relation_pairs) > 0:
            batch_size = input_ids.size(0)
            relation_features = []
            
            for b in range(batch_size):
                pairs = relation_pairs[b]
                if isinstance(pairs, dict):
                    pairs = [pairs]
                
                for pair in pairs:
                    src_start, src_end = pair["source"]
                    rel_idx = pair["relation"]
                    tgt_start, tgt_end = pair["target"]
                    
                    src_vec = sequence_output[b, src_start:src_end + 1].mean(dim=0)
                    rel_vec = sequence_output[b, rel_idx]
                    tgt_vec = sequence_output[b, tgt_start:tgt_end + 1].mean(dim=0)
                    
                    combined_vec = torch.cat([src_vec, rel_vec, tgt_vec], dim=0)
                    relation_features.append(combined_vec)
            
            if relation_features:
                relation_features = torch.stack(relation_features)
                relation_pred = self.relation_classifier(relation_features)
            else:
                relation_pred = None
        else:
            relation_pred = None
        
        return concept_logits, relation_logits, relation_pred

# Tải tokenizer
tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base", cache_dir="D:/Cache-hunging-face")

# Tải mô hình đã huấn luyện
model = JointModel(num_concept_labels=3, num_relation_labels=3, num_rel_types=1)
model.load_state_dict(torch.load("joint_model_full.pth"))
model.eval()

# Hàm loại bỏ ký tự đặc biệt
def clean_special_characters(text):
    # Giữ lại chữ cái (bao gồm có dấu), số và khoảng trắng, loại bỏ ký tự đặc biệt khác
    cleaned_text = re.sub(r'[^\w\s]', '', text, flags=re.UNICODE)
    return cleaned_text.strip()

# Hàm hoàn thiện các từ bị thiếu ký tự
def complete_missing_characters(predicted_span, input_text):
    # Làm sạch cả hai chuỗi
    cleaned_predicted = clean_special_characters(predicted_span)
    cleaned_input = clean_special_characters(input_text)
    
    # Tách thành các từ
    predicted_words = cleaned_predicted.split()
    input_words = cleaned_input.split()
    
    # Tìm vị trí khớp trong input_text
    for i in range(len(input_words) - len(predicted_words) + 1):
        match = True
        for j in range(len(predicted_words)):
            if not input_words[i + j].startswith(predicted_words[j]):
                match = False
                break
        if match:
            start_idx = i
            end_idx = i + len(predicted_words)
            return ' '.join(input_words[start_idx:end_idx])
    
    # Nếu không khớp, trả về chuỗi đã làm sạch
    return cleaned_predicted

# Hàm để tokenize và dự đoán
def predict(text):
    # Tokenize đoạn text
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=256)
    input_ids = inputs["input_ids"]
    attention_mask = inputs["attention_mask"]
    
    # Dự đoán với mô hình
    with torch.no_grad():
        concept_logits, relation_logits, _ = model(input_ids, attention_mask)
    
    # Lấy nhãn dự đoán
    concept_preds = torch.argmax(concept_logits, dim=-1).squeeze().tolist()
    relation_preds = torch.argmax(relation_logits, dim=-1).squeeze().tolist()
    
    # Lấy tokens từ input_ids
    tokens = tokenizer.convert_ids_to_tokens(input_ids.squeeze().tolist())
    
    # Trích xuất concepts và relations từ nhãn dự đoán
    concepts = extract_spans(concept_preds, tokens, relation_preds, input_ids)
    relations = extract_spans(relation_preds, tokens, concept_preds, input_ids)
    
    # Làm sạch và hoàn thiện concepts và relations
    cleaned_concepts = [complete_missing_characters(concept, text) for concept in concepts]
    cleaned_relations = [complete_missing_characters(relation, text) for relation in relations]
    
    # In ra kết quả
    print("\n1. Các cụm từ concept trong câu:")
    for concept in cleaned_concepts:
        print(f" - {concept}")
    
    print("\n2. Các cụm từ relation trong câu:")
    for relation in cleaned_relations:
        print(f" - {relation}")
    
    # Dự đoán quan hệ giữa concepts
    print("\n3. Quan hệ giữa các concepts:")
    for i, concept1 in enumerate(cleaned_concepts):
        for j, concept2 in enumerate(cleaned_concepts):
            if i < j:  # Chỉ xét quan hệ theo hướng từ trái sang phải
                rel_between = find_relation_between(concept1, concept2, cleaned_relations, tokens)
                if rel_between:
                    # Kiểm tra ngữ nghĩa chặt chẽ hơn
                    if (rel_between in ["của", "có", "đối với", "có chức năng", "là", "và", "hoặc"]) and \
                       ("của" not in concept1) and ("của" not in concept2) and \
                       (concept1 != concept2) and \
                       (rel_between != concept1) and (rel_between != concept2):
                        print(f" - {concept1} --({rel_between})--> {concept2}")

# Hàm làm sạch văn bản để loại bỏ "@@"
def clean_span_text(span_text):
    # Loại bỏ ký tự "@@" và ghép các phần lại
    parts = span_text.split('@@')
    cleaned = ''.join(parts)
    return cleaned

# Hàm trích xuất spans từ nhãn BIO với debug và làm sạch văn bản
def extract_spans(labels, tokens, other_labels, input_ids):
    spans = []
    start_idx = None
    
    # Điều chỉnh chỉ số để bỏ qua token đặc biệt <s> ở đầu
    offset = 1  # Vì tokens[0] = '<s>'
    
    for i, (label, token, other_label) in enumerate(zip(labels, tokens, other_labels)):
        if token in ['<s>', '</s>']:  # Bỏ qua token đặc biệt
            continue
        # Nếu token được gán nhãn là relation trong other_labels, kết thúc span hiện tại
        if other_label in [1, 2]:
            if start_idx is not None:
                # Decode từ input_ids từ start_idx đến i-1
                span_ids = input_ids[0, start_idx:i]
                span_text = tokenizer.decode(span_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
                span_text = clean_span_text(span_text)  # Làm sạch văn bản
                print(f"Debug: Span from {start_idx} to {i}: {span_text}")
                spans.append(span_text)
                start_idx = None
            continue
        if label == 1:  # B-
            if start_idx is not None:
                # Decode từ input_ids từ start_idx đến i-1
                span_ids = input_ids[0, start_idx:i]
                span_text = tokenizer.decode(span_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
                span_text = clean_span_text(span_text)  # Làm sạch văn bản
                print(f"Debug: Span from {start_idx} to {i}: {span_text}")
                spans.append(span_text)
            start_idx = i
        elif label == 2 and start_idx is not None:  # I-
            continue  # Tiếp tục mở rộng span
        else:
            if start_idx is not None:
                # Decode từ input_ids từ start_idx đến i-1
                span_ids = input_ids[0, start_idx:i]
                span_text = tokenizer.decode(span_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
                span_text = clean_span_text(span_text)  # Làm sạch văn bản
                print(f"Debug: Span from {start_idx} to {i}: {span_text}")
                spans.append(span_text)
                start_idx = None
    
    if start_idx is not None:
        # Decode span cuối cùng nếu còn
        span_ids = input_ids[0, start_idx:len(labels)]
        span_text = tokenizer.decode(span_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
        span_text = clean_span_text(span_text)  # Làm sạch văn bản
        print(f"Debug: Final span from {start_idx} to {len(labels)}: {span_text}")
        spans.append(span_text)
    
    return spans

# Hàm tìm relation giữa hai concepts
def find_relation_between(concept1, concept2, relations, tokens):
    try:
        concept1_start = tokens.index(concept1.split()[0].replace(" ", ""))
        concept2_start = tokens.index(concept2.split()[0].replace(" ", ""))
        for relation in relations:
            rel_start = tokens.index(relation.split()[0].replace(" ", ""))
            if concept1_start < rel_start < concept2_start:
                return relation
    except ValueError:
        return None
    return None

# Kiểm tra với hai đoạn text ví dụ
texts = [
    "Người đại diện theo pháp luật của tổ chức trong nước, tổ chức kinh tế có vốn đầu tư nước ngoài; người đứng đầu của tổ chức nước ngoài có chức năng ngoại giao đối với việc sử dụng đất của tổ chức mình.",
    "Người đại diện cho cộng đồng dân cư là trưởng thôn, làng, ấp, bản, bon, buôn, phum, sóc, tổ dân phố và điểm dân cư tương tự hoặc người được cộng đồng dân cư thỏa thuận cử ra.",
    "Người đại diện tổ chức tôn giáo, tổ chức tôn giáo trực thuộc đối với việc sử dụng đất của tổ chức tôn giáo, tổ chức tôn giáo trực thuộc.",
    "Cá nhân, người gốc Việt Nam định cư ở nước ngoài đối với việc sử dụng đất của mình.",
    "Người đại diện cho cộng đồng dân cư là ai ?"
]

for text in texts:
    print(f"\nTesting with text: {text}")
    predict(text)