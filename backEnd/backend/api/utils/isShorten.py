# from ..utils.VnCoreNLP import get_vncorenlp
from py_vncorenlp import VnCoreNLP

# vncorenlp_annotator = VnCoreNLP(
        #     save_dir = "C:\\Users\\baoqu\\Desktop\\KLTN\\Test\\backEnd\\backend\\api\\VnCoreNLP-master",
        #     annotators=["pos", "parse"],
        #     max_heap_size='-Xmx8g'
        # )
def is_shorten(text):
    if text == '': return 0
    print('sai chỗ VNcoreNLP')
    words = vncorenlp_annotator.annotate_text(text)[0]
    print(words)
    # words = output['text'][0]

    has_subject = False
    has_verb = False
    print('lỗi chỗ sử dụng')
    for word in words:
        if word['posTag'].startswith("V"):  # Nếu là động từ
            has_verb = True
        if word['depLabel'] in ["sub"]:  # Nếu có chủ ngữ
            has_subject = True
    print('hết hàm is_shorten')
    return has_verb and not has_subject