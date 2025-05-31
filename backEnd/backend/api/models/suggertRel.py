from django.db import models
from .relEle import relEle
class SuggestRel(models.Model):
    id1 = models.ForeignKey(relEle, on_delete=models.CASCADE, related_name='rel_suggest_from')
    id2 = models.ForeignKey(relEle, on_delete=models.CASCADE, related_name='rel_suggest_to')
    relation1 = models.TextField(blank=True, null=True)
    relation2 = models.TextField(blank=True, null=True)
    similar_index = models.FloatField()

    class Meta:
        unique_together = ('id1', 'id2')
        db_table = "suggestrel"

    def __str__(self):
        return f"{self.relation1} ~ {self.relation2} ({self.similar_index})"