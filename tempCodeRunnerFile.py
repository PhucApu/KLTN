from transformers import RobertaTokenizerFast

# Tải tokenizer "fast" rõ ràng
tokenizer = RobertaTokenizerFast.from_pretrained("vinai/phobert-base", cache_dir="D:/Cache-hunging-face")

# Kiểm tra
print(f"Tokenizer class: {type(tokenizer).__name__}")
print(f"Is fast tokenizer: {tokenizer.is_fast}")

# Nếu không phải "fast", dừng chương trình
if not tokenizer.is_fast:
    raise ValueError("Không thể tải fast tokenizer cho vinai/phobert-base.")