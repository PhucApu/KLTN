from django.db import models
from .concEle import Concele
class SuggestConc(models.Model):
    id1 = models.ForeignKey(Concele, on_delete=models.CASCADE, related_name='suggested_from')
    id2 = models.ForeignKey(Concele, on_delete=models.CASCADE, related_name='suggested_to')
    conc1 = models.TextField()
    conc2 = models.TextField()
    similar_index = models.FloatField()

    class Meta:
        db_table = "suggestconc"
        unique_together = ('id1', 'id2')

    def __str__(self):
        return f"{self.conc1} ~ {self.conc2} ({self.similar_index})"