# import re
# import json

# def split_sentences(text):
#     """
#     Tách câu dựa trên dấu chấm, dấu hỏi, dấu chấm than theo sau bởi khoảng trắng.
#     """
#     sentences = re.split(r'(?<=[.!?])\s+', text)
#     return [s.strip() for s in sentences if s.strip()]

# def clean_sentence(sentence):
#     """
#     Loại bỏ các đánh số đề mục ở đầu câu:
#     - "Chương <số>" (số La Mã)
#     - "Điều <số>"
#     - "Mục <số>"
#     và các đánh số danh sách như "1.", "2)" ở đầu câu.
#     Nếu sau đó câu chỉ chứa số hoặc không có ký tự chữ, trả về chuỗi rỗng.
#     """
#     # Loại bỏ các đánh số đề mục cố định: Chương, Điều, Mục
#     cleaned = re.sub(r'^(?:Chương\s+[IVXLCDM]+|Điều\s+\d+|Mục\s+\d+)[.:]?\s*', '', sentence, flags=re.IGNORECASE)
#     # Loại bỏ các đánh số danh sách ở đầu câu, ví dụ: "1. ", "2) ", v.v.
#     cleaned = re.sub(r'^[0-9]+[\.\)]\s*', '', cleaned)
#     cleaned = cleaned.strip()
#     # Nếu câu không có chữ cái (chỉ có số, dấu câu, khoảng trắng) thì bỏ qua.
#     if not re.search(r'[^\d\W]', cleaned, flags=re.UNICODE):
#         return ""
#     return cleaned

# # Đọc dữ liệu từ file JSON có cấu trúc dạng cây
# with open("law_structure.json", "r", encoding="utf-8") as f:
#     law_data = json.load(f)

# law = law_data.get("law", {})

# # Xử lý nội dung của Law: tách câu, làm sạch và đánh dấu parent, part.
# law_sentences = []
# for s in split_sentences(law.get("content", "")):
#     cleaned = clean_sentence(s)
#     if cleaned:
#         law_sentences.append({
#             "sentence": cleaned,
#             "part": "law",
#             "parent": law.get("title", "Law")
#         })
# law["sentences"] = law_sentences

# # Xử lý nội dung cho mỗi Chapter và Article
# for chapter in law.get("chapters", []):
#     # Đối với nội dung của chương
#     chapter_sentences = []
#     for s in split_sentences(chapter.get("content", "")):
#         cleaned = clean_sentence(s)
#         if cleaned:
#             chapter_sentences.append({
#                 "sentence": cleaned,
#                 "part": "chapter",
#                 "parent": chapter.get("name", "Chapter")
#             })
#     chapter["sentences"] = chapter_sentences

#     # Xử lý từng Điều trong chương
#     for article in chapter.get("articles", []):
#         article_sentences = []
#         for s in split_sentences(article.get("content", "")):
#             cleaned = clean_sentence(s)
#             if cleaned:
#                 article_sentences.append({
#                     "sentence": cleaned,
#                     "part": "article",
#                     "parent": article.get("name", "Article")
#                 })
#         article["sentences"] = article_sentences

# # Lưu kết quả ra file mới
# with open("law_sentences_clean.json", "w", encoding="utf-8") as f:
#     json.dump(law_data, f, ensure_ascii=False, indent=4)

# print("Đã tách câu, loại bỏ các đánh dấu chỉ mục và đánh dấu parent cho từng phần thành công.")














import json

# Đọc tệp JSON
filename = 'law_sentences_clean.json'
with open(filename, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Nếu dữ liệu trong JSON là một mảng (danh sách) hoặc bạn cần trích xuất một phần của nó, bạn có thể làm:
print("Nội dung tệp JSON:")
print(data)

