# import json
# import numpy as np
# from datasets import Dataset
# from transformers import (
#     AutoTokenizer,
#     AutoConfig,
#     Trainer,
#     TrainingArguments,
#     DataCollatorForTokenClassification,
#     PreTrainedModel,
#     AutoModel
# )
# import torch
# import torch.nn as nn
# from transformers.modeling_outputs import TokenClassifierOutput
# from sklearn.metrics import precision_recall_fscore_support

# # 1. Định nghĩa mapping nhãn cho relation pair extraction (bài toán 3 loại)
# relation2id = {"0": 0, "1": 1, "2": 2}

# # 2. Hàm tính concept spans từ nhãn (token có nhãn khác 0 và -100 tạo thành 1 concept)
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

# # 3. Xây dựng custom joint model cho 3 nhiệm vụ: concept, relation token, và relation pair extraction
# class PhoBERTJointModel(PreTrainedModel):
#     config_class = AutoConfig

#     def __init__(self, config, num_labels, num_relation_token_labels, relation2id, lambda_relation=0.1):
#         super().__init__(config)
#         self.num_labels = num_labels                      # Nhiệm vụ nhận biết concept (token classification)
#         self.num_relation_token_labels = num_relation_token_labels  # Nhiệm vụ nhận biết relation ở mức token
#         self.relation2id = relation2id                    # Mapping cho relation pair extraction
#         self.num_relation_pair_labels = len(relation2id)
#         self.lambda_relation = lambda_relation            # Hệ số cân bằng loss cho relation pair extraction

#         # PhoBERT backbone
#         self.phobert = AutoModel.from_pretrained("vinai/phobert-base", config=config)
#         hidden_size = config.hidden_size
#         self.dropout = nn.Dropout(config.hidden_dropout_prob)
#         # Head cho nhận biết concept
#         self.concept_classifier = nn.Linear(hidden_size, num_labels)
#         # Head cho nhận biết relation ở mức token
#         self.token_relation_classifier = nn.Linear(hidden_size, num_relation_token_labels)
#         # Head cho relation pair extraction: kết hợp vector của 2 concept
#         self.relation_pair_classifier = nn.Sequential(
#             nn.Linear(2 * hidden_size, hidden_size),
#             nn.ReLU(),
#             nn.Linear(hidden_size, self.num_relation_pair_labels)
#         )
#         self.loss_fct = nn.CrossEntropyLoss(ignore_index=-100)

#     def forward(self, input_ids, attention_mask, labels=None, relation_labels=None,
#                 concept_spans_subword=None, relation_pairs=None):
#         outputs = self.phobert(input_ids=input_ids, attention_mask=attention_mask)
#         sequence_output = outputs.last_hidden_state  # [batch_size, seq_len, hidden_size]
#         sequence_output = self.dropout(sequence_output)
        
#         # Nhiệm vụ 1: Nhận biết concept (token classification)
#         concept_logits = self.concept_classifier(sequence_output)  # [batch_size, seq_len, num_labels]
#         loss_concept = None
#         if labels is not None:
#             loss_concept = self.loss_fct(concept_logits.view(-1, self.num_labels), labels.view(-1))
        
#         # Nhiệm vụ 2: Nhận biết relation ở mức token
#         token_relation_logits = self.token_relation_classifier(sequence_output)  # [batch_size, seq_len, num_relation_token_labels]
#         loss_relation_token = None
#         if relation_labels is not None:
#             loss_relation_token = self.loss_fct(token_relation_logits.view(-1, self.num_relation_token_labels),
#                                                   relation_labels.view(-1))
        
#         # Nhiệm vụ 3: Relation pair extraction (xác định mối quan hệ giữa các concept)
#         relation_logits_all = []
#         relation_labels_all = []
#         loss_relation_pair = None
#         if concept_spans_subword is not None and relation_pairs is not None:
#             batch_size = input_ids.size(0)
#             for i in range(batch_size):
#                 rep = sequence_output[i]  # [seq_len, hidden_size]
#                 spans = concept_spans_subword[i]  # Danh sách tuple (start, end)
#                 concept_reps = []
#                 for span in spans:
#                     start, end = span
#                     if end > start:
#                         pooled = rep[start:end].mean(dim=0)
#                     else:
#                         pooled = rep[0]
#                     concept_reps.append(pooled)
#                 if len(concept_reps) == 0:
#                     continue
#                 concept_reps = torch.stack(concept_reps, dim=0)  # [num_concepts, hidden_size]
#                 for rel in relation_pairs[i]:
#                     src = rel["source"]
#                     tgt = rel["target"]
#                     if src < concept_reps.size(0) and tgt < concept_reps.size(0):
#                         rep_src = concept_reps[src]
#                         rep_tgt = concept_reps[tgt]
#                         pair_rep = torch.cat([rep_src, rep_tgt], dim=-1)
#                         logits_rel = self.relation_pair_classifier(pair_rep)  # [num_relation_pair_labels]
#                         relation_logits_all.append(logits_rel.unsqueeze(0))
#                         rel_label_str = str(rel.get("label", rel.get("rel_type", "0")))
#                         rel_label_id = self.relation2id.get(rel_label_str, 0)
#                         relation_labels_all.append(torch.tensor(rel_label_id, device=input_ids.device).unsqueeze(0))
#             if relation_logits_all:
#                 relation_logits_all = torch.cat(relation_logits_all, dim=0)
#                 relation_labels_all = torch.cat(relation_labels_all, dim=0)
#                 loss_relation_pair = self.loss_fct(relation_logits_all, relation_labels_all)
        
#         total_loss = 0
#         if loss_concept is not None:
#             total_loss += loss_concept
#         if loss_relation_token is not None:
#             total_loss += loss_relation_token
#         if loss_relation_pair is not None:
#             total_loss += self.lambda_relation * loss_relation_pair

#         # Quan trọng: trả về "logits" để Trainer sử dụng cho compute_metrics
#         return TokenClassifierOutput(loss=total_loss, logits=concept_logits)

# # 4. Chuẩn bị dữ liệu từ file JSON
# with open("training_data_for_phobert.json", "r", encoding="utf-8") as f:
#     data = json.load(f)

# # File JSON của bạn là danh sách các record, nên dùng from_list
# dataset = Dataset.from_list(data)

# if len(dataset) > 1:
#     split_dataset = dataset.train_test_split(test_size=0.2, seed=42)
#     train_dataset = split_dataset["train"]
#     val_dataset = split_dataset["test"]
# else:
#     train_dataset = dataset
#     val_dataset = dataset

# # 5. Load tokenizer và cấu hình model
# tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base", use_fast=True)
# config = AutoConfig.from_pretrained("vinai/phobert-base")
# num_labels = 3                   # Nhận biết concept (0: non-entity, 1 và 2 là entity)
# num_relation_token_labels = 3    # Nhận biết relation ở mức token (0, 1, 2)

# model = PhoBERTJointModel(config, num_labels=num_labels, num_relation_token_labels=num_relation_token_labels,
#                            relation2id=relation2id)

# # 6. Hàm xử lý dữ liệu: lấy các trường cần thiết cho huấn luyện
# def preprocess_function(example):
#     return {
#         "input_ids": example["input_ids"],
#         "attention_mask": example["attention_mask"],
#         "labels": example["labels"],
#         "relation_labels": example["relation_labels"],
#         "concept_spans_subword": compute_concept_spans(example["labels"]),
#         "relation_pairs": example.get("relation_pairs", [])
#     }

# train_dataset = train_dataset.map(preprocess_function)
# val_dataset = val_dataset.map(preprocess_function)

# # 7. Custom data collator: đảm bảo các trường phụ được truyền qua Trainer
# def custom_data_collator(features):
#     extra_fields = {
#         "concept_spans_subword": [f["concept_spans_subword"] for f in features],
#         "relation_pairs": [f["relation_pairs"] for f in features],
#         "relation_labels": [f["relation_labels"] for f in features]
#     }
#     features_for_collator = [
#         {k: v for k, v in f.items() if k not in ["concept_spans_subword", "relation_pairs", "relation_labels"]}
#         for f in features
#     ]
#     batch = DataCollatorForTokenClassification(tokenizer, padding=True)(features_for_collator)
#     batch["concept_spans_subword"] = extra_fields["concept_spans_subword"]
#     batch["relation_pairs"] = extra_fields["relation_pairs"]
#     max_len = max(len(x) for x in extra_fields["relation_labels"])
#     padded_relation_labels = [x + [-100]*(max_len - len(x)) for x in extra_fields["relation_labels"]]
#     batch["relation_labels"] = torch.tensor(padded_relation_labels, dtype=torch.long)
#     return batch

# # 8. Hàm compute_metrics sử dụng mảng NumPy cho việc tính metric
# def compute_metrics(p):
#     preds, labels = p
#     preds = np.array(preds)
#     labels = np.array(labels)
#     preds = np.argmax(preds, axis=2)
#     # Nếu tổng số phần tử của labels gấp đôi preds, downsample labels
#     if labels.size == preds.size * 2:
#          # Giả sử labels có shape (batch_size, seq_len*2)
#          # ta reshape lại và lấy mỗi token thứ 2
#          labels = labels.reshape(preds.shape[0], -1)[:, ::2]
#     preds = preds.flatten()
#     labels = labels.flatten()
#     mask = labels != -100
#     true_preds = preds[mask]
#     true_labels = labels[mask]
#     precision, recall, f1, _ = precision_recall_fscore_support(true_labels, true_preds, average="macro")
#     return {"precision": precision, "recall": recall, "f1": f1}




# # 9. Cấu hình TrainingArguments
# training_args = TrainingArguments(
#     output_dir="./phobert-joint",
#     num_train_epochs=30,
#     per_device_train_batch_size=25,
#     per_device_eval_batch_size=15,
#     evaluation_strategy="epoch",
#     save_strategy="epoch",
#     save_total_limit=3,
#     logging_dir="./logs",
#     learning_rate=2e-3,
#     weight_decay=0.001,
#     max_grad_norm=1.0,
#     warmup_steps=1500,
#     lr_scheduler_type="cosine"
# )

# trainer = Trainer(
#     model=model,
#     args=training_args,
#     train_dataset=train_dataset,
#     eval_dataset=val_dataset,
#     tokenizer=tokenizer,
#     data_collator=custom_data_collator,
#     compute_metrics=compute_metrics,
# )

# trainer.train()
# trainer.evaluate()
# trainer.save_model("./phobert-joint-finetuned")

















# #######################################################


# import json
# import torch
# import torch.nn as nn
# import torch.optim as optim
# from torch.utils.data import Dataset, DataLoader
# from transformers import AutoModel, logging

# logging.set_verbosity_error()

# NUM_ENTITY_LABELS = 3    # O, B-Concept, I-Concept
# NUM_RELATION_LABELS = 3  # O, B-Relation, I-Relation

# # Định nghĩa lớp Dataset
# class PhoBERTDataset(Dataset):
#     def __init__(self, json_file):
#         with open(json_file, 'r', encoding='utf-8') as f:
#             self.samples = json.load(f)
    
#     def __len__(self):
#         return len(self.samples)
    
#     def __getitem__(self, idx):
#         sample = self.samples[idx]
#         item = {
#             "input_ids": torch.tensor(sample["input_ids"], dtype=torch.long),
#             "attention_mask": torch.tensor(sample["attention_mask"], dtype=torch.long),
#             "labels": torch.tensor(sample["labels"], dtype=torch.long),
#             "relation_labels": torch.tensor(sample["relation_labels"], dtype=torch.long),
#             "relation_pairs": sample.get("relation_pairs", []),
#             "text": sample["text"]
#         }
#         return item

# # Định nghĩa mô hình đa nhiệm PhoBERT
# class PhoBERTMultiTaskModel(nn.Module):
#     def __init__(self, num_entity_labels, num_relation_labels):
#         super(PhoBERTMultiTaskModel, self).__init__()
#         self.phobert = AutoModel.from_pretrained("vinai/phobert-base", cache_dir="D:/Cache-hunging-face")
#         hidden_size = self.phobert.config.hidden_size
#         self.entity_classifier = nn.Linear(hidden_size, num_entity_labels)          # Phân loại thực thể
#         self.token_relation_classifier = nn.Linear(hidden_size, num_relation_labels)  # Phân loại token quan hệ
#         self.relation_classifier = nn.Linear(hidden_size * 3, num_relation_labels)  # Phân loại quan hệ dựa trên cặp
    
#     def forward(self, input_ids, attention_mask, entity_labels=None, relation_labels=None, relation_pairs=None):
#         # Lấy đầu ra từ PhoBERT
#         outputs = self.phobert(input_ids=input_ids, attention_mask=attention_mask)
#         sequence_output = outputs.last_hidden_state
        
#         # Phân loại thực thể
#         entity_logits = self.entity_classifier(sequence_output)
        
#         # Phân loại token quan hệ
#         token_relation_logits = self.token_relation_classifier(sequence_output)
        
#         # Tính loss cho phân loại thực thể
#         loss_entity = None
#         if entity_labels is not None:
#             loss_fct = nn.CrossEntropyLoss(ignore_index=-100)
#             loss_entity = loss_fct(entity_logits.view(-1, entity_logits.size(-1)), entity_labels.view(-1))
        
#         # Tính loss cho phân loại token quan hệ
#         loss_relation_token = None
#         if relation_labels is not None:
#             loss_fct = nn.CrossEntropyLoss(ignore_index=-100)
#             loss_relation_token = loss_fct(token_relation_logits.view(-1, token_relation_logits.size(-1)), relation_labels.view(-1))
        
#         # Phân loại quan hệ dựa trên cặp
#         loss_relation = None
#         all_relation_logits = []
#         all_relation_labels = []
#         if relation_pairs is not None:
#             for i, rel_list in enumerate(relation_pairs):
#                 if len(rel_list) == 0:
#                     continue
#                 for rel in rel_list:
#                     src_idx = rel["source"]
#                     rel_idx = rel["relation"]
#                     tgt_idx = rel["target"]
#                     src_repr = sequence_output[i, src_idx, :]
#                     rel_repr = sequence_output[i, rel_idx, :]
#                     tgt_repr = sequence_output[i, tgt_idx, :]
#                     combined = torch.cat([src_repr, rel_repr, tgt_repr], dim=-1)
#                     logits = self.relation_classifier(combined)
#                     all_relation_logits.append(logits)
#                     all_relation_labels.append(rel["rel_type"])
#             if all_relation_logits:  # Kiểm tra xem list có rỗng hay không
#                 all_relation_logits_tensor = torch.stack(all_relation_logits, dim=0)
#                 all_relation_labels_tensor = torch.tensor(all_relation_labels, dtype=torch.long, device=all_relation_logits_tensor.device)
#                 loss_fct_relation = nn.CrossEntropyLoss()
#                 loss_relation = loss_fct_relation(all_relation_logits_tensor, all_relation_labels_tensor)
        
#         # Tổng hợp loss
#         losses = []
#         if loss_entity is not None:
#             losses.append(loss_entity)
#         if loss_relation_token is not None:
#             losses.append(loss_relation_token)
#         if loss_relation is not None:
#             losses.append(loss_relation)
#         total_loss = sum(losses) if losses else None
        
#         # Trả về kết quả
#         return {
#             "loss": total_loss,
#             "entity_logits": entity_logits,
#             "token_relation_logits": token_relation_logits,
#             "relation_logits": all_relation_logits if len(all_relation_logits) > 0 else None
#         }

# # Hàm huấn luyện mô hình
# def train_model(model, dataloader, optimizer, device, num_epochs=3):
#     model.train()
#     for epoch in range(num_epochs):
#         running_loss = 0.0
#         for batch in dataloader:
#             optimizer.zero_grad()
#             input_ids = batch["input_ids"].to(device)
#             attention_mask = batch["attention_mask"].to(device)
#             labels = batch["labels"].to(device)
#             rel_labels = batch["relation_labels"].to(device)
#             relation_pairs = batch["relation_pairs"]
#             outputs = model(
#                 input_ids=input_ids,
#                 attention_mask=attention_mask,
#                 entity_labels=labels,
#                 relation_labels=rel_labels,
#                 relation_pairs=relation_pairs
#             )
#             loss = outputs["loss"]
#             if loss is not None:
#                 loss.backward()
#                 optimizer.step()
#                 running_loss += loss.item()
#         print(f"Epoch {epoch+1}/{num_epochs}, Loss: {running_loss/len(dataloader):.4f}")

# # Khởi chạy chương trình chính
# if __name__ == "__main__":
#     json_file = "training_data_for_phobert.json"
#     dataset = PhoBERTDataset(json_file)
#     dataloader = DataLoader(dataset, batch_size=2, shuffle=True, collate_fn=lambda x: {
#         "input_ids": torch.nn.utils.rnn.pad_sequence([item["input_ids"] for item in x], batch_first=True, padding_value=1),
#         "attention_mask": torch.nn.utils.rnn.pad_sequence([item["attention_mask"] for item in x], batch_first=True, padding_value=0),
#         "labels": torch.nn.utils.rnn.pad_sequence([item["labels"] for item in x], batch_first=True, padding_value=-100),
#         "relation_labels": torch.nn.utils.rnn.pad_sequence([item["relation_labels"] for item in x], batch_first=True, padding_value=-100),
#         "relation_pairs": [item["relation_pairs"] for item in x],
#         "text": [item["text"] for item in x]
#     })

#     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#     model = PhoBERTMultiTaskModel(num_entity_labels=NUM_ENTITY_LABELS, num_relation_labels=NUM_RELATION_LABELS)
#     model.to(device)
    
#     optimizer = optim.AdamW(model.parameters(), lr=2e-4)
#     num_epochs = 20
#     train_model(model, dataloader, optimizer, device, num_epochs=num_epochs)

#     torch.save(model.state_dict(), "phobert_multitask_model.pt")
#     print("Model saved to phobert_multitask_model.pt")
    
#     model.phobert.save_pretrained("phobert_multitask_checkpoint")
#     torch.save(model.entity_classifier.state_dict(), "entity_classifier.pt")
#     torch.save(model.relation_classifier.state_dict(), "relation_classifier.pt")
#     print("Checkpoint saved!")


###########################################################################


# import json
# import torch
# import torch.nn as nn
# import torch.optim as optim
# from torch.utils.data import Dataset, DataLoader
# from transformers import AutoModel, AutoTokenizer
# import numpy as np
# from sklearn.metrics import precision_recall_fscore_support

# # Thiết lập tham số
# NUM_ENTITY_LABELS = 3    # O, B-Concept, I-Concept
# NUM_RELATION_LABELS = 3  # O, B-Relation, I-Relation
# DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# # 1. Dataset
# class PhoBERTDataset(Dataset):
#     def __init__(self, json_file):
#         with open(json_file, 'r', encoding='utf-8') as f:
#             self.samples = json.load(f)
    
#     def __len__(self):
#         return len(self.samples)
    
#     def __getitem__(self, idx):
#         sample = self.samples[idx]
#         return {
#             "input_ids": torch.tensor(sample["input_ids"], dtype=torch.long),
#             "attention_mask": torch.tensor(sample["attention_mask"], dtype=torch.long),
#             "labels": torch.tensor(sample["labels"], dtype=torch.long),
#             "relation_labels": torch.tensor(sample["relation_labels"], dtype=torch.long),
#             "relation_pairs": sample.get("relation_pairs", []),
#             "text": sample["text"]
#         }

# # 2. Model
# class PhoBERTMultiTaskModel(nn.Module):
#     def __init__(self, num_entity_labels, num_relation_labels):
#         super(PhoBERTMultiTaskModel, self).__init__()
#         self.phobert = AutoModel.from_pretrained("vinai/phobert-base", cache_dir="D:/Cache-hunging-face")
#         hidden_size = self.phobert.config.hidden_size
#         self.dropout = nn.Dropout(0.1)
#         self.entity_classifier = nn.Linear(hidden_size, num_entity_labels)
#         self.token_relation_classifier = nn.Linear(hidden_size, num_relation_labels)
#         self.relation_classifier = nn.Linear(hidden_size * 3, num_relation_labels)
    
#     def forward(self, input_ids, attention_mask, entity_labels=None, relation_labels=None, relation_pairs=None):
#         outputs = self.phobert(input_ids=input_ids, attention_mask=attention_mask)
#         sequence_output = self.dropout(outputs.last_hidden_state)

#         entity_logits = self.entity_classifier(sequence_output)
#         loss_entity = None
#         if entity_labels is not None:
#             loss_fct = nn.CrossEntropyLoss(ignore_index=-100)
#             loss_entity = loss_fct(entity_logits.view(-1, entity_logits.size(-1)), entity_labels.view(-1))

#         token_relation_logits = self.token_relation_classifier(sequence_output)
#         loss_relation_token = None
#         if relation_labels is not None:
#             loss_fct = nn.CrossEntropyLoss(ignore_index=-100)
#             loss_relation_token = loss_fct(token_relation_logits.view(-1, token_relation_logits.size(-1)), relation_labels.view(-1))

#         loss_relation = None
#         relation_logits_list = []
#         relation_labels_list = []
#         if relation_pairs is not None:
#             for i, rel_list in enumerate(relation_pairs):
#                 if not rel_list:
#                     continue
#                 sample_logits = []
#                 sample_labels = []
#                 for rel in rel_list:
#                     src_idx = rel["source"]
#                     rel_idx = rel["relation"]
#                     tgt_idx = rel["target"]
#                     src_repr = sequence_output[i, src_idx, :]
#                     rel_repr = sequence_output[i, rel_idx, :]
#                     tgt_repr = sequence_output[i, tgt_idx, :]
#                     combined = torch.cat([src_repr, rel_repr, tgt_repr], dim=-1)
#                     logits = self.relation_classifier(combined)
#                     sample_logits.append(logits)
#                     sample_labels.append(rel["rel_type"])
#                 if sample_logits:
#                     sample_logits = torch.stack(sample_logits, dim=0)
#                     relation_logits_list.append(sample_logits)
#                     relation_labels_list.extend(sample_labels)

#             if relation_logits_list:
#                 all_relation_logits = torch.cat(relation_logits_list, dim=0)
#                 all_relation_labels = torch.tensor(relation_labels_list, dtype=torch.long, device=input_ids.device)
#                 loss_fct = nn.CrossEntropyLoss()
#                 loss_relation = loss_fct(all_relation_logits, all_relation_labels)

#         total_loss = 0
#         if loss_entity is not None:
#             total_loss += loss_entity
#         if loss_relation_token is not None:
#             total_loss += loss_relation_token
#         if loss_relation is not None:
#             total_loss += 0.5 * loss_relation

#         return {
#             "loss": total_loss,
#             "entity_logits": entity_logits,
#             "token_relation_logits": token_relation_logits,
#             "relation_logits": relation_logits_list if relation_logits_list else None,
#             "sequence_output": sequence_output
#         }

# # 3. Hàm tính concept spans (đã sửa)
# def compute_concept_spans(labels):
#     spans = []
#     start = None
#     for i, label in enumerate(labels):
#         if label == 1:  # B-Concept
#             if start is not None:
#                 spans.append((start, i))
#             start = i
#         elif label == 2 and start is not None:  # I-Concept, chỉ tiếp tục nếu đã có B-Concept
#             continue
#         elif label == 0 or label == -100:  # O hoặc padding
#             if start is not None:
#                 spans.append((start, i))
#                 start = None
#     if start is not None:
#         spans.append((start, len(labels)))
#     return spans

# # 4. Hàm huấn luyện
# def train_model(model, dataloader, optimizer, device, num_epochs=20):
#     model.train()
#     for epoch in range(num_epochs):
#         running_loss = 0.0
#         all_entity_preds, all_entity_labels = [], []
#         all_relation_preds, all_relation_labels = [], []
#         all_triplet_preds, all_triplet_labels = [], []

#         for batch_idx, batch in enumerate(dataloader):
#             optimizer.zero_grad()
#             input_ids = batch["input_ids"].to(device)
#             attention_mask = batch["attention_mask"].to(device)
#             entity_labels = batch["labels"].to(device)
#             rel_labels = batch["relation_labels"].to(device)
#             relation_pairs = batch["relation_pairs"]

#             outputs = model(
#                 input_ids=input_ids,
#                 attention_mask=attention_mask,
#                 entity_labels=entity_labels,
#                 relation_labels=rel_labels,
#                 relation_pairs=relation_pairs
#             )
#             loss = outputs["loss"]
#             if loss is not None:
#                 loss.backward()
#                 optimizer.step()
#                 running_loss += loss.item()

#             entity_preds = torch.argmax(outputs["entity_logits"], dim=-1).cpu().numpy()
#             entity_labels_np = entity_labels.cpu().numpy()
#             rel_preds = torch.argmax(outputs["token_relation_logits"], dim=-1).cpu().numpy()
#             rel_labels_np = rel_labels.cpu().numpy()

#             for i in range(len(input_ids)):
#                 mask = entity_labels_np[i] != -100
#                 all_entity_preds.extend(entity_preds[i][mask])
#                 all_entity_labels.extend(entity_labels_np[i][mask])
#                 mask = rel_labels_np[i] != -100
#                 all_relation_preds.extend(rel_preds[i][mask])
#                 all_relation_labels.extend(rel_labels_np[i][mask])

#             if outputs["relation_logits"] and relation_pairs:
#                 for logits, rels in zip(outputs["relation_logits"], relation_pairs):
#                     if rels:
#                         preds = torch.argmax(logits, dim=-1).cpu().numpy()
#                         labels = [rel["rel_type"] for rel in rels]
#                         if len(preds) == len(labels):
#                             all_triplet_preds.extend(preds)
#                             all_triplet_labels.extend(labels)

#         avg_loss = running_loss / len(dataloader)
#         entity_prec, entity_rec, entity_f1, _ = precision_recall_fscore_support(all_entity_labels, all_entity_preds, average="macro", zero_division=0)
#         rel_prec, rel_rec, rel_f1, _ = precision_recall_fscore_support(all_relation_labels, all_relation_preds, average="macro", zero_division=0)
        
#         triplet_prec, triplet_rec, triplet_f1 = 0, 0, 0
#         if all_triplet_preds and all_triplet_labels and len(all_triplet_preds) == len(all_triplet_labels):
#             triplet_prec, triplet_rec, triplet_f1, _ = precision_recall_fscore_support(all_triplet_labels, all_triplet_preds, average="macro", zero_division=0)

#         print(f"Epoch {epoch+1}/{num_epochs}, Loss: {avg_loss:.4f}")
#         print(f"Concept - Precision: {entity_prec:.4f}, Recall: {entity_rec:.4f}, F1: {entity_f1:.4f}")
#         print(f"Relation Token - Precision: {rel_prec:.4f}, Recall: {rel_rec:.4f}, F1: {rel_f1:.4f}")
#         print(f"Triplet - Precision: {triplet_prec:.4f}, Recall: {triplet_rec:.4f}, F1: {triplet_f1:.4f}")

# # 5. Hàm suy luận (đã cải thiện)
# def predict(model, tokenizer, text, device):
#     model.eval()
#     inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=256)
#     input_ids = inputs["input_ids"].to(device)
#     attention_mask = inputs["attention_mask"].to(device)

#     with torch.no_grad():
#         outputs = model(input_ids=input_ids, attention_mask=attention_mask)

#     entity_logits = outputs["entity_logits"][0].cpu().numpy()
#     entity_preds = np.argmax(entity_logits, axis=-1)
#     concept_spans = compute_concept_spans(entity_preds)

#     token_relation_logits = outputs["token_relation_logits"][0].cpu().numpy()
#     relation_preds = np.argmax(token_relation_logits, axis=-1)
#     relation_indices = [i for i, pred in enumerate(relation_preds) if pred in [1, 2]]

#     sequence_output = outputs["sequence_output"][0]  # [seq_len, hidden_size]
#     triplets = []
#     if len(concept_spans) >= 2:
#         for i in range(len(concept_spans) - 1):
#             start1, end1 = concept_spans[i]
#             start2, end2 = concept_spans[i + 1]
#             # Tìm token quan hệ giữa hai concept
#             rel_idx = None
#             for idx in relation_indices:
#                 if end1 <= idx < start2:
#                     rel_idx = idx
#                     break
#             if rel_idx is not None:
#                 src_repr = sequence_output[start1:end1].mean(dim=0) if end1 > start1 else sequence_output[start1]
#                 rel_repr = sequence_output[rel_idx]
#                 tgt_repr = sequence_output[start2:end2].mean(dim=0) if end2 > start2 else sequence_output[start2]
#                 combined = torch.cat([src_repr, rel_repr, tgt_repr], dim=0).unsqueeze(0)
#                 logit = model.relation_classifier(combined)
#                 pred = torch.argmax(logit).item()
#                 if pred > 0:
#                     triplets.append({
#                         "source": (start1, end1),
#                         "relation": rel_idx,
#                         "target": (start2, end2),
#                         "rel_type": pred
#                     })

#     tokens = tokenizer.convert_ids_to_tokens(input_ids[0])
#     result = {
#         "concepts": [(tokens[start:end], start, end) for start, end in concept_spans],
#         "relations": [(tokens[idx], idx) for idx in relation_indices],
#         "triplets": [(tokens[t["source"][0]:t["source"][1]], tokens[t["relation"]], tokens[t["target"][0]:t["target"][1]]) for t in triplets]
#     }
#     print("Entity Predictions:", entity_preds)
#     print("Relation Predictions:", relation_preds)
#     return result

# # 6. Main
# if __name__ == "__main__":
#     # Load data
#     json_file = "training_data_for_phobert.json"
#     dataset = PhoBERTDataset(json_file)
#     dataloader = DataLoader(dataset, batch_size=2, shuffle=True, collate_fn=lambda x: {
#         "input_ids": torch.nn.utils.rnn.pad_sequence([item["input_ids"] for item in x], batch_first=True, padding_value=1),
#         "attention_mask": torch.nn.utils.rnn.pad_sequence([item["attention_mask"] for item in x], batch_first=True, padding_value=0),
#         "labels": torch.nn.utils.rnn.pad_sequence([item["labels"] for item in x], batch_first=True, padding_value=-100),
#         "relation_labels": torch.nn.utils.rnn.pad_sequence([item["relation_labels"] for item in x], batch_first=True, padding_value=-100),
#         "relation_pairs": [item["relation_pairs"] for item in x],
#         "text": [item["text"] for item in x]
#     })

#     # Khởi tạo model và optimizer
#     model = PhoBERTMultiTaskModel(num_entity_labels=NUM_ENTITY_LABELS, num_relation_labels=NUM_RELATION_LABELS)
#     model.to(DEVICE)
#     optimizer = optim.AdamW(model.parameters(), lr=2e-4)

#     # Huấn luyện
#     train_model(model, dataloader, optimizer, DEVICE, num_epochs=20)

#     # Lưu model
#     torch.save(model.state_dict(), "phobert_multitask_model.pt")
#     model.phobert.save_pretrained("phobert_multitask_checkpoint")
#     torch.save(model.entity_classifier.state_dict(), "entity_classifier.pt")
#     torch.save(model.relation_classifier.state_dict(), "relation_classifier.pt")
#     print("Model saved!")

#     # Suy luận thử
#     tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base", cache_dir="D:/Cache-hunging-face")
#     text = "Người đại diện theo pháp luật của tổ chức trong nước, tổ chức kinh tế có vốn đầu tư nước ngoài; người đứng đầu của tổ chức nước ngoài có chức năng ngoại giao đối với việc sử dụng đất của tổ chức mình."
#     result = predict(model, tokenizer, text, DEVICE)
#     print("\nInference Result:")
#     print("Concepts:", result["concepts"])
#     print("Relation Tokens:", result["relations"])
#     print("Triplets:", result["triplets"])





##############################################

import json
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from torch.nn.utils.rnn import pad_sequence
from transformers import RobertaModel, AdamW
from torch.optim import AdamW

# Định nghĩa dataset
class JointDataset(Dataset):
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]

# Hàm collate_fn để padding các tensor trong batch
def collate_fn(batch):
    input_ids = [item["input_ids"] for item in batch]
    attention_mask = [item["attention_mask"] for item in batch]
    concept_labels = [item["concept_labels"] for item in batch]
    relation_labels = [item["relation_labels"] for item in batch]
    relation_pairs = [item["relation_pairs"] for item in batch]

    input_ids = pad_sequence(input_ids, batch_first=True, padding_value=1)  # 1 là ID của [PAD] trong phoBERT
    attention_mask = pad_sequence(attention_mask, batch_first=True, padding_value=0)
    concept_labels = pad_sequence(concept_labels, batch_first=True, padding_value=-100)  # -100 để bỏ qua trong loss
    relation_labels = pad_sequence(relation_labels, batch_first=True, padding_value=-100)

    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "concept_labels": concept_labels,
        "relation_labels": relation_labels,
        "relation_pairs": relation_pairs
    }

# Định nghĩa mô hình
class JointModel(nn.Module):
    def __init__(self, num_concept_labels=3, num_relation_labels=3, num_rel_types=1):
        super().__init__()
        self.phobert = RobertaModel.from_pretrained("vinai/phobert-base", cache_dir="D:/Cache-hunging-face")
        self.hidden_size = 768
        
        # Đầu ra cho NER concepts
        self.concept_head = nn.Linear(self.hidden_size, num_concept_labels)
        
        # Đầu ra cho NER relations
        self.relation_head = nn.Linear(self.hidden_size, num_relation_labels)
        
        # Đầu ra cho phân loại quan hệ (dự đoán cặp source-target-relation)
        self.relation_classifier = nn.Linear(self.hidden_size * 3, num_rel_types)  # Kết hợp 3 vector

    def forward(self, input_ids, attention_mask, relation_pairs=None):
        outputs = self.phobert(input_ids, attention_mask=attention_mask)
        sequence_output = outputs.last_hidden_state  # [batch_size, seq_len, 768]
        
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
                    rel_idx = pair["relation"]  # Chỉ lấy chỉ số token duy nhất
                    tgt_start, tgt_end = pair["target"]
                    
                    src_vec = sequence_output[b, src_start:src_end + 1].mean(dim=0)  # [768]
                    rel_vec = sequence_output[b, rel_idx]  # Lấy vector tại chỉ số rel_idx, [768]
                    tgt_vec = sequence_output[b, tgt_start:tgt_end + 1].mean(dim=0)  # [768]
                    
                    combined_vec = torch.cat([src_vec, rel_vec, tgt_vec], dim=0)  # [768 * 3]
                    relation_features.append(combined_vec)
            
            if relation_features:
                relation_features = torch.stack(relation_features)  # [num_pairs, 768 * 3]
                relation_pred = self.relation_classifier(relation_features)
            else:
                relation_pred = None
        else:
            relation_pred = None
        
        return concept_logits, relation_logits, relation_pred

# Chuẩn bị dữ liệu
with open("training_data_for_phobert.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

data = []
for record in raw_data:
    data.append({
        "input_ids": torch.tensor(record["input_ids"], dtype=torch.long),
        "attention_mask": torch.tensor(record["attention_mask"], dtype=torch.long),
        "concept_labels": torch.tensor(record["labels"], dtype=torch.long),
        "relation_labels": torch.tensor(record["relation_labels"], dtype=torch.long),
        "relation_pairs": record["relation_pairs"]
    })

# Tạo dataset và dataloader
dataset = JointDataset(data)
dataloader = DataLoader(dataset, batch_size=2, shuffle=True, collate_fn=collate_fn)

# Khởi tạo mô hình và optimizer
model = JointModel(num_concept_labels=3, num_relation_labels=3, num_rel_types=1)
optimizer = AdamW(model.parameters(), lr=2e-4)

# Huấn luyện
num_epochs = 15
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

for epoch in range(num_epochs):
    model.train()
    total_loss = 0
    for batch in dataloader:
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        concept_labels = batch["concept_labels"].to(device)
        relation_labels = batch["relation_labels"].to(device)
        relation_pairs = batch["relation_pairs"]
        
        # Forward pass
        concept_logits, relation_logits, relation_pred = model(input_ids, attention_mask, relation_pairs)
        
        # Loss cho concept NER
        concept_loss = nn.CrossEntropyLoss(ignore_index=-100)(concept_logits.view(-1, 3), concept_labels.view(-1))
        
        # Loss cho relation NER
        relation_loss = nn.CrossEntropyLoss(ignore_index=-100)(relation_logits.view(-1, 3), relation_labels.view(-1))
        
        # Loss cho phân loại quan hệ
        if relation_pred is not None:
            rel_labels = torch.tensor([pair["rel_type"] for b in range(len(relation_pairs)) 
                                      for pair in (relation_pairs[b] if isinstance(relation_pairs[b], list) 
                                                  else [relation_pairs[b]])], 
                                      dtype=torch.long).to(device)
            relation_loss_pair = nn.CrossEntropyLoss()(relation_pred, rel_labels)
        else:
            relation_loss_pair = torch.tensor(0.0).to(device)
        
        # Tổng loss
        loss = concept_loss + relation_loss + relation_loss_pair
        total_loss += loss.item()
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    
    print(f"Epoch {epoch + 1}, Loss: {total_loss / len(dataloader)}")

# Lưu mô hình
torch.save(model.state_dict(), "joint_model_full.pth")
print("Model saved to 'joint_model_full.pth'")
