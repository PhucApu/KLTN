from neo4j import GraphDatabase
import json

# Thông tin kết nối Neo4j
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "0823072871phuc"  # Thay bằng mật khẩu Neo4j của bạn
driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

# Hàm tìm node trong đồ thị dựa trên reference
def find_node_by_reference(tx, reference):
    type = reference['type']
    id = reference['id']
    
    if type == "Article":
        query = f"MATCH (a:Article {{id: '{id}'}}) RETURN a"
    elif type == "Clause":
        query = f"MATCH (c:Clause {{id: '{id}'}}) RETURN c"
    elif type == "Point":
        query = f"MATCH (p:Point {{id: '{id}'}}) RETURN p"
    else:
        raise ValueError(f"Loại không được hỗ trợ: {type}")
    
    result = tx.run(query)
    record = result.single()
    if record:
        return record[0]  # Trả về node đầu tiên trong record
    else:
        raise ValueError(f"Không tìm thấy node cho {type} với id {id}")

# Hàm tạo node Concept và kết nối với node trong cấu trúc pháp luật
def create_concept_nodes(tx, concepts, reference_node, reference_type):
    for concept in concepts:
        concept_id = concept['id']
        concept_name = concept['khái niệm']
        
        # Tạo node Concept nếu chưa tồn tại
        tx.run(
            "MERGE (c:Concept {id: $id}) "
            "SET c.name = $name",
            id=concept_id, name=concept_name
        )
        
        # Kết nối Concept với node trong cấu trúc pháp luật bằng mối quan hệ MENTIONS
        if reference_type == "Article":
            tx.run(
                "MATCH (a:Article {id: $node_id}), (c:Concept {id: $concept_id}) "
                "MERGE (a)-[:MENTIONS]->(c)",
                node_id=reference_node['id'], concept_id=concept_id
            )
        elif reference_type == "Clause":
            tx.run(
                "MATCH (cl:Clause {id: $node_id}), (c:Concept {id: $concept_id}) "
                "MERGE (cl)-[:MENTIONS]->(c)",
                node_id=reference_node['id'], concept_id=concept_id
            )
        elif reference_type == "Point":
            tx.run(
                "MATCH (p:Point {id: $node_id}), (c:Concept {id: $concept_id}) "
                "MERGE (p)-[:MENTIONS]->(c)",
                node_id=reference_node['id'], concept_id=concept_id
            )

# Hàm tạo mối quan hệ giữa các node Concept dựa trên relation_pairs
def create_concept_relations(tx, relation_pairs, relations):
    for pair in relation_pairs:
        concept1_id = pair['concept1']
        relation_id = pair['relation']
        concept2_id = pair['concept2']
        
        # Lấy giá trị "khái niệm" từ relations (từ thực sự trong câu)
        relation_text = next(r['khái niệm'] for r in relations if r['id'] == relation_id)
        
        # Tạo mối quan hệ RELATED_TO với thuộc tính relation_text
        tx.run(
            "MATCH (c1:Concept {id: $c1_id}), (c2:Concept {id: $c2_id}) "
            "MERGE (c1)-[r:RELATED_TO]->(c2) "
            "SET r.relation_text = $relation_text",
            c1_id=concept1_id, c2_id=concept2_id, relation_text=relation_text
        )

# Hàm chính để xử lý mảng JSON
def process_sentences(sentences):
    with driver.session() as session:
        for sentence_data in sentences:
            reference = sentence_data['reference']
            concepts = sentence_data['concepts']
            relations = sentence_data['relations']
            relation_pairs = sentence_data['relation_pairs']
            
            # Tìm node trong đồ thị dựa trên reference
            reference_node = session.read_transaction(find_node_by_reference, reference)
            
            # Lấy loại của reference_node từ reference
            reference_type = reference['type']
            
            # Tạo các node Concept và kết nối với reference_node
            session.write_transaction(create_concept_nodes, concepts, reference_node, reference_type)
            
            # Tạo các mối quan hệ giữa các Concept
            session.write_transaction(create_concept_relations, relation_pairs, relations)

# Đọc dữ liệu đầu vào và thực thi
with open('sentences_with_concepts.json', 'r', encoding='utf-8') as f:
    sentences = json.load(f)

process_sentences(sentences)

# Đóng kết nối
driver.close()