# import re
# import json
# import pdfplumber

# text = ""
# with pdfplumber.open("31-2024-qh15_1.pdf") as pdf:
#     for page in pdf.pages:
#         text += page.extract_text() + "\n"

# # Khởi tạo cấu trúc cơ bản của văn bản luật
# law = {
#     "id": "law_001",
#     "title": "LUẬT ĐẤT ĐAI",
#     "content": text,   # Nội dung đầy đủ (bạn có thể bỏ nếu không cần lưu)
#     "date": "01-03-2024",
#     "source": "Quốc hội",
#     "category": "Đất đai",
#     "chapters": []
# }

# # Định nghĩa biểu thức chính quy để nhận diện Chương, Mục, Điều và Điều khoản
# chapter_pattern = re.compile(r"^Chương\s+([IVXLCDM]+)(.*)", re.IGNORECASE)
# section_pattern = re.compile(r"^Mục\s+(\d+)\s*(.*)", re.IGNORECASE)
# article_pattern = re.compile(r"^Điều\s+(\d+)[\.\:]\s*(.*)", re.IGNORECASE)
# # Pattern cho điều khoản, giả sử bắt đầu bằng số và dấu chấm (ví dụ: "1. Nội dung điều khoản")
# clause_pattern = re.compile(r"^(\d+)\.\s*(.*)")

# lines = text.splitlines()
# i = 0
# current_chapter = None
# current_section = None
# current_article = None
# current_clause = None

# while i < len(lines):
#     line = lines[i].strip()
#     if not line:
#         i += 1
#         continue

#     # Kiểm tra tiêu đề Chương
#     chapter_match = chapter_pattern.match(line)
#     if chapter_match:
#         roman_num = chapter_match.group(1)
#         chapter_title = chapter_match.group(2).strip()
#         current_chapter = {
#             "id": f"chapter_{roman_num}",
#             "name": f"Chương {roman_num} {chapter_title}",
#             "number": roman_num,
#             "content": "",
#             "articles": []
#         }
#         law["chapters"].append(current_chapter)
#         current_section = None
#         current_article = None
#         current_clause = None
#         i += 1
#         continue

#     # Kiểm tra tiêu đề Mục
#     section_match = section_pattern.match(line)
#     if section_match and current_chapter:
#         section_number = section_match.group(1)
#         section_title = section_match.group(2).strip()
#         full_section_header = f"Mục {section_number} {section_title}".strip()
#         j = i + 1
#         while j < len(lines):
#             next_line = lines[j].strip()
#             if not next_line:
#                 j += 1
#                 continue
#             if chapter_pattern.match(next_line) or article_pattern.match(next_line) or section_pattern.match(next_line):
#                 break
#             full_section_header += " " + next_line
#             j += 1
#         current_section = full_section_header
#         i = j
#         continue

#     # Kiểm tra tiêu đề Điều
#     article_match = article_pattern.match(line)
#     if article_match and current_chapter:
#         article_number = article_match.group(1)
#         article_rest = article_match.group(2).strip()
#         current_article = {
#             "id": f"article_{article_number}",
#             "parent": current_section if current_section is not None else None,
#             "name": article_rest,  # Ở đây có thể tách riêng nếu cần
#             "number": int(article_number),
#             "content": article_rest,
#             "clauses": []  # Danh sách chứa các điều khoản của điều này
#         }
#         current_chapter["articles"].append(current_article)
#         current_clause = None  # Reset điều khoản cho điều mới
#         i += 1
#         continue

#     # Kiểm tra nếu dòng là tiêu đề của điều khoản (clause)
#     clause_match = clause_pattern.match(line)
#     if clause_match and current_article:
#         clause_number = clause_match.group(1)
#         clause_text = clause_match.group(2).strip()
#         current_clause = {
#             "id": f"clause_{current_article['number']}_{clause_number}",
#             "number": int(clause_number),
#             "content": clause_text
#         }
#         current_article["clauses"].append(current_clause)
#         i += 1
#         continue

#     # Nếu dòng không khớp với tiêu đề nào, gán vào nội dung của điều khoản nếu đang có, nếu không thì gán vào nội dung của điều
#     if current_clause:
#         current_clause["content"] += " " + line
#     elif current_article:
#         current_article["content"] += " " + line
#     elif current_chapter:
#         current_chapter["content"] += " " + line

#     i += 1

# # Lưu kết quả ra file JSON
# with open("law_structure.json", "w", encoding="utf-8") as f:
#     json.dump({"law": law}, f, ensure_ascii=False, indent=4)
















# ###################################################################
import re
import json
from docx import Document

# Đọc dữ liệu từ file DOCX vừa chuyển đổi
doc = Document("31-2024-qh15_1.docx")
text = "\n".join([para.text for para in doc.paragraphs])

# Khởi tạo cấu trúc cơ bản của văn bản luật
law = {
    "id": "law_001",
    "title": "LUẬT ĐẤT ĐAI",
    "content": text,   # Nội dung đầy đủ
    "date": "01-03-2024",
    "source": "Quốc hội",
    "category": "Đất đai",
    "chapters": []
}

# Định nghĩa biểu thức chính quy để nhận diện Chương, Mục, Điều và Điều khoản
chapter_pattern = re.compile(r"^Chương\s+([IVXLCDM]+)(.*)", re.IGNORECASE)
section_pattern = re.compile(r"^Mục\s+(\d+)\s*(.*)", re.IGNORECASE)
article_pattern = re.compile(r"^Điều\s+(\d+)[\.\:]\s*(.*)", re.IGNORECASE)
clause_pattern = re.compile(r"^(\d+)\.\s*(.*)")

lines = text.splitlines()
i = 0
current_chapter = None
current_section = None
current_article = None
current_clause = None

while i < len(lines):
    line = lines[i].strip()
    if not line:
        i += 1
        continue

    # Kiểm tra tiêu đề Chương
    chapter_match = chapter_pattern.match(line)
    if chapter_match:
        roman_num = chapter_match.group(1)
        chapter_title = chapter_match.group(2).strip()
        current_chapter = {
            "id": f"chapter_{roman_num}",
            "name": f"Chương {roman_num} {chapter_title}",
            "number": roman_num,
            "content": "",
            "articles": []
        }
        law["chapters"].append(current_chapter)
        current_section = None
        current_article = None
        current_clause = None
        i += 1
        continue

    # Kiểm tra tiêu đề Mục
    section_match = section_pattern.match(line)
    if section_match and current_chapter:
        section_number = section_match.group(1)
        section_title = section_match.group(2).strip()
        full_section_header = f"Mục {section_number} {section_title}".strip()
        j = i + 1
        while j < len(lines):
            next_line = lines[j].strip()
            if not next_line:
                j += 1
                continue
            if chapter_pattern.match(next_line) or article_pattern.match(next_line) or section_pattern.match(next_line):
                break
            full_section_header += " " + next_line
            j += 1
        current_section = full_section_header
        i = j
        continue

    # Kiểm tra tiêu đề Điều
    article_match = article_pattern.match(line)
    if article_match and current_chapter:
        article_number = article_match.group(1)
        article_rest = article_match.group(2).strip()
        current_article = {
            "id": f"article_{article_number}",
            "parent": current_section if current_section is not None else None,
            "name": article_rest,
            "number": int(article_number),
            "content": article_rest,
            "clauses": []
        }
        current_chapter["articles"].append(current_article)
        current_clause = None  # Reset cho điều mới
        i += 1
        continue

    # Kiểm tra nếu dòng là tiêu đề của điều khoản (clause)
    clause_match = clause_pattern.match(line)
    if clause_match and current_article:
        clause_number = clause_match.group(1)
        clause_text = clause_match.group(2).strip()
        current_clause = {
            "id": f"clause_{current_article['number']}_{clause_number}",
            "number": int(clause_number),
            "content": clause_text
        }
        current_article["clauses"].append(current_clause)
        i += 1
        continue

    # Nếu dòng không khớp với tiêu đề nào, gán vào nội dung của điều khoản nếu đang có,
    # nếu không thì gán vào nội dung của điều
    if current_clause:
        current_clause["content"] += " " + line
    elif current_article:
        current_article["content"] += " " + line
    elif current_chapter:
        current_chapter["content"] += " " + line

    i += 1

# Lưu kết quả ra file JSON
with open("law_structure.json", "w", encoding="utf-8") as f:
    json.dump({"law": law}, f, ensure_ascii=False, indent=4)

print("Đã chuyển file DOC sang DOCX, đọc file DOCX và cập nhật cấu trúc văn bản luật thành công.")
