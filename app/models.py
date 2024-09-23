from django.db import models

class DynamicExcelData(models.Model):
    data = models.JSONField() 

    @staticmethod
    def get_column_names():
        if DynamicExcelData.objects.exists():
            return DynamicExcelData.objects.first().data.keys()
        return []
