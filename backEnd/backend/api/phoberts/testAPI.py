########## Bản chính thức ###################

import torch
from torch import nn
from transformers import PhobertTokenizer, RobertaModel

# Định nghĩa lớp mô hình (giữ nguyên)
class JointModel(nn.Module):
    def __init__(self, num_concept_labels=3, num_relation_labels=3, num_rel_types=1):
        super().__init__()
        self.phobert = RobertaModel.from_pretrained("vinai/phobert-base", cache_dir="Cache-hunging-face")
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
            pass  # Giữ nguyên logic xử lý relation_pairs nếu có
        return concept_logits, relation_logits, relation_pred

# Khởi tạo tokenizer và mô hình
tokenizer = PhobertTokenizer.from_pretrained("vinai/phobert-base",use_fast=False, cache_dir="Cache-hunging-face")
model = JointModel(num_concept_labels=3, num_relation_labels=3, num_rel_types=1)
# model.load_state_dict(torch.load("joint_model_best.pth"))

# nếu chạy bằng cpu thì mở comand ra
# model.load_state_dict(torch.load("joint_model_best.pth", map_location=torch.device('cpu')))
model.load_state_dict(torch.load("C:\\Users\\baoqu\\Desktop\\KLTN\\Test\\backEnd\\backend\\api\\phoberts\\joint_model_best.pth", map_location=torch.device('cpu')))

model.eval()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Hàm phụ: Trích xuất spans từ nhãn BIO
def extract_spans(labels, attention_mask):
    spans = []
    current_span = []
    for i in range(len(labels)):  # Duyệt qua tất cả token trong text_labels
        if attention_mask[i] == 0:  # Bỏ qua padding
            continue
        label = labels[i]
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

# Hàm phụ: Làm sạch văn bản (loại bỏ @@ và thay thế <unk>)
def clean_text(text):
    text = text.replace('@@', '')  # Loại bỏ ký tự @@
    text = text.replace('<unk>', '')  # Thay <unk> bằng [UNK] hoặc chuỗi khác nếu muốn
    return text.strip()

# Hàm phụ: Chuyển span token thành văn bản từ danh sách token
def span_to_text(span, text_tokens):
    if not span:
        return ""
    start_idx = span[0]
    end_idx = span[-1]
    span_tokens = text_tokens[start_idx:end_idx + 1]
    text = tokenizer.convert_tokens_to_string(span_tokens)
    text = clean_text(text)  # Làm sạch văn bản sau khi chuyển đổi
    return text.strip()

# Hàm phụ: Chia câu thành các chunk nhỏ hơn
def split_sentence(sentence, max_tokens=256):
    words = sentence.split()
    chunks = []
    current_chunk = []
    for word in words:
        current_chunk.append(word)
        temp_text = " ".join(current_chunk)
        temp_tokens = tokenizer.encode(temp_text, add_special_tokens=True)
        if len(temp_tokens) > max_tokens:
            if len(current_chunk) > 1:
                current_chunk.pop()
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
            else:
                chunks.append(word)
                current_chunk = []
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

# Function 1: Nhận diện concepts
def identify_concepts(sentence):
    tokens = tokenizer.encode(sentence, add_special_tokens=True)
    chunks = split_sentence(sentence)
    all_concepts = []
    for chunk in chunks:
        encoding = tokenizer(chunk, padding=True, truncation=True, max_length=256, return_tensors="pt")
        input_ids = encoding['input_ids'].to(device)
        attention_mask = encoding['attention_mask'].to(device)
        
        full_tokens = tokenizer.convert_ids_to_tokens(input_ids[0].cpu().numpy())
        text_tokens = full_tokens[1:-1]  # Loại bỏ <s> và </s>
        text_attention_mask = attention_mask[0, 1:-1].cpu().numpy()
        
        with torch.no_grad():
            concept_logits, _, _ = model(input_ids, attention_mask)
            concept_preds = torch.argmax(concept_logits, dim=-1)[0]
        
        text_labels = concept_preds[1:-1].cpu().numpy()
        concept_spans = extract_spans(text_labels, text_attention_mask)
        concepts = [span_to_text(span, text_tokens) for span in concept_spans]
        all_concepts.extend(concepts)
    
    all_concepts = list(set(all_concepts))
    return all_concepts

# Function 2: Nhận diện relations
def identify_relations(sentence):
    tokens = tokenizer.encode(sentence, add_special_tokens=True)
    chunks = split_sentence(sentence)
    all_relations = []
    for chunk in chunks:
        encoding = tokenizer(chunk, padding=True, truncation=True, max_length=256, return_tensors="pt")
        input_ids = encoding['input_ids'].to(device)
        attention_mask = encoding['attention_mask'].to(device)
        
        full_tokens = tokenizer.convert_ids_to_tokens(input_ids[0].cpu().numpy())
        text_tokens = full_tokens[1:-1]  # Loại bỏ <s> và </s>
        text_attention_mask = attention_mask[0, 1:-1].cpu().numpy()
        
        with torch.no_grad():
            _, relation_logits, _ = model(input_ids, attention_mask)
            relation_preds = torch.argmax(relation_logits, dim=-1)[0]
        
        text_labels = relation_preds[1:-1].cpu().numpy()
        relation_spans = extract_spans(text_labels, text_attention_mask)
        relations = [span_to_text(span, text_tokens) for span in relation_spans]
        all_relations.extend(relations)
    
    all_relations = list(set(all_relations))
    return all_relations

# Function 3: Nhận diện bộ ba Concept1-Relation-Concept2
def identify_triples(sentence):
    tokens = tokenizer.encode(sentence, add_special_tokens=True)
    chunks = split_sentence(sentence)
    all_triples = []
    for chunk in chunks:
        encoding = tokenizer(chunk, padding=True, truncation=True, max_length=256, return_tensors="pt")
        input_ids = encoding['input_ids'].to(device)
        attention_mask = encoding['attention_mask'].to(device)
        
        full_tokens = tokenizer.convert_ids_to_tokens(input_ids[0].cpu().numpy())
        text_tokens = full_tokens[1:-1]  # Loại bỏ <s> và </s>
        text_attention_mask = attention_mask[0, 1:-1].cpu().numpy()
        
        with torch.no_grad():
            concept_logits, relation_logits, _ = model(input_ids, attention_mask)
            concept_preds = torch.argmax(concept_logits, dim=-1)[0]
            relation_preds = torch.argmax(relation_logits, dim=-1)[0]
        
        concept_text_labels = concept_preds[1:-1].cpu().numpy()
        relation_text_labels = relation_preds[1:-1].cpu().numpy()
        concept_spans = extract_spans(concept_text_labels, text_attention_mask)
        relation_spans = extract_spans(relation_text_labels, text_attention_mask)
        
        for rel_span in relation_spans:
            left_concept, right_concept = find_closest_concepts(rel_span, concept_spans)
            if left_concept and right_concept:
                c1_text = span_to_text(left_concept, text_tokens)
                r_text = span_to_text(rel_span, text_tokens)
                c2_text = span_to_text(right_concept, text_tokens)
                all_triples.append([c1_text, r_text, c2_text])
    
    return all_triples

# Ví dụ sử dụng
if __name__ == "__main__":
    test_sentence = "Ủy ban nhân dân cấp xã chủ trì, phối hợp với Ủy ban Mặt trận Tổ quốc Việt Nam cấp xã nơi có đất thu hồi và đơn vị, tổ chức thực hiện nhiệm vụ bồi thường, hỗ trợ, tái định cư vận động, thuyết phục để người có đất thu hồi, chủ sở hữu tài sản gắn liền với đất, người có quyền lợi và nghĩa vụ liên quan bàn giao đất cho đơn vị, tổ chức thực hiện nhiệm vụ bồi thường, hỗ trợ, tái định cư"
    print("Concepts:", identify_concepts(test_sentence))
    print("Relations:", identify_relations(test_sentence))
    print("Triples:", identify_triples(test_sentence))  
    
    
