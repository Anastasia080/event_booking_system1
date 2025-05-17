from django.contrib import admin  # Добавьте этот импорт
from django.urls import path, include  # Добавьте include
from . import views

app_name = 'booking'

urlpatterns = [
    path('', views.home, name='home'),  # Один корневой путь
    path('events/', views.event_list, name='event_list'),  # Перенесли сюда
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('event/<int:event_id>/book/<int:seat_id>/', views.book_seat, name='book_seat'),
    path('create-event/', views.create_event, name='create_event'),
    path('edit-event/<int:event_id>/', views.create_event, name='edit_event'),
    path('venue-editor/', views.venue_editor, name='venue_editor'),
    path('venue-editor/<int:venue_id>/', views.venue_editor, name='venue_editor_with_id'),
    path('edit-seat/<int:seat_id>/', views.edit_seat, name='edit_seat'),
    path('about_event/<int:event_id>/', views.about_event, name='about_event'),
    path('login/', views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.LogoutView.as_view(template_name='registration/logout.html'), name='logout'),
    path('register/', views.register, name='register'),
]