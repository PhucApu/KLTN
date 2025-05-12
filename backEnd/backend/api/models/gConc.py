from django.db import models
from .file import file
from .concEle import Concele
class GConc(models.Model):
    # id = models.CharField(primary_key=True, max_length=100)
    lstid = models.JSONField(default=list)
    lstidlaw = models.JSONField(default=list)
    lstConC = models.JSONField(blank=True, null=True, default=list)
    meaning = models.TextField(blank=True, null=True)
    descendants = models.JSONField(blank=True, null=True, default=list)
    updateNeo4j = models.IntegerField(default=1)


    def __str__(self):
        return f"GConc {self.id} ({self.meaning})"