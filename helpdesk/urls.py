from django.urls import path


from . import views

app_name = 'helpdesk'

urlpatterns = [
    # Adres /helpdesk/ będzie głowną stroną aplikacji - lista zgłoszeń, dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),
    # Formularz tworzenia zgłoszenia
    path('nowe/', views.ZgloszenieCreateView.as_view(), name='zgloszenie_nowe'),
    # Widok szczegołów danego zgłoszenia, np. /helpdesk/zgloszenie/5 (
    path('zgloszenie/<int:pk>/', views.ZgloszenieDetailView.as_view(), name='zgloszenie_detail'),
    path('zgloszenie/<int:pk>/przypisz/', views.ZgloszeniePrzypiszView.as_view(), name='zgloszenie_przypisz'),
    path('zgloszenie/<int:pk>/status/', views.ZgloszenieStatusView.as_view(), name='zgloszenie_status'),
]