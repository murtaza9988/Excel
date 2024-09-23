import pandas as pd
from django.core.management.base import BaseCommand
from django.db import models
from django.apps import apps
from django.conf import settings

class Command(BaseCommand):
    help = 'Imports data from an Excel file and creates models dynamically based on columns'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str)

    def handle(self, *args, **kwargs):
        excel_file = kwargs['excel_file']
        df = pd.read_excel(excel_file)

        # Dynamically create a new model
        model_name = 'DynamicExcelModel'
        fields = {
            col: models.CharField(max_length=255, blank=True, null=True)
            for col in df.columns
        }

        class Meta:
            db_table = model_name.lower()

        attrs = {'__module__': 'app.models', 'Meta': Meta}
        attrs.update(fields)
        DynamicModel = type(model_name, (models.Model,), attrs)

        # Register the new model with the app registry
        app_label = 'app'
        if app_label not in settings.INSTALLED_APPS:
            settings.INSTALLED_APPS.append(app_label)
        apps.all_models[app_label][model_name] = DynamicModel

        # Create migrations for the new model
        from django.core.management import call_command
        call_command('makemigrations', app_label)
        call_command('migrate', app_label)

        # Insert data from the Excel file
        for index, row in df.iterrows():
            row_data = {col: str(row[col]) for col in df.columns}
            DynamicModel.objects.create(**row_data)

        self.stdout.write(self.style.SUCCESS(f'Successfully imported data and created model {model_name}.'))
