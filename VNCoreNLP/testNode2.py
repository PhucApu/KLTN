from collections import defaultdict, deque

# Định nghĩa lớp Node
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
        return f"Node(index={self.index}, word='{self.wordForm}', pos='{self.posTag}', edges={self.edges})"


def build_children_mapping(nodes):
    """Tạo mapping từ một node (theo index) đến danh sách các node con của nó."""
    children = defaultdict(list)
    for node in nodes:
        if node.head != 0:
            children[node.head].append(node.index)
    return children


def is_np_head(node, node_dict):
    """
    Kiểm tra xem node có phải là NP head hay không.
    Ta xem một danh từ là NP head nếu:
      - Nó không có cha (head == 0) hoặc
      - Cha của nó không phải là danh từ, hoặc
      - Quan hệ nối với cha không thuộc tập các nhãn mở rộng (ví dụ: nmod, amod, det, compound, loc, pob)
    """
    if node.head == 0:
        return True
    parent = node_dict[node.head]
    allowed_upward = {'nmod', 'amod', 'det', 'compound', 'loc', 'pob'}
    if parent.posTag == 'N' and node.depLabel in allowed_upward:
        return False
    return True


def extract_np_phrase(np_head_index, children, node_dict, allowed_downward=None):
    """
    Từ NP head, duyệt cây con với các nhãn phụ thuộc cho phép và thu thập các node.
    Sau đó, sắp xếp theo thứ tự xuất hiện và ghép lại thành cụm.
    """
    if allowed_downward is None:
        allowed_downward = {'nmod', 'loc', 'adv', 'vmod', 'amod', 'det', 'compound', 'pob', 'conj'}
    indices = set()
    def dfs(idx):
        indices.add(idx)
        for child in children.get(idx, []):
            if node_dict[child].depLabel in allowed_downward:
                dfs(child)
    dfs(np_head_index)
    sorted_indices = sorted(indices)
    phrase = " ".join(node_dict[idx].wordForm for idx in sorted_indices)
    return phrase


def bfs_path(graph, start, goal):
    """Tìm đường đi ngắn nhất từ start đến goal trong đồ thị không hướng."""
    visited = {start}
    queue = deque([[start]])
    while queue:
        path = queue.popleft()
        current = path[-1]
        if current == goal:
            return path
        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = path + [neighbor]
                queue.append(new_path)
    return None


def build_dependency_graph(nodes):
    """Xây dựng đồ thị phụ thuộc không hướng từ danh sách Node."""
    graph = {}
    for node in nodes:
        idx = node.index
        graph.setdefault(idx, [])
        if node.head != 0:
            graph[idx].append(node.head)
            graph.setdefault(node.head, []).append(idx)
    return graph


def build_knowledge_graph_np(nodes):
    """
    Xây dựng đồ thị tri thức với các concept là cụm từ (NP) trích xuất từ dependency parsing.
    Các bước:
      1. Tạo từ điển node theo index và mapping từ node đến các node con.
      2. Với mỗi Node có posTag 'N', nếu là NP head (theo hàm is_np_head), trích xuất cụm NP.
      3. Xây dựng đồ thị phụ thuộc không hướng.
      4. Với mỗi cặp NP (đại diện bởi NP head), tìm đường đi ngắn nhất trên đồ thị. 
         Trong đường đi (ngoại trừ đầu và cuối), các node có posTag 'V' được ghép lại làm nhãn quan hệ.
    """
    # Tạo từ điển mapping từ index đến Node
    node_dict = {node.index: node for node in nodes}
    children = build_children_mapping(nodes)
    
    # Trích xuất NP (concept) từ các Node có posTag 'N'
    np_phrases = {}
    for node in nodes:
        if node.posTag == 'N' and is_np_head(node, node_dict):
            phrase = extract_np_phrase(node.index, children, node_dict)
            np_phrases[node.index] = phrase

    # Xây dựng đồ thị phụ thuộc không hướng
    dep_graph = build_dependency_graph(nodes)
    
    edges = []
    np_head_indices = list(np_phrases.keys())
    n = len(np_head_indices)
    for i in range(n):
        for j in range(i + 1, n):
            start = np_head_indices[i]
            end = np_head_indices[j]
            path = bfs_path(dep_graph, start, end)
            if path:
                # Lấy các node trung gian (loại trừ start và end)
                intermediate = path[1:-1]
                # Trích xuất các token có posTag là 'V' làm nhãn quan hệ
                relation_tokens = [node_dict[idx].wordForm for idx in intermediate if node_dict[idx].posTag == 'V']
                if relation_tokens:
                    relation = " ".join(relation_tokens)
                    edges.append((np_phrases[start], relation, np_phrases[end]))
    
    nodes_np = list(set(np_phrases.values()))
    return nodes_np, edges


# # --- Ví dụ sử dụng với dữ liệu đầu vào ---
# if __name__ == '__main__':
#     # Dữ liệu mẫu (dạng dictionary) được chuyển thành các Node
#     data = [
#         {'index': 1, 'wordForm': 'Chi_phí', 'posTag': 'N', 'nerLabel': 'O', 'head': 7, 'depLabel': 'sub'},
#         {'index': 2, 'wordForm': 'đầu_tư', 'posTag': 'V', 'nerLabel': 'O', 'head': 1, 'depLabel': 'nmod'},
#         {'index': 3, 'wordForm': 'vào', 'posTag': 'E', 'nerLabel': 'O', 'head': 1, 'depLabel': 'loc'},
#         {'index': 4, 'wordForm': 'đất', 'posTag': 'N', 'nerLabel': 'O', 'head': 3, 'depLabel': 'pob'},
#         {'index': 5, 'wordForm': 'còn', 'posTag': 'V', 'nerLabel': 'O', 'head': 4, 'depLabel': 'nmod'},
#         {'index': 6, 'wordForm': 'lại', 'posTag': 'R', 'nerLabel': 'O', 'head': 5, 'depLabel': 'adv'},
#         {'index': 7, 'wordForm': 'là', 'posTag': 'V', 'nerLabel': 'O', 'head': 0, 'depLabel': 'root'},
#         {'index': 8, 'wordForm': 'chi_phí', 'posTag': 'N', 'nerLabel': 'O', 'head': 7, 'depLabel': 'dob'},
#         {'index': 9, 'wordForm': 'hợp_lý', 'posTag': 'A', 'nerLabel': 'O', 'head': 8, 'depLabel': 'nmod'},
#         {'index': 10, 'wordForm': 'mà', 'posTag': 'C', 'nerLabel': 'O', 'head': 7, 'depLabel': 'coord'},
#         {'index': 11, 'wordForm': 'người', 'posTag': 'N', 'nerLabel': 'O', 'head': 15, 'depLabel': 'sub'},
#         {'index': 12, 'wordForm': 'sử_dụng', 'posTag': 'V', 'nerLabel': 'O', 'head': 11, 'depLabel': 'nmod'},
#         {'index': 13, 'wordForm': 'đất', 'posTag': 'N', 'nerLabel': 'O', 'head': 12, 'depLabel': 'dob'},
#         {'index': 14, 'wordForm': 'đã', 'posTag': 'R', 'nerLabel': 'O', 'head': 15, 'depLabel': 'adv'},
#         {'index': 15, 'wordForm': 'đầu_tư', 'posTag': 'V', 'nerLabel': 'O', 'head': 10, 'depLabel': 'conj'},
#         {'index': 16, 'wordForm': 'trực_tiếp', 'posTag': 'A', 'nerLabel': 'O', 'head': 15, 'depLabel': 'vmod'},
#         {'index': 17, 'wordForm': 'vào', 'posTag': 'E', 'nerLabel': 'O', 'head': 15, 'depLabel': 'loc'},
#         {'index': 18, 'wordForm': 'đất', 'posTag': 'N', 'nerLabel': 'O', 'head': 17, 'depLabel': 'pob'},
#         {'index': 19, 'wordForm': 'phù_hợp', 'posTag': 'V', 'nerLabel': 'O', 'head': 18, 'depLabel': 'nmod'},
#         {'index': 20, 'wordForm': 'với', 'posTag': 'E', 'nerLabel': 'O', 'head': 19, 'depLabel': 'vmod'},
#         {'index': 21, 'wordForm': 'mục_đích', 'posTag': 'N', 'nerLabel': 'O', 'head': 20, 'depLabel': 'pob'},
#         {'index': 22, 'wordForm': 'sử_dụng', 'posTag': 'V', 'nerLabel': 'O', 'head': 21, 'depLabel': 'nmod'},
#         {'index': 23, 'wordForm': 'đất', 'posTag': 'N', 'nerLabel': 'O', 'head': 22, 'depLabel': 'dob'},
#         {'index': 24, 'wordForm': 'nhưng', 'posTag': 'C', 'nerLabel': 'O', 'head': 7, 'depLabel': 'coord'},
#         {'index': 25, 'wordForm': 'đến', 'posTag': 'E', 'nerLabel': 'O', 'head': 32, 'depLabel': 'tmp'},
#         {'index': 26, 'wordForm': 'thời_điểm', 'posTag': 'N', 'nerLabel': 'O', 'head': 25, 'depLabel': 'pob'},
#         {'index': 27, 'wordForm': 'Nhà_Nước', 'posTag': 'N', 'nerLabel': 'O', 'head': 26, 'depLabel': 'nmod'},
#         {'index': 28, 'wordForm': 'thu_hồi', 'posTag': 'V', 'nerLabel': 'O', 'head': 26, 'depLabel': 'nmod'},
#         {'index': 29, 'wordForm': 'đất', 'posTag': 'N', 'nerLabel': 'O', 'head': 28, 'depLabel': 'dob'},
#         {'index': 30, 'wordForm': 'còn', 'posTag': 'R', 'nerLabel': 'O', 'head': 32, 'depLabel': 'adv'},
#         {'index': 31, 'wordForm': 'chưa', 'posTag': 'R', 'nerLabel': 'O', 'head': 32, 'depLabel': 'adv'},
#         {'index': 32, 'wordForm': 'thu_hồi', 'posTag': 'V', 'nerLabel': 'O', 'head': 24, 'depLabel': 'conj'},
#         {'index': 33, 'wordForm': 'hết', 'posTag': 'R', 'nerLabel': 'O', 'head': 32, 'depLabel': 'adv'},
#         {'index': 34, 'wordForm': '.', 'posTag': 'CH', 'nerLabel': 'O', 'head': 7, 'depLabel': 'punct'}
#     ]
    
#     # Tạo danh sách Node từ dữ liệu
#     nodes = [Node(**item) for item in data]
    
#     nodes_np, edges = build_knowledge_graph_np(nodes)
#     print("Các concept (nodes):")
#     print(nodes_np)
#     print("\nCác mối quan hệ (edges):")
#     for subj, rel, obj in edges:
#         print(f"{subj} -- {rel} --> {obj}")
