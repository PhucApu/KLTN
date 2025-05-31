from django.db import models
from ..models.file import file

class component(models.Model):
    # id = models.BigIntegerField(primary_key=True)
    idLaw = models.ForeignKey(file, on_delete=models.CASCADE, related_name="component", null=True, blank=True)
    parent = models.BigIntegerField(null=True, blank=True)
    name = models.TextField(max_length=255, null=True, blank=True)
    content = models.TextField(null=True, blank= True)
    contentSearch = models.TextField(null=True, blank= True)
    child = models.JSONField(default=list, null=True, blank=True)
    descendants = models.JSONField(default=list, null=True, blank=True)
    is_shorten = models.BooleanField(default=False, null=True, blank=True)
    is_theory = models.BooleanField(default=False, null=True, blank=True)

    class Meta:
        db_table = "Component"

    def __str__(self):
        return self.name
    
