from django.urls import path


from . import views

app_name = 'helpdesk'

urlpatterns = [
    # Adres /helpdesk/ będzie głowną stroną aplikacji - lista zgłoszeń, dashboard
    path('', views.DashboardView_as_view(), name='Dashboard'),
    # Formularz tworzenia zgłoszenia
    path('nowe/', views.ZgloszenieCreateView.as_view(), name='zgloszenie_nowe'),
    # Widok szczegołów danego zgłoszenia, np. /helpdesk/zgloszenie/5 (
    path('zgloszenie/<int:pk>/', views.ZgoszenieDetailView.as_view(), name='zgloszenie_detail'),
]