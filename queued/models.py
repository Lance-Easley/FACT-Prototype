from django.db import models

# Create your models here.
class QueuedContract(models.Model):
    contract = models.ForeignKey(
        'contracts.Contract', 
        on_delete=models.CASCADE
        )
    pend_containers = models.JSONField()
    def clean(self):
        if sum(self.pend_containers) != self.contract.total_weight
         raise ValidationError(
                {
                    "pend_containers": "Weight must equal total weight."
                }
            )