from neo4j import GraphDatabase
import itertools

# Thông tin kết nối Neo4j
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "0823072871phuc"  # Thay bằng mật khẩu Neo4j của bạn
driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))

# Hàm tìm bộ ba trong đồ thị Neo4j
def find_triples(tx, concept1_name, relation_text, concept2_name):
    query = (
        "MATCH (c1:Concept {name: $c1_name})-[r:RELATED_TO {relation_text: $relation_text}]->(c2:Concept {name: $c2_name}) "
        "RETURN c1, r, c2"
    )
    result = tx.run(query, c1_name=concept1_name, relation_text=relation_text, c2_name=concept2_name)
    triples = [record for record in result]
    print(f"Triples found: {len(triples)}")
    return triples

# Hàm truy ngược để lấy toàn bộ cấu trúc văn bản luật theo nhánh
def get_law_structure_paths(tx, concept1_node, concept2_node, relation_text):
    query = (
        "MATCH (structure)-[:MENTIONS]->(c1:Concept), (structure)-[:MENTIONS]->(c2:Concept) "
        "WHERE elementId(c1) = $concept1_id AND elementId(c2) = $concept2_id "
        "AND EXISTS((c1)-[:RELATED_TO {relation_text: $relation_text}]->(c2)) "
        "OPTIONAL MATCH (article:Article)-[:HAS_CLAUSE]->(structure) "
        "OPTIONAL MATCH (chapter:Chapter)-[:HAS_ARTICLE]->(article) "
        "OPTIONAL MATCH (law:Law)-[:HAS_CHAPTER]->(chapter) "
        "RETURN law, chapter, article, structure"
    )
    result = tx.run(query, 
                    concept1_id=concept1_node.element_id,
                    concept2_id=concept2_node.element_id,
                    relation_text=relation_text)
    paths = []
    for record in result:
        path = []
        if record["law"]:
            path.append(record["law"])
        if record["chapter"]:
            path.append(record["chapter"])
        if record["article"]:
            path.append(record["article"])
        if record["structure"]:
            path.append(record["structure"])
        paths.append(path)
    print(f"Structure paths found: {len(paths)}")
    return paths

# Hàm định dạng nội dung cho một nhánh
def format_path(path):
    contents = []
    for node in path:
        # Lấy nhãn đầu tiên từ frozenset
        type_ = next(iter(node.labels))  # Sử dụng next(iter()) để lấy phần tử đầu tiên từ labels
        id_ = node["id"] or "N/A"
        name = node["name"] or ""
        number = node["number"] or "N/A"
        content = node["content"] or ""
        title = node.get("title", "")  # Lấy title nếu có (cho Law)

        if type_ == "Law":
            line = f"{type_} (ID: {id_})"
            if title:
                line += f" - {title}"
        else:
            line = f"{type_} {number} (ID: {id_})"
            if name:
                line += f" - {name}"
            if content:
                line += f": {content}"
        contents.append(line)
    return contents

# Hàm chính để xử lý đầu vào và trả về nội dung văn bản luật theo từng nhánh
def retrieve_law_content(input_data):
    all_paths = []
    with driver.session() as session:
        for item in input_data:
            concepts = item["concepts"]
            relations = item["relations"]
            
            for relation in relations:
                for c1, c2 in itertools.permutations(concepts, 2):
                    triple = (c1, relation, c2)
                    print(f"Đang tìm kiếm bộ ba: {triple}")
                    
                    triples_found = session.execute_read(find_triples, c1, relation, c2)
                    
                    if triples_found:
                        for record in triples_found:
                            concept1_node = record["c1"]
                            concept2_node = record["c2"]
                            
                            # Lấy các nhánh cấu trúc
                            paths = session.execute_read(get_law_structure_paths, concept1_node, concept2_node, relation)
                            all_paths.extend(paths)
                    else:
                        print(f"Không tìm thấy bộ ba: {triple} trong Neo4j")
    
    if not all_paths:
        print("Không có nội dung văn bản luật nào được tìm thấy")
        return []

    # Định dạng và nhóm theo từng nhánh
    formatted_results = []
    for i, path in enumerate(all_paths, 1):
        formatted_path = format_path(path)
        formatted_results.append((f"Nhánh {i}", formatted_path))

    return formatted_results

# Đầu vào ví dụ
input_data = [
    {
        "concepts": ["Người đại diện theo pháp luật", "Việc sử dụng đất"],
        "relations": ["đối với"]
    }
]

# Thực thi và in kết quả
law_paths = retrieve_law_content(input_data)
print("\nVăn bản luật tổng hợp:")
for group_name, contents in law_paths:
    print(f"{group_name}:")
    for content in contents:
        print(f"  + {content}")

# Đóng kết nối
driver.close()