import os
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from ..models.gConc import GConc
from ..models.gRel import gRel
import pandas as pd
# kiểm tra sự tồn tại của 01 node
def relationship_exists(driver, rel_id):
    query = """
    MATCH ()-[r]->()
    WHERE r.relation_id = $relId
    RETURN COUNT(r) > 0 AS exists
    """
    with driver.session() as session:
        result = session.run(query, relId=rel_id)
        return result.single()["exists"]
    
# cập nhật 1 node thông qua node_id
def update_node_by_id(driver, node_id, updates: dict):
    query = """
    MATCH (n)
    WHERE n.node_id = $node_id
    SET n += $updates
    RETURN n
    """
    with driver.session() as session:
        result = session.run(query, node_id=node_id, updates=updates)
        return result.single()[0] if result.peek() else None
    
# Tạo một node mới
def create_node(driver, properties: dict):
        query = f"""
        CREATE (n:Conc)
        SET n += $props
        RETURN n
        """
        with driver.session() as session:
            result = session.run(query, props=properties)
            return result.single()[0] if result.peek() else None

#Kiểm tra 1 node có tồn tại không thông qua 1 thuộc tính nào đó
def node_exists_by_property(driver, property_key: str, property_value) -> bool:
    query = f"""
    MATCH (n:Conc)
    WHERE n.{property_key} = $property_value
    RETURN COUNT(n) > 0 AS exists
    """
    with driver.session() as session:
        result = session.run(query, property_value=property_value)
        return result.single()["exists"]
    
# Tạo một quan hệ mới
def create_relationship(driver, start_node_id, end_node_id, rel_properties: dict):
    query = f"""
    MATCH (a), (b)
    WHERE a.node_id = $start_node_id AND b.node_id = $end_node_id
    CREATE (a)-[r:Rel]->(b)
    SET r += $rel_properties
    RETURN r
    """
    with driver.session() as session:
        result = session.run(query, start_node_id=start_node_id, end_node_id=end_node_id, rel_properties=rel_properties)
        return result.single()[0] if result.peek() else None
    

# xóa hậu duệ mà xóa file của node
def remove_descendants(driver, descendants_des: list):
    query = """
    WITH $descendants_des AS removeList
    MATCH (n)
    WHERE ANY(item IN removeList WHERE item IN n.descendants)
    SET n.descendants = [x IN n.descendants WHERE NOT x IN removeList]
    RETURN n
    """
    with driver.session() as session:
        result = session.run(query, descendants_des=descendants_des)
        return [record["n"] for record in result]
    
# xóa hậu duệ của relation
def remove_descendants_from_relationships(driver, descendants_des: list):
    query = """
    WITH $descendants_des AS removeList
    MATCH ()-[r]->()
    WHERE ANY(item IN removeList WHERE item IN r.descendants)
    SET r.descendants = [x IN r.descendants WHERE NOT x IN removeList]
    RETURN r
    """
    with driver.session() as session:
        result = session.run(query, descendants_des=descendants_des)
        return [record["r"] for record in result]

# cập nhật rel
def update_relationship(driver, rel_id, updates: dict):
    query = f"""
    MATCH (a)-[r:relation]->(b)
    WHERE r.relation_id = $relation_id
    SET r += $updates
    RETURN r
    """
    with driver.session() as session:
        result = session.run(
            query,
            relation_id = rel_id,
            updates=updates
        )
        return result.single()[0] if result.peek() else None
    
def run_query(driver, query):
    
        with driver.session() as session:
            result = session.run(query)
            return result.data()
    
def export_jsonfields_to_excel(file_path='data.xlsx'):
    # Lấy danh sách JSON từ mỗi model
    data_gconc_list = list(GConc.objects.values_list('lstConC', flat=True))
    data_grel_list = list(gRel.objects.values_list('lstRel', flat=True))
    lstconc = set()
    lstgrel = set()
    for item in data_gconc_list:
        lstconc.add(item)
    for item in data_grel_list:
        lstgrel.add(item)
    
    data = pd.DataFrame({
        'concept': list(lstconc),
        'relation': list(lstgrel)
    }).to_csv(file_path)