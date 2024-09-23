import pandas as pd
import json
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import ExcelUploadForm
from .models import DynamicExcelData
import os
from django.core.mail import send_mail
from .tasks import process_excel_file
import requests
from dotenv import load_dotenv
load_dotenv()



# Access GitHub API settings
BASE_GITHUB_API_URL = os.getenv('BASE_GITHUB_API_URL')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

def download_file_from_github(file_url, save_path):
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3.raw'
    }
    response = requests.get(file_url, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors
    
    with open(save_path, 'wb') as file:
        file.write(response.content)


def upload_excel(request, folder_name=None, file_name=None):
    form = ExcelUploadForm()  # Initialize the form
    if file_name:
        file_url = f"{BASE_GITHUB_API_URL}/{folder_name}/{file_name}"
        local_save_path = os.path.join('/home/samar/Documents/UP-WORK/Chris#07/DataLeadsProject/core/data', file_name)
        try:
            download_file_from_github(file_url, local_save_path)
            print(f"File downloaded and saved to: {local_save_path}")
        except Exception as e:
            print(f"Error downloading file: {e}")
        pass_file_name = f"data/{file_name}"
        process_excel_file.delay(pass_file_name)
        return redirect('dashboard')  # Redirect after processing

    github_url = BASE_GITHUB_API_URL
    if folder_name:
        github_url = os.path.join(github_url, folder_name)

    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    response = requests.get(github_url, headers=headers)
    files_and_folders = response.json()
    print(f"==>> files_and_folders: {files_and_folders}")
    return render(request, 'app/upload.html', {'form': form, 'files': files_and_folders, 'folder_name': folder_name})


def dashboard(request):
    data = DynamicExcelData.objects.all().values_list('data', flat=True)
    data = [json.loads(item) for item in data]  # Convert JSON string to Python dict
    return render(request, 'app/dashboard.html', {'data': data})


def send_email(request):
    if request.method == 'POST':
        selected_indices = request.POST.getlist('selected_data')
        data = DynamicExcelData.objects.all().values_list('data', flat=True)
        data = [json.loads(item) for item in data]
        selected_data = [data[int(index)] for index in selected_indices]
        
        email_body = "Selected Data:\n\n"
        for item in selected_data:
            email_body += json.dumps(item, indent=4) + "\n\n"
        send_mail(
            'Selected Data from Dashboard',
            email_body, #Json
            settings.DEFAULT_FROM_EMAIL,
            [settings.RECIPIENT_EMAIL],  # Replace with the recipient's email
            fail_silently=False,
        )
        return redirect('dashboard')
    return redirect('dashboard')