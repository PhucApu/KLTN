import os
from docx import Document
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from ..models.gConc import GConc
from ..models.gRel import gRel
from ..models.concEle import Concele
from docx2pdf import convert
import pandas as pd
import pypandoc
from django.db.models import Q
# kiểm tra sự tồn tại của 01 node
import os
from django.conf import settings
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
    start_node_id = Concele.objects.filter(id = start_node_id).first().similar
    end_node_id = Concele.objects.filter(id = end_node_id).first().similar
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
    file1 = os.path.join(settings.MEDIA_ROOT, "listconcept.docx")
    file2 = os.path.join(settings.MEDIA_ROOT, "listrelation.docx")
    merged_file = "merged.docx"
    pdf_file = "merged.pdf"
    if not os.path.exists(file1):
        create_docx_with_table(file1,"Concept")

    if not os.path.exists(file2):
        create_docx_with_table(file2,'Relation')
    
    lstNode = GConc.objects.filter(updateNeo4j = 1)
    for item in lstNode:
            pass

def create_docx_with_table(filename,header):
    try:
        doc = Document()
        table = doc.add_table(rows=2, cols=1)
        table.style = 'Table Grid'
        table.cell(0, 0).text = header
        table.cell(1, 0).text = ""
        doc.save(filename)
    except Exception as e:
        return False
    return False

def merge_documents(file1, file2, output_file):
        doc1 = Document(file1)
        doc2 = Document(file2)
        doc1.add_paragraph("")
        for element in doc2.element.body:
            doc1.element.body.append(element)
        doc1.save(output_file)
        return output_file
    

def convert_to_pdf(input_docx, output_pdf):
    try:
        pypandoc.convert_file(input_docx, 'pdf', outputfile=output_pdf)
        return output_pdf
    except Exception as e:
        print("Lỗi khi chuyển sang PDF:", e)
        return False
    
from docx import Document

def read_second_row_from_table(filename):
    doc = Document(filename)
    table = doc.tables[0]  # lấy bảng đầu tiên
    if len(table.rows) >= 2:
        text = table.rows[1].cells[0].text
        result = set(item.strip() for item in text.split(','))
        return result
    else:
        return False

def overload():
    filename1 = os.path.join(settings.MEDIA_ROOT,  "listconcept.docx")
    if os.path.exists(filename1):
        doc = Document(filename1)
    else:
        doc = Document()
        doc.add_table(rows=2, cols=1)
         

    if doc.tables:
        table = doc.tables[0]
        table.style = 'Table Grid'

    else:
        print("File không có bảng nào, đang tạo bảng mới...")
        table = doc.add_table(rows=2, cols=1)
        table.style = 'Table Grid'

    
    items = set()
    while len(table.rows) < 2:
        table.add_row()
    table.cell(0,0).text= 'concept'
    text = table.cell(1,0).text
    if text:
        items = set(item.strip() for item in text.split(','))
    lstNode = GConc.objects.filter(updateNeo4j = 1)
    for node in lstNode:
        items.update(set(node.lstConC))
    lstNode = GConc.objects.filter(updateNeo4j = 2)
    for node in lstNode:
        items.update(set(node.lstConC))
    table.rows[1].cells[0].text = ', '.join(items)
    doc.save(filename1)

    filename2 = os.path.join(settings.MEDIA_ROOT, "listrelation.docx")
    if os.path.exists(filename2):
        doc = Document(filename2)
    else:
        doc = Document()
        doc.add_table(rows=2, cols=1) 

    if doc.tables:
        table = doc.tables[0]
        table.style = 'Table Grid'

    else:
        print("File không có bảng nào, đang tạo bảng mới...")
        table = doc.add_table(rows=2, cols=1)
        table.style = 'Table Grid'

    
    items = set()
    while len(table.rows) < 2:
        table.add_row()
    table.cell(0,0).text= 'relation'
    text = table.cell(1,0).text
    if text:
        items = set(item.strip() for item in text.split(','))
    lstRelation = gRel.objects.filter(updaterel = 1)
    for relation in lstRelation:
        items.update(set(relation.lstRel))
    lstRelation = gRel.objects.exclude(Q(update_concs=None)| Q(update_concs=[]))
    for relation in lstRelation:
        items.update(set(relation.lstRel))
    table.rows[1].cells[0].text = ','.join(items)
    doc.save(filename2)

    # word_merge = merge_documents(file1=filename1, file2 = filename2,output_file= os.path.join(settings.MEDIA_ROOT, 'merge_content.docx'))
    # pdf_merge = convert(word_merge,os.path.join(settings.MEDIA_ROOT, "merge_content.pdf"))
    return True


def get_key_phase(filename):
    filename = os.path.join(settings.MEDIA_ROOT,  filename)
    doc = Document(filename)
    table = doc.tables[0]
    key = table.rows[0].cells[0].text.strip()
    value = table.rows[1].cells[0].text.strip()
    data = {key: value}
    return data

