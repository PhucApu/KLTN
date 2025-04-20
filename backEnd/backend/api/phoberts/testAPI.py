########## Bản chính thức ###################


import torch
from torch import nn
from transformers import RobertaTokenizerFast, RobertaModel

# Định nghĩa lớp mô hình (giữ nguyên)
class JointModel(nn.Module):
    def __init__(self, num_concept_labels=3, num_relation_labels=3, num_rel_types=1):
        super().__init__()
        self.phobert = RobertaModel.from_pretrained("vinai/phobert-base", cache_dir="./Cache-hunging-face")
        self.hidden_size = 768
        self.concept_head = nn.Linear(self.hidden_size, num_concept_labels)
        self.relation_head = nn.Linear(self.hidden_size, num_relation_labels)
        self.relation_classifier = nn.Linear(self.hidden_size * 3, num_rel_types)

    def forward(self, input_ids, attention_mask, relation_pairs=None):
        outputs = self.phobert(input_ids, attention_mask=attention_mask)
        sequence_output = outputs.last_hidden_state
        concept_logits = self.concept_head(sequence_output)
        relation_logits = self.relation_head(sequence_output)
        relation_pred = None
        if relation_pairs is not None and len(relation_pairs) > 0:
            pass
        return concept_logits, relation_logits, relation_pred

# Khởi tạo tokenizer và mô hình
tokenizer = RobertaTokenizerFast.from_pretrained("vinai/phobert-base", cache_dir="./Cache-hunging-face")
model = JointModel(num_concept_labels=3, num_relation_labels=3, num_rel_types=1)
model.load_state_dict(torch.load("joint_model_full.pth"))
model.eval()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Hàm phụ: Trích xuất spans từ nhãn BIO
def extract_spans(labels, attention_mask):
    spans = []
    current_span = []
    for i, (label, mask) in enumerate(zip(labels, attention_mask)):
        if mask == 0:  # Bỏ qua padding tokens
            continue
        if label == 1:  # B-X (Begin)
            if current_span:
                spans.append(current_span)
            current_span = [i]
        elif label == 2:  # I-X (Inside)
            if current_span:
                current_span.append(i)
        else:  # O (Outside)
            if current_span:
                spans.append(current_span)
                current_span = []
    if current_span:
        spans.append(current_span)
    return spans

# Hàm phụ: Tìm concept gần nhất trước và sau relation
def find_closest_concepts(relation_span, concept_spans):
    relation_start = relation_span[0]
    relation_end = relation_span[-1]
    left_concepts = [span for span in concept_spans if span[-1] < relation_start]
    right_concepts = [span for span in concept_spans if span[0] > relation_end]
    left_concept = max(left_concepts, key=lambda span: span[-1]) if left_concepts else None
    right_concept = min(right_concepts, key=lambda span: span[0]) if right_concepts else None
    return left_concept, right_concept

# Hàm phụ: Chuyển span token thành văn bản từ câu gốc
def span_to_text(span, input_ids, sentence, offset_mapping):
    if not span:
        return ""
    start_idx = span[0]
    end_idx = span[-1]
    start_char = offset_mapping[start_idx][0]
    end_char = offset_mapping[end_idx][1]
    text = sentence[start_char:end_char].strip()
    return text

# Function 1: Nhận diện concepts
def identify_concepts(sentence):
    encoding = tokenizer(sentence, padding=True, truncation=True, return_tensors="pt", return_offsets_mapping=True)
    input_ids = encoding['input_ids'].to(device)
    attention_mask = encoding['attention_mask'].to(device)
    offset_mapping = encoding['offset_mapping'][0].cpu().numpy()

    with torch.no_grad():
        concept_logits, _, _ = model(input_ids, attention_mask)
        concept_preds = torch.argmax(concept_logits, dim=-1)[0]

    concept_spans = extract_spans(concept_preds.cpu().numpy(), attention_mask[0].cpu().numpy())
    concepts = [span_to_text(span, input_ids[0], sentence, offset_mapping) for span in concept_spans]
    return concepts

# Function 2: Nhận diện relations
def identify_relations(sentence):
    encoding = tokenizer(sentence, padding=True, truncation=True, return_tensors="pt", return_offsets_mapping=True)
    input_ids = encoding['input_ids'].to(device)
    attention_mask = encoding['attention_mask'].to(device)
    offset_mapping = encoding['offset_mapping'][0].cpu().numpy()

    with torch.no_grad():
        _, relation_logits, _ = model(input_ids, attention_mask)
        relation_preds = torch.argmax(relation_logits, dim=-1)[0]

    relation_spans = extract_spans(relation_preds.cpu().numpy(), attention_mask[0].cpu().numpy())
    relations = [span_to_text(span, input_ids[0], sentence, offset_mapping) for span in relation_spans]
    return relations

# Function 3: Nhận diện bộ ba Concept1-Relation-Concept2
def identify_triples(sentence):
    encoding = tokenizer(sentence, padding=True, truncation=True, return_tensors="pt", return_offsets_mapping=True)
    input_ids = encoding['input_ids'].to(device)
    attention_mask = encoding['attention_mask'].to(device)
    offset_mapping = encoding['offset_mapping'][0].cpu().numpy()

    with torch.no_grad():
        concept_logits, relation_logits, _ = model(input_ids, attention_mask)
        concept_preds = torch.argmax(concept_logits, dim=-1)[0]
        relation_preds = torch.argmax(relation_logits, dim=-1)[0]

    concept_spans = extract_spans(concept_preds.cpu().numpy(), attention_mask[0].cpu().numpy())
    relation_spans = extract_spans(relation_preds.cpu().numpy(), attention_mask[0].cpu().numpy())

    triples = []
    for rel_span in relation_spans:
        left_concept, right_concept = find_closest_concepts(rel_span, concept_spans)
        if left_concept and right_concept:
            c1_text = span_to_text(left_concept, input_ids[0], sentence, offset_mapping)
            r_text = span_to_text(rel_span, input_ids[0], sentence, offset_mapping)
            c2_text = span_to_text(right_concept, input_ids[0], sentence, offset_mapping)
            triples.append([c1_text, r_text, c2_text])

    return triples

# Ví dụ sử dụng
if __name__ == "__main__":
    test_sentence = "Quỳnh đi học ở trường đại học sài gòn SGU"
    print('\n\n\n')
    print("Concepts:", identify_concepts(test_sentence))
    print("Relations:", identify_relations(test_sentence))
    print("Triples:", identify_triples(test_sentence))