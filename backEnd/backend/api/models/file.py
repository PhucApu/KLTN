import os
import shutil
from django.db import models, transaction
from django.conf import settings
from docx2pdf import convert

 


class file(models.Model):
    file = models.FileField(upload_to=None, null=True, blank=True)  # Để đường dẫn tùy chỉnh
    status = models.IntegerField(default=1)
    name = models.CharField(max_length=255)
    upFile_at = models.DateTimeField(auto_now_add=True)
    is_use = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        temp_file_path = None  # Lưu đường dẫn file tạm thời

        if self.pk is None and self.file:  # Nếu là bản ghi mới và có file
            temp_file_path = self.file.path  # Đường dẫn file tạm trước khi lưu DB
        # Sử dụng transaction để đảm bảo tính toàn vẹn
        with transaction.atomic():
            super().save(*args, **kwargs)  # Lưu vào DB

            if temp_file_path:  # Nếu có file và đã lưu DB thành công
                try:
                    temp_file_founder = settings.MEDIA_ROOT
                    # print('có thể lỗi 1')
                    temp_file_path = os.path.join(temp_file_founder, self.file.name)
                    new_folder = os.path.join(settings.MEDIA_ROOT, f'{self.id}/')  # Tạo thư mục theo ID
                    # print('có thể lỗi 2')
                    os.makedirs(new_folder, exist_ok=True)  # Tạo thư mục nếu chưa có

                    
                    # print('có thể lỗi 3')

                    # Đường dẫn mới cho file gốc
                    new_file_path = os.path.join(new_folder, os.path.basename(self.file.name))
                    # print('có thể lỗi 4')

                    shutil.move(temp_file_path, new_file_path)  # Di chuyển file về thư mục theo ID
                    # print('có thể lỗi 4')
                    
                    # Định dạng file ban đầu
                    original_file_ext = os.path.splitext(self.file.name)[1].lower()
                    # Nếu file là Word (.docx hoặc .doc) → Chuyển sang PDF
                    if original_file_ext in [".docx"]:
                        # print('có thể lỗi 4')

                        pdf_file_path = new_file_path.replace(original_file_ext, ".pdf")  # Định dạng PDF
                        print(new_file_path, pdf_file_path)

                        # Chuyển Word sang PDF
                        convert(new_file_path, pdf_file_path)

                        # Lưu đường dẫn PDF vào database (có thể tạo thêm field pdf_file nếu muốn lưu riêng)
                        file_pdf_name = f'{self.id}/{os.path.basename(pdf_file_path)}'
                        file.objects.filter(pk=self.pk).update(file=file_pdf_name)
                        print('có thể lỗi 4')

                    else:
                        print('có thể lỗi 4')

                        # Nếu file là PDF, cập nhật đường dẫn
                        file.objects.filter(pk=self.pk).update(file=f'{self.id}/{os.path.basename(self.file.name)}')

                except Exception as e:
                    print(f"Lỗi khi xử lý file: {e}")
                    # shutil.rmtree(new_folder) 
                # finally:
                    # shutil.rmtree(os.path.join(temp_file_founder, 'None'))
    class Meta:
        db_table = "File"

    def __str__(self):
        return self.file.name if self.file else "No File"
