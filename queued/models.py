from django.db import models

# Create your models here.
class QueuedContract(models.Model):
    contract = models.ForeignKey(
        'contracts.Contract', 
        on_delete=models.CASCADE
        )
    pend_containers = models.JSONField()