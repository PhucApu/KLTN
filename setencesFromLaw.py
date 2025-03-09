import json
import re

# Hàm tách câu từ văn bản
def split_sentences(text):
    # Tách câu dựa trên dấu chấm, chấm than, dấu hỏi, và dấu chấm phẩy, nhưng không tách tại dấu chấm trong số thứ tự
    sentences = re.split(r'(?<![0-9])[.!?;]\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    # Gộp các phần mở đầu kết thúc bằng dấu hai chấm với câu tiếp theo
    merged_sentences = []
    i = 0
    while i < len(sentences):
        if sentences[i].endswith(':') and i + 1 < len(sentences):
            merged_sentences.append(sentences[i] + ' ' + sentences[i + 1])
            i += 2  # Bỏ qua câu tiếp theo đã được gộp
        else:
            merged_sentences.append(sentences[i])
            i += 1
    
    return merged_sentences

# Hàm trích xuất câu từ một phần (Article, Clause, Point)
def extract_sentences(data, reference_type, reference_id, parent_ids=None):
    sentences = []
    content = data.get('content', '')
    if content:
        for sentence in split_sentences(content):
            reference = {
                'type': reference_type,
                'id': reference_id
            }
            if parent_ids:
                reference.update(parent_ids)
            sentences.append({
                'sentence': sentence,
                'reference': reference
            })
    return sentences

# Hàm xử lý file JSON và trích xuất tất cả câu
def process_law_structure(input_file, output_file):
    # Đọc file JSON đầu vào
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    law_data = data['law']
    all_sentences = []
    
    # Duyệt qua các chương
    for chapter in law_data['chapters']:
        chapter_id = chapter['id']
        # Kiểm tra xem chapter có sections không
        if 'sections' in chapter:
            for section in chapter['sections']:
                section_id = section['id']
                for article in section['articles']:
                    article_id = article['id']
                    # Trích xuất câu từ Article trong Section
                    all_sentences.extend(extract_sentences(article, 'Article', article_id, {'chapter_id': chapter_id, 'section_id': section_id}))
                    for clause in article['clauses']:
                        clause_id = clause['id']
                        # Trích xuất câu từ Clause trong Article của Section
                        all_sentences.extend(extract_sentences(clause, 'Clause', clause_id, {'chapter_id': chapter_id, 'section_id': section_id, 'article_id': article_id}))
                        for point in clause.get('points', []):
                            point_id = point['id']
                            # Trích xuất câu từ Point trong Clause của Article trong Section
                            all_sentences.extend(extract_sentences(point, 'Point', point_id, {'chapter_id': chapter_id, 'section_id': section_id, 'article_id': article_id, 'clause_id': clause_id}))
        else:
            # Nếu chapter không có sections, duyệt trực tiếp các articles
            for article in chapter['articles']:
                article_id = article['id']
                # Trích xuất câu từ Article trực tiếp trong Chapter
                all_sentences.extend(extract_sentences(article, 'Article', article_id, {'chapter_id': chapter_id}))
                for clause in article['clauses']:
                    clause_id = clause['id']
                    # Trích xuất câu từ Clause trong Article trực tiếp của Chapter
                    all_sentences.extend(extract_sentences(clause, 'Clause', clause_id, {'chapter_id': chapter_id, 'article_id': article_id}))
                    for point in clause.get('points', []):
                        point_id = point['id']
                        # Trích xuất câu từ Point trong Clause của Article trực tiếp trong Chapter
                        all_sentences.extend(extract_sentences(point, 'Point', point_id, {'chapter_id': chapter_id, 'article_id': article_id, 'clause_id': clause_id}))
    
    # Lưu vào file JSON đầu ra
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_sentences, f, ensure_ascii=False, indent=4)
    print(f"Đã lưu {len(all_sentences)} câu vào file {output_file}")

# Thực thi chương trình
input_file = 'law_structure.json'  # Đường dẫn đến file đầu vào
output_file = 'sentences.json'     # Đường dẫn đến file đầu ra
process_law_structure(input_file, output_file)