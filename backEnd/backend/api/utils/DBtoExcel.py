import sqlite3
import pandas as pd

# Kết nối đến file SQLite
conn = sqlite3.connect('C:\\Users\\baoqu\\Desktop\\KLTN\\Test\\backEnd\\backend\\db.sqlite3')

# Đọc dữ liệu từ bảng (ví dụ: "users")
df = pd.read_sql_query("SELECT * FROM Component where is_theory = true", conn)

# Xuất ra file Excel
df.to_excel("Component.xlsx", index=False)

# Đóng kết nối
conn.close()

print("Xuất dữ liệu thành công!")


