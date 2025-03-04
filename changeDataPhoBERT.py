import json
from transformers import PreTrainedTokenizerFast

# Định nghĩa mapping nhãn cho NER
label2id = {"O": 0, "B-Concept": 1, "I-Concept": 2}

def read_extended_conll_file(file_path):
    """
    Đọc file CoNLL mở rộng với cấu trúc:
      - Các dòng token: token_index, token, label.
      - Một block "# Concepts:" với các dòng: concept_index, concept_text, start, end.
      - Một block "# Relations:" với các dòng: source_index, target_index, relation_label.
    Trả về danh sách các mẫu với cấu trúc:
      {
        "tokens": [token1, token2, ...],
        "labels": [label1, label2, ...],
        "concepts": [ { "index": int, "text": str, "start": int, "end": int }, ... ],
        "relations": [ { "source": int, "target": int, "label": str }, ... ]
      }
    """
    samples = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [line.rstrip("\n") for line in f]
    
    i = 0
    while i < len(lines):
        # Bỏ qua dòng trắng
        while i < len(lines) and lines[i].strip() == "":
            i += 1
        if i >= len(lines):
            break
        sample = {"tokens": [], "labels": [], "concepts": [], "relations": []}
        # Đọc block token (dòng không bắt đầu bằng dấu "#")
        while i < len(lines) and lines[i].strip() != "":
            line = lines[i].strip()
            if line.startswith("#"):
                break
            parts = line.split("\t")
            if len(parts) >= 3:
                token = parts[1]
                label = parts[2]
                sample["tokens"].append(token)
                sample["labels"].append(label)
            i += 1
        # Bỏ qua dòng trắng
        while i < len(lines) and lines[i].strip() == "":
            i += 1
        # Đọc block concepts nếu có
        if i < len(lines) and lines[i].strip().startswith("# Concepts:"):
            i += 1  # bỏ qua dòng "# Concepts:"
            while i < len(lines) and lines[i].strip() != "":
                parts = lines[i].strip().split("\t")
                if len(parts) >= 4:
                    concept_index = int(parts[0])
                    concept_text = parts[1]
                    start = int(parts[2])
                    end = int(parts[3])
                    sample["concepts"].append({
                        "index": concept_index,
                        "text": concept_text,
                        "start": start,
                        "end": end
                    })
                i += 1
        # Bỏ qua dòng trắng
        while i < len(lines) and lines[i].strip() == "":
            i += 1
        # Đọc block relations nếu có
        if i < len(lines) and lines[i].strip().startswith("# Relations:"):
            i += 1  # bỏ qua dòng "# Relations:"
            while i < len(lines) and lines[i].strip() != "":
                parts = lines[i].strip().split("\t")
                if len(parts) >= 3:
                    source = int(parts[0])
                    target = int(parts[1])
                    rel_label = parts[2]
                    sample["relations"].append({
                        "source": source,
                        "target": target,
                        "label": rel_label
                    })
                i += 1
        # Bỏ qua dòng trắng trước khi chuyển sang mẫu tiếp theo
        while i < len(lines) and lines[i].strip() == "":
            i += 1
        samples.append(sample)
    return samples

def compute_token_offsets(tokens):
    """
    Tính toán offset cho mỗi token khi ghép các token bằng khoảng trắng.
    Trả về list các tuple (start, end) cho mỗi token.
    """
    offsets = []
    current = 0
    for token in tokens:
        start = current
        end = start + len(token)
        offsets.append((start, end))
        current = end + 1  # cộng thêm khoảng trắng
    return offsets

def get_concept_token_span(concept, token_offsets):
    """
    Với một concept có offset ký tự (concept["start"], concept["end"]) trong văn bản gốc,
    và danh sách token_offsets của danh sách token gốc (từ " ".join(tokens)),
    xác định phạm vi token (start_token, end_token) mà concept bao phủ.
    Nếu không tìm thấy token phù hợp, trả về None.
    """
    c_start = concept["start"]
    c_end = concept["end"]
    indices = []
    for i, (t_start, t_end) in enumerate(token_offsets):
        # Nếu token nằm hoàn toàn trong phạm vi concept
        if t_start >= c_start and t_end <= c_end:
            indices.append(i)
    if indices:
        return (indices[0], indices[-1] + 1)
    return None

def convert_for_training(conll_file, output_json):
    """
    Chuyển dữ liệu từ file CoNLL mở rộng sang định dạng training cho pipeline huấn luyện của PhoBERT.
    Mỗi mẫu bao gồm:
      - input_ids, attention_mask, labels (cho nhiệm vụ NER)
      - concept_spans_subword: danh sách các cặp (start, end) của các concept (theo chỉ số subword)
      - relation_pairs: danh sách các quan hệ giữa các concept (theo thứ tự của concept trong danh sách)
      - original_tokens: danh sách token gốc từ file CoNLL
    """
    samples = read_extended_conll_file(conll_file)
    tokenizer = PreTrainedTokenizerFast.from_pretrained("vinai/phobert-base")
    
    training_examples = []
    
    for sample in samples:
        tokens = sample["tokens"]
        labels = sample["labels"]
        original_text = " ".join(tokens)  # giả sử ghép các token bằng khoảng trắng
        
        # Tính toán offset cho token gốc theo cách ghép trên
        token_offsets = compute_token_offsets(tokens)
        
        # Dùng fast tokenizer với is_split_into_words=True để token hóa lại danh sách token gốc
        encoded = tokenizer(tokens, is_split_into_words=True, return_offsets_mapping=True, truncation=True)
        word_ids = encoded.word_ids()  # mapping từ các subword token đến chỉ số token gốc
        
        # Căn chỉnh lại nhãn cho token subword
        new_labels = []
        previous_word_idx = None
        for word_idx in word_ids:
            if word_idx is None:
                new_labels.append(-100)
            elif word_idx != previous_word_idx:
                new_labels.append(label2id.get(labels[word_idx], 0))
            else:
                new_labels.append(-100)
            previous_word_idx = word_idx
        
        # Với mỗi concept (theo thông tin ký tự trong sample["concepts"]), chuyển sang phạm vi token gốc
        concept_token_spans = []
        for concept in sample["concepts"]:
            span = get_concept_token_span(concept, token_offsets)
            # Nếu không tìm được, ta bỏ qua concept đó (hoặc có thể set span = (0,0))
            if span is not None:
                concept_token_spans.append(span)
            else:
                concept_token_spans.append((0, 0))
        
        # Dựa vào mapping word_ids, chuyển các phạm vi concept từ token gốc sang subword.
        concept_spans_subword = []
        for span in concept_token_spans:
            start_token, end_token = span
            subword_indices = [j for j, wid in enumerate(word_ids) if wid is not None and start_token <= wid < end_token]
            if subword_indices:
                concept_spans_subword.append((subword_indices[0], subword_indices[-1] + 1))
            else:
                concept_spans_subword.append((0, 0))
        
        # Lấy danh sách quan hệ như cũ (relation_pairs)
        relation_pairs = sample["relations"]
        
        training_examples.append({
            "input_ids": encoded["input_ids"],
            "attention_mask": encoded["attention_mask"],
            "labels": new_labels,
            "concept_spans_subword": concept_spans_subword,
            "relation_pairs": relation_pairs,
            "original_tokens": tokens,
            "text": sample.get("text", original_text)  # nếu có trường text
        })
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(training_examples, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    conll_file = "training_data.conll"                   # File dữ liệu CoNLL mở rộng đã có
    output_json = "training_data_for_phobert.json"         # File đầu ra cho pipeline huấn luyện
    convert_for_training(conll_file, output_json)
