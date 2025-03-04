from google import genai
import json

client = genai.Client(api_key="AIzaSyDmFH8wHZsG-TK2hzd14jRkyCsTeMl8qbE")

contents = "Construct a knowledge graph from the data '<Hành vi bị nghiêm cấm trong lĩnh vực đất đai.>' and return the result in JSON format with the structure {c1, r, c2}. I only want the response to contain the JSON structure, nothing else, as I am making an API call."

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=contents,
)

print(response.text)

responseVal = response.text

# Loại bỏ các dấu ```json và ```
clean_json = responseVal.strip('`json\n')

# Chuyển đổi JSON thành danh sách dictionary
data = json.loads(clean_json)

# Hiển thị kết quả
print(data)

# Hàm kiểm tra kết quả trả về 
def validate_result(data, original_content):
    """
    Kiểm tra xem các giá trị của c1, r, c2 trong data có xuất hiện trong phần dữ liệu gốc
    (nằm giữa dấu '<' và '>') hay không.
    Nếu có tất cả trả về True, ngược lại trả về False.
    """
    # Trích xuất nội dung giữa dấu < và >
    start = original_content.find('<')
    end = original_content.find('>')
    if start == -1 or end == -1 or end <= start:
        return False  # Không tìm thấy nội dung hợp lệ

    inner_text = original_content[start + 1:end]
    
    # Kiểm tra từng phần tử
    for item in data:
        # Nếu một trong các giá trị không có trong inner_text thì dữ liệu không hợp lệ
        if item.get('c1') not in inner_text:
            return False
        if item.get('r') not in inner_text:
            return False
        if item.get('c2') not in inner_text:
            return False
    return True


print(validate_result(data,contents))

def transform_data_to_lower(data):
    """
    Nhận vào một danh sách các dictionary có khóa c1, r, c2 và trả về danh sách mới
    với giá trị của các khóa đó được chuyển thành chữ in thường.
    """
    new_data = []
    for item in data:
        new_item = {
            'c1': item.get('c1', '').lower(),
            'r': item.get('r', '').lower(),
            'c2': item.get('c2', '').lower()
        }
        new_data.append(new_item)
    return new_data


data_lower = transform_data_to_lower(data)

# ###############################


# from neo4j import GraphDatabase
# import json

# # Thông tin kết nối đến Neo4j
# URI = "bolt://localhost:7687"
# USERNAME = "neo4j"
# PASSWORD = "0823072871phuc"

# # Class kết nối đến Neo4j
# class Neo4jConnection:
#     def __init__(self, uri, user, password):
#         self._driver = GraphDatabase.driver(uri, auth=(user, password))
#     def close(self):
#         self._driver.close()
#     def run_query(self, query, parameters={}):
#         with self._driver.session() as session:
#             result = session.run(query, parameters)
#             return list(result)

# # Khởi tạo kết nối
# conn = Neo4jConnection(URI, USERNAME, PASSWORD)

# # Kiểm tra kết nối
# test_query = "RETURN 'Kết nối Neo4j thành công!' AS message"
# for record in conn.run_query(test_query):
#     print(record["message"])

# # Đọc dữ liệu từ file JSON (cấu trúc dạng cây của văn bản pháp luật)
# with open("law_structure.json", "r", encoding="utf-8") as f:
#     law_data = json.load(f)
# law = law_data["law"]

# # Tạo node Law
# law_query = """
# MERGE (l:Law {id: $id})
# SET l.title = $title, l.content = $content, l.date = $date, l.source = $source, l.category = $category
# RETURN l
# """
# conn.run_query(law_query, {
#     "id": law["id"],
#     "title": law["title"],
#     "content": law["content"],
#     "date": law["date"],
#     "source": law["source"],
#     "category": law["category"]
# })

# Lặp qua các chương để tạo node Chapter và quan hệ HAS_CHAPTER (Law -> Chapter)
# for chapter in law.get("chapters", []):
#     chapter_query = """
#     MERGE (c:Chapter {id: $id})
#     SET c.name = $name, c.number = $number, c.content = $content
#     RETURN c
#     """
#     conn.run_query(chapter_query, {
#         "id": chapter["id"],
#         "name": chapter["name"],
#         "number": chapter["number"],
#         "content": chapter["content"]
#     })
#     # Tạo quan hệ HAS_CHAPTER từ Law đến Chapter
#     rel_query = """
#     MATCH (l:Law {id: $law_id}), (c:Chapter {id: $chapter_id})
#     MERGE (l)-[:HAS_CHAPTER]->(c)
#     """
#     conn.run_query(rel_query, {
#         "law_id": law["id"],
#         "chapter_id": chapter["id"]
#     })
    
#     # Lặp qua các Điều trong chương để tạo node Article và quan hệ HAS_ARTICLE (Chapter -> Article)
#     for article in chapter.get("articles", []):
#         article_query = """
#         MERGE (a:Article {id: $id})
#         SET a.parent = $parent, a.name = $name, a.number = $number, a.content = $content
#         RETURN a
#         """
#         conn.run_query(article_query, {
#             "id": article["id"],
#             "parent": article["parent"],  # Nếu không có Mục thì giá trị này sẽ là null
#             "name": article["name"],
#             "number": article["number"],
#             "content": article["content"]
#         })
#         # Tạo quan hệ HAS_ARTICLE từ Chapter đến Article
#         rel_article_query = """
#         MATCH (c:Chapter {id: $chapter_id}), (a:Article {id: $article_id})
#         MERGE (c)-[:HAS_ARTICLE]->(a)
#         """
#         conn.run_query(rel_article_query, {
#             "chapter_id": chapter["id"],
#             "article_id": article["id"]
#         })

# (Tùy chọn) Tạo thêm các node Concept và quan hệ giữa chúng từ dữ liệu mẫu
# data_lower = [
#     {'c1': 'Chỉ tiêu sử dụng đất', 'r': 'là', 'c2': 'diện tích đất của từng loại đất'},
#     {'c1': 'Chỉ tiêu sử dụng đất', 'r': 'được xác định trong', 'c2': 'quy hoạch, kế hoạch sử dụng đất các cấp'},
#     {'c1': 'quy hoạch, kế hoạch sử dụng đất các cấp', 'r': 'do', 'c2': 'cơ quan nhà nước có thẩm quyền xác định'},
#     {'c1': 'Chỉ tiêu sử dụng đất', 'r': 'được phân bổ trong quá trình', 'c2': 'lập quy hoạch, kế hoạch sử dụng đất'}
# ]

# for entry in data_lower:
#     c1 = entry['c1']
#     rel_type = entry['r']
#     c2 = entry['c2']
#     concept_query = f"""
#     MERGE (a:Concept {{name: $c1}})
#     MERGE (b:Concept {{name: $c2}})
#     MERGE (a)-[r:`{rel_type}`]->(b)
#     """
#     conn.run_query(concept_query, {"c1": c1, "c2": c2})

# print("Đã tạo các node và quan hệ thành công.")

# conn.close()

