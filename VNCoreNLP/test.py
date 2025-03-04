# from py_vncorenlp import VnCoreNLP

# # Đường dẫn tuyệt đối tới file .jar và models
# vncorenlp_dir = 'D:/SGU_University/HK8_(2025-2026)/KLTN/Project/VNCoreNLP'

# # Khởi tạo VnCoreNLP
# rdrsegmenter = VnCoreNLP(
#     annotators=["wseg"],
#     save_dir=vncorenlp_dir  # Thư mục chứa VnCoreNLP-1.2.jar và models
# )

# # Văn bản cần xử lý
# text = "Ông Nguyễn Khắc Chúc đang làm việc tại Đại học Quốc gia Hà Nội. Bà Lan, vợ ông Chúc, cũng làm việc tại đây."

# # Tách từ
# output = rdrsegmenter.word_segment(text)
# print(output)

# -----------------------------------------------------------

# from py_vncorenlp import VnCoreNLP

# # Đường dẫn tới thư mục chứa VnCoreNLP-1.2.jar và models
# vncorenlp_dir = 'D:/SGU_University/HK8_(2025-2026)/KLTN/Project/VNCoreNLP'

# # Khởi tạo VnCoreNLP
# rdrsegmenter = VnCoreNLP(
#     save_dir=vncorenlp_dir,
#     annotators=["wseg", "pos", "ner", "parse"],
#     max_heap_size='-Xmx2g'
# )

# # Văn bản cần phân tích
# text = "Ông Nguyễn Khắc Chúc đang làm việc tại Đại học Quốc gia Hà Nội."

# # Kiểm tra văn bản đầu vào
# print(f"Văn bản đầu vào: {text}")

# # Phân tích văn bản
# annotation = rdrsegmenter.annotate_text(text)

# # In kết quả phân tích
# print("=== Kết quả phân tích ===")
# print(annotation)

# # Kiểm tra và xử lý kết quả
# if annotation and "sentences" in annotation:
#     print("=== Kết quả phân đoạn từ (Word Segmentation) ===")
#     print(annotation["sentences"][0]["tokens"])

#     print("\n=== Kết quả gắn thẻ từ loại (POS Tagging) ===")
#     for word in annotation["sentences"][0]["tokens"]:
#         print(f"{word['form']} → {word['pos']}")

#     print("\n=== Kết quả nhận diện thực thể tên (NER) ===")
#     for word in annotation["sentences"][0]["tokens"]:
#         if word["ner"] != "O":
#             print(f"{word['form']} → {word['ner']}")

#     print("\n=== Kết quả phân tích cú pháp phụ thuộc (Dependency Parsing) ===")
#     for word in annotation["sentences"][0]["tokens"]:
#         print(f"{word['form']} (head: {word['head']} - relation: {word['deprel']})")
# else:
#     print("Không tìm thấy kết quả phân tích. Vui lòng kiểm tra đầu vào hoặc cấu hình.")
    
    
    
# -------------------------------------------------------


from py_vncorenlp import VnCoreNLP
import testNode, testNode2

# Đường dẫn tới thư mục chứa VnCoreNLP-1.2.jar và models
# vncorenlp_dir = 'D:/SGU_University/HK8_(2025-2026)/KLTN/Project/VNCoreNLP'

vncorenlp_dir = "D:/SGU_University/HK8_(2025-2026)/KLTN/Project/VNCoreNLP"

# Khởi tạo VnCoreNLP
rdrsegmenter = VnCoreNLP(
    save_dir=vncorenlp_dir,
    annotators=["wseg", "pos", "ner", "parse"],
    max_heap_size='-Xmx2g'
)

# Văn bản cần phân tích
text = "Chi phí đầu tư vào đất còn lại là chi phí hợp lý mà người sử dụng đất đã đầu tư trực tiếp vào đất phù hợp với mục đích sử dụng đất nhưng đến thời điểm Nhà nước thu hồi đất còn chưa thu hồi hết."

# text = "Ông Nguyễn Văn A gửi thư cho bà Nguyễn Thị B qua bưu điện."

# Kiểm tra văn bản đầu vào
print(f"Văn bản đầu vào: {text}")

# Phân tích văn bản
annotation = rdrsegmenter.annotate_text(text)

# In kết quả phân tích đầy đủ
print("=== Kết quả phân tích ===")
print(annotation)




# Hàm để chuyển đổi kết quả Dependency Parsing thành mảng đồ thị tri thức
def convert_to_knowledge_graph(tokens):
    knowledge_graph = []  # Lưu trữ kết quả đồ thị tri thức
    
    concept_1 = None
    relation = None
    concept_2 = None

    # Các từ loại liên quan đến danh từ và động từ
    noun_tags = {"N", "Nc", "Np", "P"}
    verb_tags = {"V"}

    # Lặp qua từng token
    for token in tokens:
        index = token["index"]
        word = token["wordForm"]
        pos = token["posTag"]
        head = token["head"]
        dep_label = token["depLabel"]

        # Nếu từ hiện tại là danh từ và chưa có concept_1
        if pos in noun_tags and concept_1 is None:
            concept_1 = word  # Đặt từ này làm concept_1

        # Nếu từ hiện tại là động từ và concept_1 đã được xác định
        elif pos in verb_tags and concept_1 is not None and relation is None:
            relation = word  # Đặt từ này làm relation

        # Nếu từ hiện tại là danh từ và relation đã xác định
        elif pos in noun_tags and relation is not None:
            concept_2 = word  # Đặt từ này làm concept_2
            # Thêm vào đồ thị tri thức
            knowledge_graph.append({
                "c1": concept_1,
                "relation": relation,
                "c2": concept_2
            })
            # Reset concept_1 và relation, tiếp tục phân tích
            concept_1 = concept_2
            relation = None
            concept_2 = None

    return knowledge_graph


# Kiểm tra và xử lý kết quả
if annotation:
    for sentence_id, tokens in annotation.items():
        print(f"\n=== Câu {sentence_id + 1} ===")
        
        # Phân đoạn từ
        print("Kết quả phân đoạn từ (Word Segmentation):")
        for token in tokens:
            print(token["wordForm"], end=' ')
        print("\n")
        
        # POS Tagging
        print("Kết quả gắn thẻ từ loại (POS Tagging):")
        for token in tokens:
            print(f"{token['wordForm']} → {token['posTag']}")
        print("\n")
        
        # NER (Nhận diện thực thể tên)
        print("Kết quả nhận diện thực thể tên (NER):")
        for token in tokens:
            if token["nerLabel"] != "O":  # Bỏ qua các từ không có thực thể
                print(f"{token['wordForm']} → {token['nerLabel']}")
        print("\n")
        
        # Dependency Parsing
        print("Kết quả phân tích cú pháp phụ thuộc (Dependency Parsing):")
        for token in tokens:
            print(f"Index: {token['index']}-{token['wordForm']} (head: {token['head']} - relation: {token['depLabel']})")
            
        # Vẽ biểu đồ tri thức
        # Chuyển đổi sang đồ thị tri thức
        # knowledge_graph = convert_to_knowledge_graph(tokens)
        # print("\n=== Đồ thị tri thức (dạng JSON) ===")
        # for edge in knowledge_graph:
        #     print(edge)
        
        # Các loại từ hợp lệ
        valid_pos = {"N", "Nc", "Np", "V"}

        # Quy trình xử lý
        nodes = testNode.build_graph(tokens)  # Bước 1: Xây dựng đồ thị ban đầu
        valid_nodes = testNode.filter_valid_nodes(nodes, valid_pos)  # Bước 2: Lọc các node hợp lệ
        testNode.reconnect_edges(nodes, valid_nodes)  # Bước 3: Kết nối lại các node
        testNode.display_graph(valid_nodes)  # Bước 4: Hiển thị đồ thị
        
        #  # Chuyển các token thành Node nếu cần
        # nodes = [testNode2.Node(**token) for token in tokens]
    
        # # Gọi hàm xây dựng đồ thị tri thức trong file testNode2.py
        # nodes_np, edges = testNode2.build_knowledge_graph_np(nodes)
        
        # print("Các concept (nodes):")
        # print(nodes_np)
        # print("\nCác mối quan hệ (edges):")
        # for subj, rel, obj in edges:
        #     print(f"{subj} -- {rel} --> {obj}")
            
        
else:
    print("Không tìm thấy kết quả phân tích. Vui lòng kiểm tra đầu vào hoặc cấu hình.")



