# models.py
from django.db import models
from .file import file

class Concele(models.Model):
    IdLaw = models.ForeignKey(file, on_delete=models.CASCADE, related_name='concele_list')
    # Id = models.CharField(max_length=50, unique=True)
    conC = models.TextField(blank=True, null=True)
    Meaning = models.TextField(blank=True, null=True)
    descendants = models.JSONField(blank=True, null=True, default=list)  # Danh sách con
    similar = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "concele"

    def __str__(self):
        return f"{self.Id}: {self.ConC}"
