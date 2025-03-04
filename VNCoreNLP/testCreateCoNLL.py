# import json
# import re

# def simple_tokenize_with_spans(text):
#     """
#     Tokenize văn bản sử dụng biểu thức chính quy, tính toán chỉ số bắt đầu và kết thúc cho mỗi token.
#     """
#     tokens_with_info = []
#     for match in re.finditer(r'\S+', text):
#         token = match.group()
#         start = match.start()
#         end = match.end()
#         tokens_with_info.append({
#             "token": token,
#             "start_char": start,
#             "end_char": end
#         })
#     return tokens_with_info

# def get_concepts(annotations):
#     """
#     Trích xuất các concept từ annotation.
#     Mỗi concept được lấy từ phần annotation kiểu "labels" có nhãn "Concept".
#     Trả về một dictionary mapping: id concept -> thông tin (text, start, end)
#     """
#     concepts = {}
#     for ann in annotations:
#         for res in ann.get("result", []):
#             if res.get("type") == "labels":
#                 value = res.get("value", {})
#                 labels = value.get("labels", [])
#                 if "Concept" in labels:
#                     cid = res.get("id")
#                     concepts[cid] = {
#                         "text": value.get("text"),
#                         "start": value.get("start"),
#                         "end": value.get("end")
#                     }
#     return concepts

# def get_relations(annotations):
#     """
#     Trích xuất các quan hệ giữa concept từ annotation.
#     Mỗi quan hệ có kiểu "relation" với thông tin: from_id, to_id và label (lấy nhãn đầu tiên nếu có nhiều).
#     """
#     relations = []
#     for ann in annotations:
#         for res in ann.get("result", []):
#             if res.get("type") == "relation":
#                 relations.append({
#                     "from_id": res.get("from_id"),
#                     "to_id": res.get("to_id"),
#                     "label": res.get("labels", [None])[0]
#                 })
#     return relations

# def assign_bio_labels(tokens_with_info, concepts):
#     """
#     Gán nhãn BIO cho các token dựa trên khoảng span của các concept.
#       - "B-Concept": Token bắt đầu chính xác tại vị trí bắt đầu của concept.
#       - "I-Concept": Token nằm trong khoảng của concept nhưng không phải token đầu tiên.
#       - "O": Token không thuộc bất kỳ concept nào.
#     """
#     for token in tokens_with_info:
#         start = token["start_char"]
#         end = token["end_char"]
#         label = "O"
#         for concept in concepts.values():
#             if start >= concept["start"] and end <= concept["end"]:
#                 label = "B-Concept" if start == concept["start"] else "I-Concept"
#                 break
#         token["label"] = label
#     return tokens_with_info

# def process_file(input_file, output_file):
#     with open(input_file, 'r', encoding='utf-8') as f:
#         data = json.load(f)

#     output_data = []

#     for sample in data:
#         text = sample["data"]["text"]
#         # Tokenize văn bản bằng hàm đơn giản
#         tokens = simple_tokenize_with_spans(text)
        
#         # Lấy annotation từ sample
#         annotations = sample.get("annotations", [])
        
#         # Trích xuất các concept và quan hệ
#         concepts = get_concepts(annotations)
#         relations = get_relations(annotations)
        
#         # Gán nhãn BIO cho các token dựa trên khoảng của concept
#         tokens_with_labels = assign_bio_labels(tokens, concepts)
        
#         # Xử lý các concept: sắp xếp theo vị trí và ánh xạ id concept sang chỉ số trong danh sách
#         sorted_concepts = sorted(concepts.items(), key=lambda x: x[1]["start"])
#         concept_list = []
#         concept_id_to_index = {}
#         for idx, (cid, cinfo) in enumerate(sorted_concepts):
#             concept_obj = {
#                 "id": cid,
#                 "text": cinfo["text"],
#                 "start": cinfo["start"],
#                 "end": cinfo["end"]
#             }
#             concept_list.append(concept_obj)
#             concept_id_to_index[cid] = idx
        
#         # Xử lý quan hệ: chuyển từ id concept sang chỉ số trong danh sách concept
#         relation_list = []
#         for rel in relations:
#             from_id = rel["from_id"]
#             to_id = rel["to_id"]
#             if from_id in concept_id_to_index and to_id in concept_id_to_index:
#                 relation_list.append({
#                     "source": concept_id_to_index[from_id],
#                     "target": concept_id_to_index[to_id],
#                     "label": rel["label"]
#                 })
        
#         output_sample = {
#             "text": text,
#             "tokens": tokens_with_labels,
#             "concepts": concept_list,
#             "relations": relation_list
#         }
#         output_data.append(output_sample)

#     with open(output_file, 'w', encoding='utf-8') as f:
#         json.dump(output_data, f, ensure_ascii=False, indent=2)

# if __name__ == "__main__":
#     input_file = "VNCoreNLP/project-1-at-2025-03-02-21-03-d26b9afe.json"  # File annotation đầu vào
#     output_file = "VNCoreNLP/output.json"  # File đầu ra với cấu trúc mới
#     process_file(input_file, output_file)
  
    
# ###################################################

# Chuyển file thành cấu trúc CoNLL để phục vụ cho việc huấn luyện 

import json

def convert_to_conll(input_json, output_txt):
    """
    Đọc file JSON với cấu trúc gồm:
      - text: văn bản gốc.
      - tokens: danh sách các token (mỗi token có các trường: token, start_char, end_char, label).
      - concepts: danh sách các concept (mỗi concept có: id, text, start, end).
      - relations: danh sách các quan hệ giữa concept (mỗi quan hệ có: source, target, label),
        trong đó source và target là chỉ số (0-index) của concept trong danh sách concepts.
    
    Xuất ra file định dạng CoNLL mở rộng với định dạng:
      (1) Các dòng token: token_index <tab> token <tab> label.
      (2) Dòng trống.
      (3) Dòng "# Concepts:" và các dòng liệt kê concept: concept_index <tab> concept_text <tab> start <tab> end.
      (4) Dòng trống.
      (5) Dòng "# Relations:" và các dòng liệt kê quan hệ: source_index <tab> target_index <tab> relation_label.
      (6) Dòng trống phân cách các mẫu.
    """
    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with open(output_txt, 'w', encoding='utf-8') as f_out:
        for sample in data:
            # Ghi token của câu
            tokens = sample.get("tokens", [])
            for idx, token in enumerate(tokens, start=1):
                token_text = token.get("token", "")
                label = token.get("label", "O")
                f_out.write(f"{idx}\t{token_text}\t{label}\n")
            f_out.write("\n")
            
            # Ghi thông tin các concept
            f_out.write("# Concepts:\n")
            concepts = sample.get("concepts", [])
            for idx, concept in enumerate(concepts):
                concept_text = concept.get("text", "")
                start = concept.get("start", "")
                end = concept.get("end", "")
                f_out.write(f"{idx}\t{concept_text}\t{start}\t{end}\n")
            f_out.write("\n")
            
            # Ghi thông tin các quan hệ
            f_out.write("# Relations:\n")
            relations = sample.get("relations", [])
            for rel in relations:
                source = rel.get("source", "")
                target = rel.get("target", "")
                rel_label = rel.get("label", "")
                f_out.write(f"{source}\t{target}\t{rel_label}\n")
            f_out.write("\n\n")  # Dòng trống phân cách các mẫu

if __name__ == "__main__":
    input_json = "VNCoreNLP/output.json"         # File JSON đầu vào (theo cấu trúc đã có)
    output_txt = "training_data.conll"   # File đầu ra theo định dạng CoNLL mở rộng
    convert_to_conll(input_json, output_txt)

