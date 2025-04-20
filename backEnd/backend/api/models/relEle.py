# models.py
from django.db import models
from .file import file
from .concEle import Concele

class relEle(models.Model):
    IdLaw = models.ForeignKey(file, on_delete=models.CASCADE, related_name='concele_list')
    # Id = models.CharField(max_length=50, unique=True)
    relation = models.TextField(max_length=255)
    Meaning = models.TextField(blank=True, null=True)
    descendants = models.JSONField(blank=True, null=True,default=list)  # Danh sách con
    similar = models.IntegerField(blank=True, null=True)
    concS = models.ForeignKey(Concele, on_delete=models.CASCADE, related_name='concele_list')
    concO = models.ForeignKey(Concele, on_delete=models.CASCADE, related_name='concele_list')


    class Meta:
        db_table = "relele"
        

    def __str__(self):
        return f"{self.Id}: {self.relation}"
