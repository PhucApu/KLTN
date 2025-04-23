import os
import sys
import django
import shutil
from django.core.management import call_command
from django.conf import settings

# Xác định thư mục gốc của dự án (chứa manage.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# Đặt biến môi trường Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

# Khởi động Django
django.setup()

def delete_migrations():
    """Xóa tất cả file migrations (trừ __init__.py)"""
    apps_dir = settings.BASE_DIR
    for app in os.listdir(apps_dir):
        migrations_path = os.path.join(apps_dir, app, "migrations")

        # Chỉ xóa file .py trong thư mục migrations (không xóa __pycache__)
        if os.path.exists(migrations_path):
            for file in os.listdir(migrations_path):
                file_path = os.path.join(migrations_path, file)
                if file.endswith(".py") and file != "__init__.py":  
                    os.remove(file_path)  # Chỉ xóa file .py
            print(f"✅ Đã xóa migrations trong {app} (không xóa __pycache__)")

def delete_media():
    """Xóa toàn bộ dữ liệu trong thư mục media/"""
    media_path = os.path.join(settings.BASE_DIR, "media")
    if os.path.exists(media_path):
        try:
            shutil.rmtree(media_path)  # Xóa cả thư mục và nội dung bên trong
            print("✅ Đã xóa thư mục media/")
        except Exception as e:
            print(f"❌ Không thể xóa thư mục media/: {e}")

def reset_database():
    """Xóa database, xóa migrations (trừ __pycache__), xóa thư mục media/ và chạy lại migrations"""
    try:
        # Xóa toàn bộ dữ liệu trong CSDL
        call_command("flush", "--no-input")
        print("✅ Đã xóa toàn bộ dữ liệu trong CSDL")

        # Xóa file migrations
        delete_migrations()

        # Xóa thư mục media/
        delete_media()

        # Chạy lại migrations
        call_command("makemigrations")
        call_command("migrate")
        print("✅ Đã chạy lại migrations thành công")

        # Khởi động lại server (tùy chọn)
        print("🚀 Khởi động lại server...")
        os.system("python manage.py runserver")

    except Exception as e:
        print(f"❌ Lỗi: {e}")

if __name__ == "__main__":
    reset_database()
