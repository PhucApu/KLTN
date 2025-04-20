from django.db import models
from .file import file
from .gConc import GConc
class gRel(models.Model):
    # id = models.CharField(primary_key=True, max_length=100)
    lstidlaw = models.JSONField(default=list)
    lstRel = models.JSONField(blank=True, null=True, default=list)
    meaning = models.TextField(blank=True, null=True)
    descendants = models.JSONField(blank=True, null=True, default=list)
    lstgConcS = models.JSONField(default=list)
    lstgConcO = models.JSONField(default=list)
    update_concs = models.JSONField(default=list,blank=True, null=True )
    update_conco = models.JSONField(default=list,blank=True, null=True )
    updaterel = models.IntegerField(default=0)

    def __str__(self):
        return f"GConc {self.id} ({self.meaning})"