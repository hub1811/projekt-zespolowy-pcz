from django.shortcuts import render
from django.views import View
from django.http import HttpResponse

# Create your views here.

class DashboardView(View):
    def get(self, request):
        return render(request, "dashboard.html")
    
class ZgloszenieCreateView(View):
    def get(self, request):
        return HttpResponse("Tu będzie formularz tworzenia zgłoszenia.")


class ZgloszenieDetailView(View):
    def get(self, request, pk):
        return HttpResponse(f"Szczegóły zgłoszenia o ID: {pk}")