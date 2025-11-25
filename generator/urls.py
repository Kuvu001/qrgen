from django.urls import path
from . import views

app_name = 'generator'

urlpatterns = [
    path('', views.index, name='index'),
    path('generate/', views.generate_qr, name='generate_qr'),
    path('download/<str:qr_filename>/', views.download_qr, name='download_qr'),
    path('api/generate/', views.api_generate_qr, name='api_generate_qr'),  # Optional API endpoint
    path('toggle-theme/', views.toggle_theme, name='toggle_theme'),

]
