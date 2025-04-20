import os
import shutil
from django.db import models, transaction
from django.conf import settings
import glob


class UpFile(models.Model):
    file = models.FileField(upload_to=None, null=True, blank=True)  # Để đường dẫn tùy chỉnh
    Status = models.IntegerField(default=1)
    Name = models.CharField(max_length=255)
    upFile_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        temp_file_path = None  # Lưu đường dẫn file tạm thời

        if self.pk is None and self.file:  # Nếu là bản ghi mới và có file
            temp_file_path = self.file.path  # Đường dẫn file tạm trước khi lưu DB

        # Sử dụng transaction để đảm bảo tính toàn vẹn
        with transaction.atomic():
           
                super().save(*args, **kwargs)  # Lưu vào DB
        
                if temp_file_path:  # Nếu có file và đã lưu DB thành công
                    try:
                        new_folder = os.path.join(settings.MEDIA_ROOT, f'{self.id}/')  # Tạo thư mục theo ID
                        new_path = os.path.join(new_folder, os.path.basename(self.file.name))  # Đường dẫn mới
                        
                        temp_file_path = os.path.join(settings.MEDIA_ROOT, f'None/')

                        os.makedirs(new_folder, exist_ok=True)  # Tạo thư mục nếu chưa có
                        # print(temp_file_path)
                        # print(shutil.move(temp_file_path, new_path))  # Di chuyển file vào thư mục {id}


                        for file_path in glob.glob(os.path.join(temp_file_path, "*.pdf")):  # Chỉ lấy file .txt
                            shutil.move(file_path, new_path)

                        # Cập nhật đường dẫn file trong DB
                        self.file.name = f'{self.id}/{os.path.basename(self.file.name)}'
                        # print(self.file.name)
                        UpFile.objects.filter(pk=self.pk).update(file=self.file.name)
                        # UpFile.objects.filter(pk=self.pk).update(id=1)
                        shutil.rmtree(temp_file_path)
                    except:
                        shutil.rmtree(new_path)
                        shutil.rmtree(temp_file_path)
    class Meta:
        db_table = "File"

    def __str__(self):
        return self.file.name if self.file else "No File"
