class Node:
    def __init__(self, index, wordForm, posTag, nerLabel, head, depLabel):
        self.index = index
        self.wordForm = wordForm
        self.posTag = posTag
        self.nerLabel = nerLabel
        self.head = head
        self.depLabel = depLabel
        self.edges = []  # Lưu danh sách các index của các node kết nối

    def add_edge(self, edge):
        self.edges.append(edge)

    def __repr__(self):
        return f"Node(index={self.index}, word='{self.word}', pos='{self.pos}', edges={self.edges})"


def build_graph(data):
    """Xây dựng đồ thị ban đầu từ dữ liệu"""
    nodes = {item["index"]: Node(item["index"], item["wordForm"], item["posTag"], item["nerLabel"], item["head"], item["depLabel"]) for item in data}
    for item in data:
        if item["head"] != 0:
            nodes[item["head"]].add_edge(item["index"])
    return nodes


def filter_valid_nodes(nodes, valid_pos):
    """Lọc các node chỉ giữ lại các node có pos hợp lệ"""
    return {index: node for index, node in nodes.items() if node.posTag in valid_pos}


def reconnect_edges(nodes, valid_nodes):
    """Kết nối lại các cạnh sau khi loại bỏ node không hợp lệ"""
    for index, node in list(valid_nodes.items()):
        new_edges = []
        for edge in node.edges:
            if edge in valid_nodes:  # Nếu node con hợp lệ
                new_edges.append(edge)
            else:  # Nếu node con không hợp lệ, kết nối lại với node cháu
                if edge in nodes:
                    for grandchild in nodes[edge].edges:
                        if grandchild in valid_nodes:
                            new_edges.append(grandchild)
        node.edges = new_edges


def display_graph(valid_nodes):
    """Hiển thị đồ thị"""
    for index, node in valid_nodes.items():
        for edge in node.edges:
            print(f"[{node.index}-{node.wordForm}] ---------- [{valid_nodes[edge].index}-{valid_nodes[edge].wordForm}]")
            
# # Hàm đệ quy theo chuỗi liên tục các động từ để tạo thành chuỗi quan hệ
# def follow_verb_chain(start_node, valid_nodes):
#     """
#     Từ một node bắt đầu (đã đảm bảo là động từ), nối các node con liên tiếp có pos là "V"
#     cho đến khi gặp một node con có pos là danh từ.
#     Trả về: (chuỗi relation, concept_2)
#     """
#     relation_chain = [start_node.wordForm]
#     current_node = start_node
#     # Duyệt tiếp nếu có con là động từ
#     while True:
#         verb_children = [valid_nodes[child] for child in current_node.edges if valid_nodes[child].posTag == "V"]
#         if not verb_children:
#             break
#         # Chọn node con có index nhỏ nhất (theo thứ tự)
#         next_verb = sorted(verb_children, key=lambda n: n.index)[0]
#         relation_chain.append(next_verb.wordForm)
#         current_node = next_verb

#     # Sau đó, từ node hiện tại, nếu có con là danh từ, chọn nó làm concept_2
#     noun_children = [valid_nodes[child] for child in current_node.edges if valid_nodes[child].posTag in {"N", "Nc", "Np"}]
#     concept_2 = ""
#     if noun_children:
#         concept_2 = sorted(noun_children, key=lambda n: n.index)[0].wordForm

#     return " ".join(relation_chain), concept_2


# # Hàm duyệt các node theo thứ tự index để trích xuất mảng đối tượng theo cấu trúc:
# # {"concept_1": "", "relation": "", "concept_2": ""}
# def extract_relations(valid_nodes):
#     relations_arr = []
#     # Duyệt các node theo thứ tự index tăng dần
#     for idx in sorted(valid_nodes.keys()):
#         node = valid_nodes[idx]
#         # Case 1: Nếu node là động từ và có cả nhánh chứa danh từ và nhánh chứa động từ
#         if node.posTag == "V":
#             noun_children = [valid_nodes[child] for child in node.edges if valid_nodes[child].posTag in {"N", "Nc", "Np"}]
#             verb_children = [valid_nodes[child] for child in node.edges if valid_nodes[child].posTag == "V"]
#             if noun_children and verb_children:
#                 # Chọn nhánh noun làm concept_1 (ví dụ, lấy node có index nhỏ nhất)
#                 concept_1 = sorted(noun_children, key=lambda n: n.index)[0].wordForm
#                 # Chọn nhánh verb làm bước nối, rồi theo chuỗi để lấy concept_2
#                 verb_child = sorted(verb_children, key=lambda n: n.index)[0]
#                 rel_chain, concept_2 = follow_verb_chain(verb_child, valid_nodes)
#                 # Full relation = node.word + " " + chuỗi từ verb chain
#                 full_relation = " ".join([node.wordForm, rel_chain]).strip()
#                 if concept_1 and full_relation and concept_2:
#                     relations_arr.append({
#                         "concept_1": concept_1,
#                         "relation": full_relation,
#                         "concept_2": concept_2
#                     })
#         # Case 2: Nếu node là danh từ và có nhánh chứa động từ, có thể tạo quan hệ mới
#         if node.posTag in {"N", "Nc", "Np"}:
#             verb_children = [valid_nodes[child] for child in node.edges if valid_nodes[child].posTag == "V"]
#             if verb_children:
#                 concept_1 = node.wordForm
#                 verb_child = sorted(verb_children, key=lambda n: n.index)[0]
#                 rel_chain, concept_2 = follow_verb_chain(verb_child, valid_nodes)
#                 full_relation = rel_chain  # Ở đây không ghép thêm gì vì concept_1 là node hiện tại
#                 if concept_1 and full_relation and concept_2:
#                     relations_arr.append({
#                         "concept_1": concept_1,
#                         "relation": full_relation,
#                         "concept_2": concept_2
#                     })
#     return relations_arr

def get_valid_subarrays(node_list):
    """
    Từ danh sách các node (đã sắp xếp theo index tăng dần) trả về danh sách các mảng con 
    thỏa các điều kiện:
      - Có đúng 1 node động từ (pos == "V")
      - Phần tử ngay trước và ngay sau node động từ là các node danh từ (pos thuộc {"N", "Nc", "Np"})
      - Mảng con được lấy liên tục.
    """
    result = []
    n = len(node_list)
    for i in range(n):
        for j in range(i+1, n+1):
            sub = node_list[i:j]  # mảng con liên tục
            # Đếm số node động từ trong subarray:
            verb_nodes = [node for node in sub if node.posTag == "V"]
            if len(verb_nodes) != 1:
                continue

            # Tìm vị trí của node động từ trong mảng con:
            verb_idx = None
            for k, node in enumerate(sub):
                if node.posTag == "V":
                    verb_idx = k
                    break

            # Điều kiện: node động từ không được ở đầu hoặc cuối mảng
            if verb_idx is None or verb_idx == 0 or verb_idx == len(sub)-1:
                continue

            # Kiểm tra rằng phần tử liền trước và liền sau node động từ đều là danh từ
            if sub[verb_idx - 1].posTag not in {"N", "Nc", "Np"} or sub[verb_idx + 1].posTag not in {"N", "Nc", "Np"}:
                continue

            # Nếu thỏa tất cả, thêm mảng con vào kết quả.
            result.append(sub)
    return result







# # Dữ liệu đầu vào
# data = [
#     {"index": 1, "word": "Ông", "posTag": "Nc", "head": 3, "depLabel": "sub"},
#     {"index": 2, "word": "Nguyễn_Văn_A", "pos": "Np", "head": 1, "depLabel": "nmod"},
#     {"index": 3, "word": "gửi", "pos": "V", "head": 0, "depLabel": "root"},
#     {"index": 4, "word": "thư", "pos": "N", "head": 3, "depLabel": "dob"},
#     {"index": 5, "word": "cho", "pos": "E", "head": 3, "depLabel": "iob"},
#     {"index": 6, "word": "bà", "pos": "Nc", "head": 5, "depLabel": "pob"},
#     {"index": 7, "word": "Nguyễn_Thị_B", "pos": "Np", "head": 6, "depLabel": "nmod"},
#     {"index": 8, "word": "qua", "pos": "E", "head": 3, "depLabel": "mnr"},
#     {"index": 9, "word": "bưu_điện", "pos": "N", "head": 8, "depLabel": "pob"},
#     {"index": 10, "word": ".", "pos": "CH", "head": 3, "depLabel": "punct"}
# ]

# # Các loại từ hợp lệ
# valid_pos = {"N", "Nc", "Np", "V"}

# # Quy trình xử lý
# nodes = build_graph(data)  # Bước 1: Xây dựng đồ thị ban đầu
# valid_nodes = filter_valid_nodes(nodes, valid_pos)  # Bước 2: Lọc các node hợp lệ
# reconnect_edges(nodes, valid_nodes)  # Bước 3: Kết nối lại các node
# display_graph(valid_nodes)  # Bước 4: Hiển thị đồ thị
