def get_unseen_pairs(id_pairs, exit_id_list):
    # Chuẩn hóa cả hai list: mỗi cặp được sort để không phân biệt thứ tự
    set_all = set(tuple(sorted(pair)) for pair in id_pairs)
    set_existing = set(tuple(sorted(pair)) for pair in exit_id_list)
    
    # Trừ tập hợp: lấy các cặp chưa có trong suggestconc
    result = set_all - set_existing
    
    # Trả về dạng list[list[int, int]]
    return [list(pair) for pair in result]
