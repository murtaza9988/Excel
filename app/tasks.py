from celery import shared_task
import pandas as pd
import json
import os
from django.core.files.storage import default_storage
from django.conf import settings
from .models import DynamicExcelData
from datetime import datetime, time


def handle_non_serializable(data):
    """
    This function converts non-serializable objects such as datetime and time to a serializable format.
    """
    for key, value in data.items():
        if isinstance(value, (datetime, pd.Timestamp)):
            # Convert datetime to string in ISO format
            data[key] = value.isoformat()
        elif isinstance(value, time):
            # Convert time to string in ISO format
            data[key] = value.strftime('%H:%M:%S')
    return data


@shared_task
def process_excel_file(file_path):
    """
    Process the Excel file and save data to the database.
    """
    try:
        df = pd.read_excel(file_path)

        # Delete previous records
        DynamicExcelData.objects.all().delete()

        # Process and save data
        for _, row in df.iterrows():
            data = row.to_dict()
            # Handle non-serializable data
            data = handle_non_serializable(data)
            json_data = json.dumps(data)  # Serialize data to JSON
            DynamicExcelData.objects.create(data=json_data)
    except Exception as e:
        print(f"Error processing the file: {e}")