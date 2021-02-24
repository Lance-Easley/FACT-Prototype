from django.db import models

### Company Codes ###
# BRC - Bright Cargo
# JNL - Jacks N-L
# AXM - Axiom
# PDT - Prudent Transport

# Create your models here.
class Container(models.Model):
    company_code = models.CharField(max_length=3)
    unit_descriptor = models.CharField(max_length=15)
    unit_code = models.PositiveIntegerField()
    restrict_code = models.CharField(max_length=5)
    rating = models.PositiveIntegerField()
    bl_link = models.URLField()
    coc_link = models.URLField()

    def __str__(self):
        return(self.unit_descriptor)