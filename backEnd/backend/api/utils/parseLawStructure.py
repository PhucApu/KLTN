from docx import Document
import re
from ..models.component import component
from ..models.file import file
from ..utils.Tool import fileToFile
import pandas as pd

def parse_law_structure(file_id):
    try:
            file_obj = file.objects.get(id=file_id)
    except file.DoesNotExist:
            return False
    file_path = fileToFile(filepath = file_obj.file.name,fileName= file_obj.file.name.split('/')[1],new_file_ext= '.docx')
    # Tạo node gốc đại diện cho file
    
    doc = Document(file_path)
    raw_text = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
    text = "\n".join(raw_text)

    try:
        nodes = parse_law(text=text, document_name=file_obj.name,parent_id= file_id)
    except Exception as e:
        print(e)
    return nodes, file_obj
    
    # try:
    #     for index, row in nodes.iterrows():
    #         component.objects.create(
    #         id = row['id'],
    #         name = row['name'],
    #         parent = row['parent'],
    #         child = row['child'],
    #         content = row['content'],
    #         descendants = row['descendants'],
    #         idLaw = file_obj,
    #         is_shorten = is_shorten(row['content']),
    #         is_theory = is_theory(row['content']),
    #         )
    # except Exception as e:
    #     print(e)
    # print('đúng hết rồi')


def parse_law(text, document_name, parent_id):
    lines = text.split("\n")
    nodes = []
    stack = []  # Used to store hierarchical structure
    id_counter = parent_id*10000 + 1  # Start ID from the largest parent node +1
    id_first = parent_id*10000 + 1 
    node_dict = {}  # Store all nodes by ID
    # Create root node from document_name
    root_node = {
        "id": parent_id,
        "parent": 0,
        "child": [],
        "descendants": [parent_id],
        "name": document_name.strip(),
        "content": ""
    }

    nodes.append(root_node)
    node_dict[parent_id] = root_node
    stack.append(("document", root_node))

    
    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Identify level  ^(Chương\s+[IVXLCDM]+)\.\s*(.*?)
        
        match_chapter = re.match(r"^(Chương\s+[IVXLCDM]+)\s*\n*\s*(.*?)", line)
        match_section = re.match(r"^(Mục\s+\w+)\.(.*)", line)
        match_article = re.match(r"^(Điều\s+\d+)\.(.*)", line)
        match_clause = re.match(r"^(\d+)\.\s*(.*)", line)
        match_point = re.match(r"^([a-zA-Z])\)\s*(.*)", line)
        level_order = ["document", "chapter", "section", "article", "clause", "point"]

        if match_chapter or match_section:
            continue
        elif match_article:
            title, content = match_article.groups()
            level = "article"
        elif match_clause:
            title, content = match_clause.groups()
            level = "clause"
            title = f"khoản {title.strip()}"
        elif match_point:
            title, content = match_point.groups()
            level = "point"
            title = f"điểm {title.strip()}"
        else:
            # Append content to the last node
            if id_counter != id_first:
                stack[-1][1]["content"] += " " + line.strip()
                continue
            else:
                continue

        # Determine parent node
        while stack and level_order.index(stack[-1][0]) >= level_order.index(level):
            stack.pop()
        
        if level == "article":
            # If there's no section before, article belongs to the last chapter
            parent_node = next((node for level_name, node in reversed(stack) if level_name in ["chapter", "section"]), root_node)
        else:
            parent_node = stack[-1][1] if stack else root_node
        
        node = {
            "id": id_counter,
            "parent": parent_node["id"],
            "child": [],
            "descendants": [id_counter],
            "name": title.strip(),
            "content": content.strip()
        }
        stack.append((level, node))

        # Update parent-child relationships
        parent_node["child"].append(id_counter)

        # Update descendants for all ancestors
        ancestor = parent_node
        while ancestor:
            ancestor["descendants"].append(id_counter)
            ancestor = node_dict.get(ancestor["parent"])

        nodes.append(node)
        node_dict[id_counter] = node
        id_counter += 1
    print('hết hàm chuyển')
    return pd.DataFrame(nodes)




