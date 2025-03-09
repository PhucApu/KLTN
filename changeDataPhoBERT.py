# import json
# from transformers import PreTrainedTokenizerFast
# from transformers import logging

# label2id_concept = {"O": 0, "B-Concept": 1, "I-Concept": 2}
# label2id_relation = {"O": 0, "B-Relation": 1, "I-Relation": 2}

# def read_extended_conll_file(file_path):
#     samples = []
#     with open(file_path, 'r', encoding='utf-8') as f:
#         lines = [line.rstrip("\n") for line in f]
#     i = 0
#     while i < len(lines):
#         # Bỏ qua các dòng trắng
#         while i < len(lines) and not lines[i].strip():
#             i += 1
#         if i >= len(lines):
#             break

#         sample = {"tokens": [], "concept_labels": [], "relation_labels": [], "relations": []}
#         # Đọc phần token và nhãn (dòng không bắt đầu bằng "#")
#         while i < len(lines) and lines[i].strip() and not lines[i].startswith("#"):
#             parts = lines[i].split("\t")
#             if len(parts) >= 6:
#                 token = parts[1]
#                 concept_label = parts[2]
#                 relation_label = parts[3]
#                 start_char = int(parts[4])
#                 end_char = int(parts[5])
#                 sample["tokens"].append({"token": token, "start_char": start_char, "end_char": end_char})
#                 sample["concept_labels"].append(concept_label)
#                 sample["relation_labels"].append(relation_label)
#             i += 1

#         # Bỏ qua các dòng trắng sau phần token
#         while i < len(lines) and not lines[i].strip():
#             i += 1

#         # Kiểm tra và đọc phần "# Relations:"
#         if i < len(lines) and lines[i].strip().startswith("# Relations:"):
#             i += 1  # bỏ qua header "# Relations:"
#             while i < len(lines):
#                 if not lines[i].strip():
#                     i += 1
#                     continue
#                 parts = lines[i].split("\t")
#                 if len(parts) == 3:
#                     sample["relations"].append({
#                         "concept1_start": int(parts[0]),
#                         "relation_start": int(parts[1]),
#                         "concept2_start": int(parts[2])
#                     })
#                 elif len(parts) == 2:
#                     # Xử lý nhóm quan hệ theo định dạng 2 cột
#                     group_concept1 = int(parts[0])
#                     group_relation = int(parts[1])
#                     i += 1
#                     group_relations = []
#                     while i < len(lines) and lines[i].strip() and len(lines[i].split("\t")) == 2:
#                         pair_parts = lines[i].split("\t")
#                         group_relations.append(int(pair_parts[1]))
#                         i += 1
#                     if group_relations:
#                         for c2 in group_relations:
#                             sample["relations"].append({
#                                 "concept1_start": group_concept1,
#                                 "relation_start": group_relation,
#                                 "concept2_start": c2
#                             })
#                     else:
#                         sample["relations"].append({
#                             "concept1_start": group_concept1,
#                             "relation_start": group_relation,
#                             "concept2_start": group_relation
#                         })
#                     continue
#                 else:
#                     break
#                 i += 1
#         samples.append(sample)
#     return samples

# def convert_for_training(conll_file, output_json):
#     samples = read_extended_conll_file(conll_file)
#     tokenizer = PreTrainedTokenizerFast.from_pretrained("vinai/phobert-base", cache_dir="D:/Cache-hunging-face")
#     training_examples = []
#     tolerance = 2  

#     print("====== START DEBUGGING ======")
#     for sample_idx, sample in enumerate(samples):
#         print(f"\n--- Sample {sample_idx} ---", flush=True)
#         tokens = sample["tokens"]
#         concept_labels = sample["concept_labels"]
#         relation_labels = sample["relation_labels"]
#         # Tái tạo text bằng cách nối token với dấu cách
#         token_texts = [t["token"] for t in tokens]
#         original_text = " ".join(token_texts)
#         print("Original text:", original_text, flush=True)

#         # In ra các offset ban đầu từ file CoNLL
#         token_offsets = [(t["start_char"], t["end_char"]) for t in tokens]
#         print("Token Offsets (gốc):", token_offsets, flush=True)

#         # Tokenize toàn bộ văn bản để lấy offset mapping toàn cục
#         encoded = tokenizer(original_text, return_offsets_mapping=True, truncation=True)
#         # Tự tính word_ids: với mỗi subword, nếu offset mapping nằm hoàn toàn trong khoảng của một token (theo file)
#         computed_word_ids = []
#         for offset in encoded["offset_mapping"]:
#             if offset[0] == offset[1]:
#                 computed_word_ids.append(None)
#                 continue
#             found = None
#             for idx, (tstart, tend) in enumerate(token_offsets):
#                 if offset[0] >= tstart and offset[1] <= tend:
#                     found = idx
#                     break
#             computed_word_ids.append(found)
#         print("Computed Word IDs:", computed_word_ids, flush=True)
#         print("Offset Mapping:", encoded["offset_mapping"], flush=True)
#         tokens_text = tokenizer.convert_ids_to_tokens(encoded["input_ids"])
#         print("Tokenized Tokens:", tokens_text, flush=True)

#         # Ánh xạ nhãn từ file theo computed_word_ids
#         new_concept_labels = [
#             label2id_concept.get(concept_labels[wid], 0) if wid is not None else -100
#             for wid in computed_word_ids
#         ]
#         new_relation_labels = [
#             label2id_relation.get(relation_labels[wid], 0) if wid is not None else -100
#             for wid in computed_word_ids
#         ]

#         # Tính derived_concepts dựa trên offset file (global)
#         derived_concepts = [
#             {"char_start": token_offsets[i][0], "token_index": i}
#             for i, lab in enumerate(concept_labels) if lab.startswith("B-")
#         ]
#         print("Derived Concepts:", derived_concepts, flush=True)

#         # Xử lý các quan hệ và in ra thông tin debug cho từng quan hệ
#         relation_pairs_index = []
#         for rel in sample["relations"]:
#             c1_char = rel["concept1_start"]
#             r_char = rel["relation_start"]
#             c2_char = rel["concept2_start"]
            
#             print(f"\nQuan hệ: c1_char={c1_char}, r_char={r_char}, c2_char={c2_char}", flush=True)
            
#             source_idx = next((idx for idx, c in enumerate(derived_concepts) if abs(c["char_start"] - c1_char) <= tolerance), None)
#             target_idx = next((idx for idx, c in enumerate(derived_concepts) if abs(c["char_start"] - c2_char) <= tolerance), None)
            
#             # Tìm subword token có offset mapping gần với r_char (toàn cục)
#             relation_subword_index = None
#             for j, (sub_start, sub_end) in enumerate(encoded["offset_mapping"]):
#                 if sub_start is None:
#                     continue
#                 print(f"Subword {j}: start={sub_start}, end={sub_end}", flush=True)
#                 if abs(sub_start - r_char) <= tolerance:
#                     relation_subword_index = j
#                     print(f" -> Tìm thấy subword index: {relation_subword_index}", flush=True)
#                     break
#             if relation_subword_index is None:
#                 print("Không tìm thấy subword index cho quan hệ này!", flush=True)
            
#             print("source_idx:", source_idx, "target_idx:", target_idx, "relation_subword_index:", relation_subword_index, flush=True)
            
#             if relation_subword_index is not None:
#                 token_index = computed_word_ids[relation_subword_index]
#                 rel_label_text = relation_labels[token_index] if token_index is not None else "O"
#             else:
#                 rel_label_text = "O"
            
#             rel_type = label2id_relation.get(rel_label_text, 0)
#             if source_idx is not None and target_idx is not None and relation_subword_index is not None:
#                 relation_pairs_index.append({
#                     "source": source_idx,
#                     "relation": relation_subword_index,
#                     "target": target_idx,
#                     "rel_type": rel_type
#                 })
        
#         print("Relation Pairs:", relation_pairs_index, flush=True)
        
#         training_examples.append({
#             "input_ids": encoded["input_ids"],
#             "attention_mask": encoded["attention_mask"],
#             "labels": new_concept_labels,
#             "relation_labels": new_relation_labels,
#             "relation_pairs": relation_pairs_index,
#             "original_tokens": token_texts,
#             "text": original_text
#         })
    
#     with open(output_json, 'w', encoding='utf-8') as f:
#         json.dump(training_examples, f, ensure_ascii=False, indent=2)
#     print("\n====== END DEBUGGING ======", flush=True)

# if __name__ == "__main__":
#     conll_file = "training_data.conll"  # File CoNLL đã được chuyển thành .txt
#     output_json = "training_data_for_phobert.json"
    
#     logging.set_verbosity_error()  # Ẩn các cảnh báo của Transformers
#     convert_for_training(conll_file, output_json)




##########################################

import json
from transformers import RobertaTokenizerFast

# Tải tokenizer "fast"
tokenizer = RobertaTokenizerFast.from_pretrained("vinai/phobert-base", cache_dir="D:/Cache-hunging-face", add_prefix_space=True)
print(f"Using tokenizer: {type(tokenizer).__name__}, Is fast: {tokenizer.is_fast}")

# Ánh xạ nhãn
concept_label_map = {"O": 0, "B-Concept": 1, "I-Concept": 2}
relation_label_map = {"O": 0, "B-Relation": 1, "I-Relation": 2}

def get_token_index_from_char_position(tokens, char_pos):
    """Chuyển từ vị trí ký tự sang chỉ số token"""
    for i, token_obj in enumerate(tokens):
        if token_obj["start_char"] <= char_pos < token_obj["end_char"]:
            return i
        if i > 0 and tokens[i-1]["end_char"] <= char_pos <= token_obj["start_char"]:
            return i  # Nếu nằm giữa 2 token, lấy token tiếp theo
    return -1  # Không tìm thấy

def align_labels_with_subwords(original_labels, word_ids):
    """Căn chỉnh nhãn từ token gốc sang subword"""
    aligned_labels = []
    for word_id in word_ids:
        if word_id is None:  # Token đặc biệt ([CLS], [SEP])
            aligned_labels.append(-100)
        else:
            aligned_labels.append(original_labels[word_id])
    return aligned_labels

def extract_relation_pair(record, word_ids, tokens):
    """Chuyển đổi quan hệ sang chỉ số subword từ vị trí ký tự"""
    relation_pairs = []
    max_token_idx = max([wid for wid in word_ids if wid is not None])  # Chỉ số token lớn nhất
    print(f"  Processing relations: {len(record.get('relations', []))} relations found")
    
    for rel_idx, rel in enumerate(record.get("relations", [])):
        # Chuyển từ vị trí ký tự sang chỉ số token
        concept1_start_token = get_token_index_from_char_position(tokens, rel["concept1_start"])
        concept2_start_token = get_token_index_from_char_position(tokens, rel["concept2_start"])
        relation_start_token = get_token_index_from_char_position(tokens, rel["relation_start"])

        print(f"    Relation {rel_idx + 1}:")
        print(f"      concept1_start: {rel['concept1_start']} -> token_idx: {concept1_start_token}")
        print(f"      relation_start: {rel['relation_start']} -> token_idx: {relation_start_token}")
        print(f"      concept2_start: {rel['concept2_start']} -> token_idx: {concept2_start_token}")

        # Kiểm tra chỉ số có hợp lệ không
        if (concept1_start_token < 0 or concept1_start_token > max_token_idx or
            concept2_start_token < 0 or concept2_start_token > max_token_idx or
            relation_start_token < 0 or relation_start_token > max_token_idx):
            print(f"    Warning: Skipping relation due to invalid token index - {rel}")
            continue

        # Tìm chỉ số subword tương ứng
        try:
            source_idx = [i for i, wid in enumerate(word_ids) if wid == concept1_start_token][0]
            target_idx = [i for i, wid in enumerate(word_ids) if wid == concept2_start_token][0]
            relation_idx = [i for i, wid in enumerate(word_ids) if wid == relation_start_token][0]

            source_span = [source_idx, source_idx + 1]  # Giới hạn span là 2 subword
            target_span = [target_idx, target_idx + 1]  # Giới hạn span là 2 subword
            
            relation_pairs.append({
                "source": source_span,
                "relation": relation_idx,
                "target": target_span,
                "rel_type": 0
            })
            print(f"      Successfully mapped to subword indices: source={source_span}, relation={relation_idx}, target={target_span}")
        except IndexError:
            print(f"    Warning: Skipping relation due to index error - {rel}")
    return relation_pairs

def convert_record(record, record_idx):
    print(f"\nProcessing record {record_idx + 1}:")
    print(f"  Text: {record['text'][:50]}... (length: {len(record['text'])})")
    print(f"  Number of tokens: {len(record['tokens'])}")
    
    original_tokens = [token_obj["token"] for token_obj in record["tokens"]]
    labels = [concept_label_map[token_obj["concept_label"]] for token_obj in record["tokens"]]
    relation_labels = [relation_label_map[token_obj["relation_label"]] for token_obj in record["tokens"]]

    # Tokenize với phoBERT
    tokenized_input = tokenizer(original_tokens, is_split_into_words=True, return_tensors="pt", padding=True, truncation=True, max_length=256)
    input_ids = tokenized_input["input_ids"][0].tolist()
    attention_mask = tokenized_input["attention_mask"][0].tolist()
    word_ids = tokenized_input.word_ids(batch_index=0)
    print(f"  Number of subwords after tokenization: {len(input_ids)}")

    # Căn chỉnh nhãn với subword
    aligned_labels = align_labels_with_subwords(labels, word_ids)
    aligned_relation_labels = align_labels_with_subwords(relation_labels, word_ids)

    # Xử lý relation pairs
    try:
        relation_pairs = extract_relation_pair(record, word_ids, record["tokens"])  # Chỉ truyền 3 tham số
        print(f"  Number of valid relation pairs: {len(relation_pairs)}")
    except Exception as e:
        print(f"Error processing record {record_idx + 1}: {str(e)}")
        relation_pairs = []

    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "labels": aligned_labels,
        "relation_labels": aligned_relation_labels,
        "relation_pairs": relation_pairs,
        "original_tokens": original_tokens,
        "text": record["text"]
    }

def main():
    with open("VNCoreNLP/output.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"Total records loaded: {len(data)}")
    training_data = [convert_record(record, idx) for idx, record in enumerate(data)]
    
    with open("training_data_for_phobert.json", "w", encoding="utf-8") as f:
        json.dump(training_data, f, ensure_ascii=False, indent=2)
    print("Processing complete. Output saved to 'training_data_for_phobert.json'")

if __name__ == "__main__":
    main()