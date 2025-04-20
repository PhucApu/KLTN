from py_vncorenlp import VnCoreNLP

# Định nghĩa biến toàn cục lưu mô hình
vncorenlp_annotator = None

def load_vncorenlp():
    """Khởi tạo mô hình VNCoreNLP khi server Django chạy."""
    global vncorenlp_annotator
    if vncorenlp_annotator is None:
        vncorenlp_annotator = VnCoreNLP(
            save_dir = "C:\\Users\\baoqu\\Desktop\\KLTN\\Test\\backEnd\\backend\\api\\VnCoreNLP-master",
            annotators=['pos','dep','wordseg'],
            max_heap_size='-Xmx4g'
        )

def get_vncorenlp():
    """Trả về mô hình đã được khởi tạo."""
    if vncorenlp_annotator is None:
        load_vncorenlp()
    return vncorenlp_annotator()
