import json
import numpy as np
from datasets import Dataset
from transformers import (
    AutoTokenizer,
    AutoConfig,
    Trainer,
    TrainingArguments,
    DataCollatorForTokenClassification,
    PreTrainedModel,
    AutoModel
)
import torch
import torch.nn as nn
from transformers.modeling_outputs import TokenClassifierOutput
from sklearn.metrics import precision_recall_fscore_support

# 1. Xây dựng custom joint model cho NER và relation extraction

class PhoBERTJointModel(PreTrainedModel):
    config_class = AutoConfig

    def __init__(self, config, num_labels, relation2id, lambda_relation=0.001):
        super().__init__(config)
        self.num_labels = num_labels
        self.relation2id = relation2id
        self.num_relation_labels = len(relation2id)
        self.lambda_relation = lambda_relation  # Hệ số cân bằng loss relation
        self.phobert = AutoModel.from_pretrained("vinai/phobert-base", config=config)
        hidden_size = config.hidden_size
        self.dropout = nn.Dropout(config.hidden_dropout_prob)
        self.classifier = nn.Linear(hidden_size, num_labels)
        self.relation_classifier = nn.Sequential(
            nn.Linear(2 * hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, self.num_relation_labels)
        )
        self.loss_fct = nn.CrossEntropyLoss(ignore_index=-100)

    def forward(self, input_ids, attention_mask, labels=None, concept_spans_subword=None, relation_pairs=None):
        outputs = self.phobert(input_ids=input_ids, attention_mask=attention_mask)
        sequence_output = outputs.last_hidden_state
        sequence_output = self.dropout(sequence_output)
        token_logits = self.classifier(sequence_output)
        
        total_loss = None
        loss_token = None
        loss_relation = None

        if labels is not None:
            loss_token = self.loss_fct(token_logits.view(-1, self.num_labels), labels.view(-1))
            total_loss = loss_token

        relation_logits_all = []
        relation_labels_all = []
        if concept_spans_subword is not None and relation_pairs is not None:
            batch_size = input_ids.size(0)
            for i in range(batch_size):
                rep = sequence_output[i]
                spans = concept_spans_subword[i]
                concept_reps = []
                for span in spans:
                    start, end = span
                    if end > start:
                        pooled = rep[start:end].mean(dim=0)
                    else:
                        pooled = rep[0]
                    concept_reps.append(pooled)
                if len(concept_reps) == 0:
                    continue
                concept_reps = torch.stack(concept_reps, dim=0)
                for rel in relation_pairs[i]:
                    src = rel["source"]
                    tgt = rel["target"]
                    if src < concept_reps.size(0) and tgt < concept_reps.size(0):
                        rep_src = concept_reps[src]
                        rep_tgt = concept_reps[tgt]
                        pair_rep = torch.cat([rep_src, rep_tgt], dim=-1)
                        logits_rel = self.relation_classifier(pair_rep)
                        relation_logits_all.append(logits_rel.unsqueeze(0))
                        rel_label_str = rel["label"]
                        rel_label_id = self.relation2id.get(rel_label_str, 0)
                        relation_labels_all.append(torch.tensor(rel_label_id, device=input_ids.device).unsqueeze(0))
            if relation_logits_all:
                relation_logits_all = torch.cat(relation_logits_all, dim=0)
                relation_labels_all = torch.cat(relation_labels_all, dim=0)
                loss_relation = self.loss_fct(relation_logits_all, relation_labels_all)
                total_loss = loss_token + self.lambda_relation * loss_relation if total_loss is not None else loss_relation
        
        return TokenClassifierOutput(loss=total_loss, logits=token_logits)

# Định nghĩa mapping nhãn cho NER và relation extraction


# BS-Concept : bắt đầu cụm chủ ngữ
# IS-Concept: mấy từ tiếp theo của bên trên

# B-Relation: bắt đầu cụm quan hệ. 
# I-Relation

# BO-Concept:  bắt đầu cụm vị ngữ
# BI-Concept:  






label2id = {"O": 0, "B-Concept": 1, "I-Concept": 2}
relation2id = {
    "thể hiện": 0,
    "lập": 1,
    "xác nhận": 2,
    "là": 3,
    "tại": 4,
    "trả lại": 5,
    "xác định": 6,
    "cho": 7,
    "đã được": 8,
    "tác động": 9,
    "đầu tư": 10,
    "đến": 11,
    "sử dụng": 12,
    "không cho phép": 13,
    "thực hiện": 14
}

# 2. Chuẩn bị dữ liệu

with open("training_data_for_phobert.json", "r", encoding="utf-8") as f:
    data = json.load(f)

dataset = Dataset.from_dict({"data": data})

if len(dataset) > 1:
    split_dataset = dataset.train_test_split(test_size=0.2, seed=42)
    train_dataset = split_dataset["train"]
    val_dataset = split_dataset["test"]
else:
    train_dataset = dataset
    val_dataset = dataset

# 3. Load tokenizer và cấu hình model

tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base", use_fast=True)
config = AutoConfig.from_pretrained("vinai/phobert-base")
num_labels = 3

# Khởi tạo mô hình joint
model = PhoBERTJointModel(config, num_labels=num_labels, relation2id=relation2id)

# 4. Hàm xử lý dữ liệu: chuyển các trường cần thiết từ file JSON
def preprocess_function(example):
    return {
        "input_ids": example["data"]["input_ids"],
        "attention_mask": example["data"]["attention_mask"],
        "labels": example["data"]["labels"],
        "concept_spans_subword": example["data"]["concept_spans_subword"],
        "relation_pairs": example["data"]["relation_pairs"]
    }

train_dataset = train_dataset.map(preprocess_function, remove_columns=["data"])
val_dataset = val_dataset.map(preprocess_function, remove_columns=["data"])

# 5. Custom data collator: đảm bảo các trường extra được truyền qua
def custom_data_collator(features):
    extra_fields = {
        "concept_spans_subword": [f["concept_spans_subword"] for f in features],
        "relation_pairs": [f["relation_pairs"] for f in features]
    }
    features_for_collator = [
        {k: v for k, v in f.items() if k not in ["concept_spans_subword", "relation_pairs"]}
        for f in features
    ]
    batch = DataCollatorForTokenClassification(tokenizer, padding=True)(features_for_collator)
    batch["concept_spans_subword"] = extra_fields["concept_spans_subword"]
    batch["relation_pairs"] = extra_fields["relation_pairs"]
    return batch

# 6. Hàm tính metrics cho nhiệm vụ NER (relation extraction có thể đánh giá riêng)
def compute_metrics(p):
    predictions, labels = p
    predictions = np.argmax(predictions, axis=2)
    true_labels = []
    true_preds = []
    for pred, label in zip(predictions, labels):
        for p_val, l_val in zip(pred, label):
            if l_val != -100:
                true_labels.append(l_val)
                true_preds.append(p_val)
    precision, recall, f1, _ = precision_recall_fscore_support(true_labels, true_preds, average="macro")
    return {"precision": precision, "recall": recall, "f1": f1}

# 7. Cấu hình huấn luyện với adaptive techniques: thêm gradient clipping và warmup_steps cho scheduler
training_args = TrainingArguments(
    output_dir="./phobert-joint",
    num_train_epochs=50,  # tăng số epoch để học sâu hơn
    per_device_train_batch_size=20,  # giảm batch size để cập nhật chi tiết hơn
    per_device_eval_batch_size=20,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    save_total_limit=1,
    logging_dir="./logs",
    learning_rate=2e-4,    # giảm learning rate
    weight_decay=0.1,     # tăng weight decay
    max_grad_norm=1.0,
    warmup_steps=1000,     # tăng số bước warmup
    lr_scheduler_type="cosine"
)


trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    tokenizer=tokenizer,
    data_collator=custom_data_collator,
    compute_metrics=compute_metrics,
)

# Huấn luyện, đánh giá và lưu mô hình
trainer.train()
trainer.evaluate()
trainer.save_model("./phobert-joint-finetuned")
