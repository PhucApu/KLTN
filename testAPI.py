import torch
import safetensors.torch
from transformers import PreTrainedTokenizerFast, AutoConfig, AutoModel
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import string
import os

# Mapping nhãn từ số sang chữ cho NER
label_map = {0: "O", 1: "B-CONCEPT", 2: "I-CONCEPT"}

# Mapping quan hệ: cập nhật theo tập dữ liệu của bạn
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
# Inverse mapping cho relation
inv_relation2id = {v: k for k, v in relation2id.items()}

# Lớp mô hình joint cho NER và relation extraction.
# Phương thức from_pretrained sẽ load trọng số từ file "model.safetensors" sử dụng safetensors.
class PhoBERTJointModel(torch.nn.Module):
    def __init__(self, config, num_labels, relation2id, lambda_relation=0.5):
        super().__init__()
        self.num_labels = num_labels
        self.relation2id = relation2id
        self.num_relation_labels = len(relation2id)
        self.lambda_relation = lambda_relation
        self.phobert = AutoModel.from_pretrained("vinai/phobert-base", config=config)
        hidden_size = config.hidden_size
        self.dropout = torch.nn.Dropout(config.hidden_dropout_prob)
        self.classifier = torch.nn.Linear(hidden_size, num_labels)
        self.relation_classifier = torch.nn.Sequential(
            torch.nn.Linear(2 * hidden_size, hidden_size),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_size, self.num_relation_labels)
        )
        self.loss_fct = torch.nn.CrossEntropyLoss(ignore_index=-100)

    @classmethod
    def from_pretrained(cls, pretrained_model_dir, **kwargs):
        config = kwargs.get("config", AutoConfig.from_pretrained("vinai/phobert-base"))
        num_labels = kwargs.get("num_labels", 3)
        relation2id = kwargs.get("relation2id", {})
        lambda_relation = kwargs.get("lambda_relation", 0.5)
        model = cls(config, num_labels, relation2id, lambda_relation)
        # Load file safetensors
        safetensors_path = os.path.join(pretrained_model_dir, "model.safetensors")
        if not os.path.exists(safetensors_path):
            raise FileNotFoundError(f"Không tìm thấy file model.safetensors tại: {safetensors_path}")
        state_dict = safetensors.torch.load_file(safetensors_path, device="cpu")
        model.load_state_dict(state_dict)
        return model

    def forward(self, input_ids, attention_mask, labels=None, concept_spans_subword=None, relation_pairs=None):
        outputs = self.phobert(input_ids=input_ids, attention_mask=attention_mask)
        sequence_output = outputs.last_hidden_state  # (batch, seq_len, hidden_size)
        sequence_output = self.dropout(sequence_output)
        token_logits = self.classifier(sequence_output)
        total_loss = None
        if labels is not None:
            loss_token = self.loss_fct(token_logits.view(-1, self.num_labels), labels.view(-1))
            total_loss = loss_token
        # Ở inference, ta chỉ trả về token_logits; loss relation không được tính.
        return token_logits

# Load mô hình joint đã fine-tuned từ file safetensors
model_path = "phobert-joint-finetuned"  # Thư mục chứa model.safetensors
config = AutoConfig.from_pretrained("vinai/phobert-base")
model = PhoBERTJointModel.from_pretrained(model_path, config=config, num_labels=3, relation2id=relation2id)
model.eval()  # Chế độ đánh giá
tokenizer = PreTrainedTokenizerFast.from_pretrained("vinai/phobert-base")

def extract_concepts_relations(text: str, gap_threshold: int = 3):
    """
    Hàm thực hiện:
      1. Tokenize văn bản, lấy offset và dự đoán nhãn token cho NER.
      2. Nhóm các token thành các concept dựa trên nhãn B/I-CONCEPT, lưu lại vị trí ký tự và token_range.
      3. Tính toán subword_span cho mỗi concept (giả sử token hiện tại là subword).
      4. Với mỗi cặp concept (không lặp lại), dùng head relation để dự đoán mối quan hệ.
    Trả về dict gồm "concepts" và "relations".
    """
    encoding = tokenizer(text, return_offsets_mapping=True, return_tensors="pt", truncation=True)
    input_ids = encoding["input_ids"]
    attention_mask = encoding["attention_mask"]
    offsets = encoding["offset_mapping"][0].tolist()  # danh sách (start, end) cho mỗi token/subword
    
    with torch.no_grad():
        outputs = model.phobert(input_ids=input_ids, attention_mask=attention_mask)
    sequence_output = outputs.last_hidden_state[0]  # (seq_len, hidden_size)
    
    token_logits = model.classifier(model.dropout(sequence_output))
    predictions = torch.argmax(token_logits, dim=1).tolist()
    tokens = tokenizer.convert_ids_to_tokens(input_ids[0])
    
    # Loại bỏ token đặc biệt ở đầu và cuối nếu có
    if tokens and tokens[0] in tokenizer.all_special_tokens:
        tokens = tokens[1:]
        offsets = offsets[1:]
        predictions = predictions[1:]
    if tokens and tokens[-1] in tokenizer.all_special_tokens:
        tokens = tokens[:-1]
        offsets = offsets[:-1]
        predictions = predictions[:-1]
    
    punctuation = set(string.punctuation)
    concepts = []
    current_concept = None
    current_token_range = None

    for i, (token, pred, (start, end)) in enumerate(zip(tokens, predictions, offsets)):
        if end <= start:
            continue
        label = label_map.get(pred, "O")
        if current_concept is None:
            if all(char in string.digits + string.punctuation for char in token):
                continue
        if token in punctuation:
            if current_concept is not None:
                concepts.append({
                    "concept": text[current_concept["start"]: offsets[i-1][1]],
                    "start": current_concept["start"],
                    "end": offsets[i-1][1],
                    "token_range": (current_token_range[0], i)
                })
                current_concept = None
                current_token_range = None
            continue
        if label == "B-CONCEPT":
            if current_concept is not None:
                concepts.append({
                    "concept": text[current_concept["start"]: offsets[i-1][1]],
                    "start": current_concept["start"],
                    "end": offsets[i-1][1],
                    "token_range": (current_token_range[0], i)
                })
            current_concept = {"start": start, "end": end}
            current_token_range = (i, i+1)
        elif label == "I-CONCEPT":
            if current_concept is not None:
                if start - current_concept["end"] > gap_threshold:
                    concepts.append({
                        "concept": text[current_concept["start"]: offsets[i-1][1]],
                        "start": current_concept["start"],
                        "end": offsets[i-1][1],
                        "token_range": (current_token_range[0], i)
                    })
                    current_concept = {"start": start, "end": end}
                    current_token_range = (i, i+1)
                else:
                    current_concept["end"] = end
                    current_token_range = (current_token_range[0], i+1)
            else:
                current_concept = {"start": start, "end": end}
                current_token_range = (i, i+1)
        else:  # label == "O"
            if current_concept is not None:
                concepts.append({
                    "concept": text[current_concept["start"]: offsets[i-1][1]],
                    "start": current_concept["start"],
                    "end": offsets[i-1][1],
                    "token_range": (current_token_range[0], i)
                })
                current_concept = None
                current_token_range = None
    if current_concept is not None:
        concepts.append({
            "concept": text[current_concept["start"]: offsets[-1][1]],
            "start": current_concept["start"],
            "end": offsets[-1][1],
            "token_range": (current_token_range[0], len(tokens))
        })
    
    # Giả định rằng các token hiện tại chính là subword token, nên subword_span = token_range
    for concept in concepts:
        token_start, token_end = concept["token_range"]
        concept["subword_span"] = (token_start, token_end)
    
    # Tính toán quan hệ: Duyệt qua các cặp concept khác nhau
    relations = []
    if len(concepts) > 1:
        for i in range(len(concepts)):
            for j in range(len(concepts)):
                if i != j:
                    span_i = concepts[i]["subword_span"]
                    span_j = concepts[j]["subword_span"]
                    if span_i[1] > span_i[0] and span_j[1] > span_j[0]:
                        rep_i = sequence_output[span_i[0]:span_i[1]].mean(dim=0)
                        rep_j = sequence_output[span_j[0]:span_j[1]].mean(dim=0)
                        pair_rep = torch.cat([rep_i, rep_j], dim=-1)
                        with torch.no_grad():
                            logits_rel = model.relation_classifier(pair_rep)
                        rel_pred_id = torch.argmax(logits_rel).item()
                        rel_label = inv_relation2id.get(rel_pred_id, "N/A")
                        relations.append({
                            "source": concepts[i]["concept"],
                            "target": concepts[j]["concept"],
                            "relation": rel_label
                        })
    return {"concepts": concepts, "relations": relations}

# Tạo API với FastAPI
app = FastAPI()

class TextInput(BaseModel):
    text: str

@app.post("/extract")
def extract_endpoint(text_input: TextInput):
    result = extract_concepts_relations(text_input.text)
    return result

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
