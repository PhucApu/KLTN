import json
from neo4j import GraphDatabase

# Thông tin kết nối Neo4j
URI = "bolt://localhost:7687"  # Thay đổi nếu cần
USERNAME = "neo4j"
PASSWORD = "0823072871phuc"  # Thay bằng mật khẩu thực tế của bạn

# Kết nối đến Neo4j
driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

# Hàm tạo node Law
def create_law(tx, law_data):
    tx.run("""
        CREATE (l:Law {id: $id, title: $title, date: $date, source: $source, category: $category})
    """, id=law_data['id'], title=law_data['title'], date=law_data['date'],
         source=law_data['source'], category=law_data['category'])

# Hàm tạo node Chapter và relationship HAS_CHAPTER
def create_chapter(tx, chapter_data, law_id):
    tx.run("""
        CREATE (c:Chapter {id: $id, name: $name, number: $number})
    """, id=chapter_data['id'], name=chapter_data['name'], number=chapter_data['number'])
    tx.run("""
        MATCH (l:Law {id: $law_id}), (c:Chapter {id: $chapter_id})
        CREATE (l)-[:HAS_CHAPTER]->(c)
    """, law_id=law_id, chapter_id=chapter_data['id'])

# Hàm tạo node Section (nếu chưa tồn tại) và trả về id của Section
def create_section(tx, section_name, chapter_id):
    # Tạo id duy nhất cho Section bằng cách kết hợp chapter_id và section_name
    section_id = f"{chapter_id}_section_{section_name.replace(' ', '_').lower()}"
    tx.run("""
        MERGE (s:Section {id: $id})
        ON CREATE SET s.name = $name
    """, id=section_id, name=section_name)
    # Kết nối Section với Chapter qua relationship HAS_SECTION
    tx.run("""
        MATCH (c:Chapter {id: $chapter_id}), (s:Section {id: $section_id})
        MERGE (c)-[:HAS_SECTION]->(s)
    """, chapter_id=chapter_id, section_id=section_id)
    return section_id

# Hàm tạo node Article và relationship HAS_ARTICLE
def create_article(tx, article_data, chapter_id):
    tx.run("""
        CREATE (a:Article {id: $id, parent: $parent, name: $name, number: $number, content: $content})
    """, id=article_data['id'], parent=article_data['parent'], name=article_data['name'],
         number=article_data['number'], content=article_data['content'])
    
    if article_data['parent'] is not None:
        # Nếu có parent, tạo hoặc lấy Section và kết nối Article với Section
        section_id = create_section(tx, article_data['parent'], chapter_id)
        tx.run("""
            MATCH (s:Section {id: $section_id}), (a:Article {id: $article_id})
            CREATE (s)-[:HAS_ARTICLE]->(a)
        """, section_id=section_id, article_id=article_data['id'])
    else:
        # Nếu không có parent, kết nối Article trực tiếp với Chapter
        tx.run("""
            MATCH (c:Chapter {id: $chapter_id}), (a:Article {id: $article_id})
            CREATE (c)-[:HAS_ARTICLE]->(a)
        """, chapter_id=chapter_id, article_id=article_data['id'])

# Hàm tạo node Clause và relationship HAS_CLAUSE
def create_clause(tx, clause_data, article_id):
    tx.run("""
        CREATE (cl:Clause {id: $id, number: $number, content: $content})
    """, id=clause_data['id'], number=clause_data['number'], content=clause_data['content'])
    tx.run("""
        MATCH (a:Article {id: $article_id}), (cl:Clause {id: $clause_id})
        CREATE (a)-[:HAS_CLAUSE]->(cl)
    """, article_id=article_id, clause_id=clause_data['id'])

# Hàm tạo node Point và relationship HAS_POINT
def create_point(tx, point_data, clause_id):
    tx.run("""
        CREATE (p:Point {id: $id, number: $number, content: $content})
    """, id=point_data['id'], number=point_data['number'], content=point_data['content'])
    tx.run("""
        MATCH (cl:Clause {id: $clause_id}), (p:Point {id: $point_id})
        CREATE (cl)-[:HAS_POINT]->(p)
    """, clause_id=clause_id, point_id=point_data['id'])

# Hàm tạo relationship REFERENCES giữa các Article
def create_reference(tx, article_id, reference_id):
    tx.run("""
        MATCH (a:Article {id: $article_id}), (ref:Article {id: $reference_id})
        CREATE (a)-[:REFERENCES]->(ref)
    """, article_id=article_id, reference_id=reference_id)

# Hàm chính để import dữ liệu từ file JSON vào Neo4j
def import_law_data(file_path):
    # Đọc file JSON
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Lấy dữ liệu law
    law_data = data['law']
    
    # Sử dụng session để thực hiện các transaction
    with driver.session() as session:
        # Tạo node Law
        session.write_transaction(create_law, law_data)
        
        # Duyệt qua các chapter
        for chapter in law_data['chapters']:
            session.write_transaction(create_chapter, chapter, law_data['id'])
            
            # Duyệt qua các article trong chapter
            for article in chapter['articles']:
                session.write_transaction(create_article, article, chapter['id'])
                
                # Duyệt qua các clause trong article
                for clause in article['clauses']:
                    session.write_transaction(create_clause, clause, article['id'])
                    
                    # Duyệt qua các point trong clause (nếu có)
                    for point in clause.get('points', []):
                        session.write_transaction(create_point, point, clause['id'])
                
                # Tạo relationship REFERENCES nếu có
                for reference in article.get('references', []):
                    session.write_transaction(create_reference, article['id'], reference)

# Thực thi hàm import với đường dẫn file JSON
file_path = 'law_structure.json'  # Thay bằng đường dẫn thực tế đến file JSON
import_law_data(file_path)

# Đóng kết nối Neo4j
driver.close()