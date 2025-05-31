from ..models.file import file
from django.db import models

class Gtext(models.Model):
    # id = models.AutoField(primary_key=True)  # ID tự động tăng
    idLaw = models.ForeignKey(file, on_delete=models.CASCADE, related_name="component", null=True, blank=True)  # ID của luật
    descendants = models.JSONField(default=list, null=True, blank=True)  # Lưu danh sách các id con dưới dạng JSON
    content = models.TextField()  # Nội dung của văn bản
    ConcS = models.TextField(blank=True, null=True)  # Concept Subject
    Relation = models.TextField( blank=True, null=True)  # Quan hệ
    ConcO = models.TextField(blank=True, null=True)  # Concept Object

    class Meta:
        db_table = "gtext"

    def __str__(self):
        return f"Law {self.idLaw} - {self.id}"
