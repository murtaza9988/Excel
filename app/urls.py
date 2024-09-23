from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('send_email/', views.send_email, name='send_email'),
    path('upload/', views.upload_excel, name='upload_excel'),
    path('upload/<str:folder_name>/', views.upload_excel, name='upload_folder'),
    path('upload/<str:folder_name>/<str:file_name>/', views.upload_excel, name='upload_file'),
]
