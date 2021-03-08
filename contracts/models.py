from django.db import models
from django.conf import settings
import json
from django.utils import timezone

# Create your models here.
class Contract(models.Model):
    contract_number = models.CharField(max_length=10)
    company_code = models.CharField(max_length=3)
    product = models.CharField(max_length=25)
    operator = models.CharField(max_length=50)
    total_weight = models.PositiveIntegerField()
    contract_date = models.DateField()
    restrictions = models.CharField(max_length=20)
    curr_containers = models.JSONField()
    pend_containers = models.JSONField(null=True)
    datetime = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return(self.company_code)

