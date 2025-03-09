# import json
# import re

# def simple_tokenize_with_spans(text):
#     """
#     Tokenize văn bản sử dụng biểu thức chính quy, tính toán chỉ số bắt đầu và kết thúc cho mỗi token.
#     Tách riêng các dấu ngắt câu khỏi từ.
#     """
#     tokens_with_info = []
#     # Biểu thức: \w+ tìm các từ; [^\w\s] tìm các ký tự không phải chữ, không phải khoảng trắng (dấu câu)
#     pattern = r'\w+|[^\w\s]'
#     for match in re.finditer(pattern, text):
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
#     Trích xuất các annotation của concept (nhãn "Concept").
#     Trả về dictionary mapping: id -> {text, start, end}
#     """
#     concepts = {}
#     for ann in annotations:
#         for res in ann.get("result", []):
#             if res.get("type") == "labels":
#                 value = res.get("value", {})
#                 if "Concept" in value.get("labels", []):
#                     cid = res.get("id")
#                     concepts[cid] = {
#                         "text": value.get("text"),
#                         "start": value.get("start"),
#                         "end": value.get("end")
#                     }
#     return concepts

# def get_relation_annotations(annotations):
#     """
#     Trích xuất các annotation của relation (nhãn "Relation").
#     Trả về dictionary mapping: relation_id -> {text, start, end}
#     """
#     relations = {}
#     for ann in annotations:
#         for res in ann.get("result", []):
#             if res.get("type") == "labels":
#                 value = res.get("value", {})
#                 if "Relation" in value.get("labels", []):
#                     rid = res.get("id")
#                     relations[rid] = {
#                         "text": value.get("text"),
#                         "start": value.get("start"),
#                         "end": value.get("end")
#                     }
#     return relations

# def get_relations(annotations):
#     """
#     Trích xuất các triple quan hệ từ annotations dựa trên thông tin liên kết.
#     Tạo triple từ source → relation → target dựa trên from_id và to_id.
#     """
#     concept_dict = get_concepts(annotations)
#     relation_dict = get_relation_annotations(annotations)
    
#     # Dictionary lưu các liên kết cho mỗi relation annotation
#     relation_connections = {}
    
#     for ann in annotations:
#         for res in ann.get("result", []):
#             if res.get("type") == "relation":
#                 from_id = res.get("from_id")
#                 to_id = res.get("to_id")
#                 # Nếu from_id là khái niệm và to_id là relation → khái niệm là source
#                 if from_id in concept_dict and to_id in relation_dict:
#                     relation_connections.setdefault(to_id, {"sources": [], "targets": []})
#                     relation_connections[to_id]["sources"].append(from_id)
#                 # Nếu from_id là relation và to_id là khái niệm → khái niệm là target
#                 elif from_id in relation_dict and to_id in concept_dict:
#                     relation_connections.setdefault(from_id, {"sources": [], "targets": []})
#                     relation_connections[from_id]["targets"].append(to_id)
    
#     # Tạo danh sách triple
#     triples = []
#     for rel_id, conn in relation_connections.items():
#         sources = conn.get("sources", [])
#         targets = conn.get("targets", [])
#         for source in sources:
#             for target in targets:
#                 triples.append({
#                     "source_id": source,
#                     "relation_id": rel_id,
#                     "target_id": target
#                 })
#     return triples

# def assign_bio_labels(tokens_with_info, spans, prefix):
#     """
#     Gán nhãn BIO cho các token dựa trên khoảng span của các annotation (concept hoặc relation).
#     Trường nhãn được lưu với key: prefix.lower() + "_label" (ví dụ: "concept_label").
#     """
#     for token in tokens_with_info:
#         start = token["start_char"]
#         end = token["end_char"]
#         token[prefix.lower() + "_label"] = "O"
#         for span in spans:
#             if start >= span["start"] and end <= span["end"]:
#                 token[prefix.lower() + "_label"] = "B-" + prefix if start == span["start"] else "I-" + prefix
#                 break
#     return tokens_with_info

# def process_file(input_file, output_file):
#     with open(input_file, 'r', encoding='utf-8') as f:
#         data = json.load(f)

#     output_data = []

#     for sample in data:
#         text = sample["data"]["text"]
#         tokens = simple_tokenize_with_spans(text)
#         annotations = sample.get("annotations", [])

#         # Lấy thông tin annotation của concept và relation
#         concept_dict = get_concepts(annotations)
#         relation_dict = get_relation_annotations(annotations)

#         # Gán nhãn BIO cho các token theo concept và relation
#         tokens = assign_bio_labels(tokens, list(concept_dict.values()), "Concept")
#         tokens = assign_bio_labels(tokens, list(relation_dict.values()), "Relation")

#         # Lấy các triple quan hệ
#         relation_triples = get_relations(annotations)
#         relations_output = []
#         for triple in relation_triples:
#             src_id = triple["source_id"]
#             rel_id = triple["relation_id"]
#             tgt_id = triple["target_id"]
#             if src_id in concept_dict and tgt_id in concept_dict and rel_id in relation_dict:
#                 relations_output.append({
#                     "concept1_start": concept_dict[src_id]["start"],
#                     "relation_start": relation_dict[rel_id]["start"],
#                     "concept2_start": concept_dict[tgt_id]["start"]
#                 })

#         # Xây dựng đối tượng đầu ra
#         output_sample = {
#             "text": text,
#             "tokens": tokens,
#             "relations": relations_output
#         }
#         output_data.append(output_sample)

#     with open(output_file, 'w', encoding='utf-8') as f:
#         json.dump(output_data, f, ensure_ascii=False, indent=2)

# if __name__ == "__main__":
#     input_file = "VNCoreNLP/project-3-at-2025-03-04-14-19-54a45aef.json"  # File annotation đầu vào
#     output_file = "VNCoreNLP/output.json"  # File đầu ra với cấu trúc mới
#     process_file(input_file, output_file)

    
    
# ###################################################

# import json

# def convert_to_conll_with_offset(input_json, output_txt):
#     """
#     Đọc file JSON với cấu trúc:
#       - tokens: danh sách các token (mỗi token có các trường: token, start_char, end_char, concept_label, relation_label)
#       - relations: danh sách các quan hệ dạng triple (concept1_start, relation_start, concept2_start)
#     Xuất ra file ConLL mở rộng với 6 cột:
#       token_index, token, concept_label, relation_label, start_char, end_char
#     Và block "# Relations:" theo định dạng:
#       Header nhóm: concept1_start <tab> relation_start
#       Sau đó, mỗi dòng: relation_start <tab> concept2_start (cho tất cả concept2_start của nhóm)
#     """
#     with open(input_json, 'r', encoding='utf-8') as f:
#         data = json.load(f)
        
#     with open(output_txt, 'w', encoding='utf-8') as f_out:
#         for sample in data:
#             tokens = sample.get("tokens", [])
#             for idx, token in enumerate(tokens, start=1):
#                 token_text = token.get("token", "")
#                 concept_label = token.get("concept_label", "O")
#                 relation_label = token.get("relation_label", "O")
#                 start_char = token.get("start_char", -1)
#                 end_char = token.get("end_char", -1)
#                 f_out.write(f"{idx}\t{token_text}\t{concept_label}\t{relation_label}\t{start_char}\t{end_char}\n")
#             f_out.write("\n")
            
#             # Nhóm các quan hệ theo key (concept1_start, relation_start)
#             relation_groups = {}
#             for rel in sample.get("relations", []):
#                 c1 = int(rel.get("concept1_start", 0))
#                 r = int(rel.get("relation_start", 0))
#                 c2 = int(rel.get("concept2_start", 0))
#                 key = (c1, r)
#                 if key not in relation_groups:
#                     relation_groups[key] = []
#                 if c2 not in relation_groups[key]:
#                     relation_groups[key].append(c2)
            
#             f_out.write("# Relations:\n")
#             for (concept1_start, relation_start), concept2_list in relation_groups.items():
#                 # In header nhóm một lần
#                 f_out.write(f"{concept1_start}\t{relation_start}\n")
#                 for concept2 in concept2_list:
#                     f_out.write(f"{relation_start}\t{concept2}\n")
#                 f_out.write("\n")
#             f_out.write("\n")

# if __name__ == "__main__":
#     input_json = "VNCoreNLP/output.json"  # JSON gốc
#     output_txt = "training_data.conll"    # File ConLL đầu ra
#     convert_to_conll_with_offset(input_json, output_txt)


######################################

import json

def convert_to_conll_with_offset(input_json, output_txt):
    """
    Đọc file JSON với cấu trúc:
      - tokens: danh sách các token (mỗi token có các trường: token, start_char, end_char, concept_label, relation_label)
      - relations: danh sách các quan hệ dạng triple (concept1_start, relation_start, concept2_start)
    Xuất ra file ConLL mở rộng với 6 cột:
      token_index, token, concept_label, relation_label, start_char, end_char
    Và block "# Relations:" với mỗi triple trên một dòng:
      concept1_start <tab> relation_start <tab> concept2_start
    """
    with open(input_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    with open(output_txt, 'w', encoding='utf-8') as f_out:
        for sample in data:
            # In phần token
            tokens = sample.get("tokens", [])
            for idx, token in enumerate(tokens, start=1):
                token_text = token.get("token", "")
                concept_label = token.get("concept_label", "O")
                relation_label = token.get("relation_label", "O")
                start_char = token.get("start_char", -1)
                end_char = token.get("end_char", -1)
                f_out.write(f"{idx}\t{token_text}\t{concept_label}\t{relation_label}\t{start_char}\t{end_char}\n")
            f_out.write("\n")
            
            # In phần quan hệ dưới dạng triple
            f_out.write("# Relations:\n")
            for rel in sample.get("relations", []):
                c1 = int(rel.get("concept1_start", 0))
                r = int(rel.get("relation_start", 0))
                c2 = int(rel.get("concept2_start", 0))
                f_out.write(f"{c1}\t{r}\t{c2}\n")
            f_out.write("\n")

if __name__ == "__main__":
    input_json = "VNCoreNLP/output.json"  # JSON gốc
    output_txt = "training_data.conll"    # File ConLL đầu ra
    convert_to_conll_with_offset(input_json, output_txt)
