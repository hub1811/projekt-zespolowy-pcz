from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.db.models import Count
from .models import Zgloszenie
from .forms import ZgloszenieForm, KomentarzForm


from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.db.models import Count

from .models import Zgloszenie
from .forms import ZgloszenieForm, KomentarzForm


class DashboardView(View):
    def get(self, request):
        status_filter = request.GET.get("status", "")
        kategoria_filter = request.GET.get("kategoria", "")

        # bazowe zgłoszenia
        zgloszenia_qs = Zgloszenie.objects.all()

        if status_filter:
            zgloszenia_qs = zgloszenia_qs.filter(status=status_filter)

        if kategoria_filter:
            zgloszenia_qs = zgloszenia_qs.filter(kategoria=kategoria_filter)

        zgloszenia_qs = zgloszenia_qs.order_by("-id")

        # zliczenie zgłoszeń po statusie (co realnie jest w bazie)
        status_counts = (
            Zgloszenie.objects
            .values("status")
            .annotate(count=Count("pk"))
        )

        # mapa: status -> ile zgłoszeń (lub 0, jeśli brak)
        count_map = {row["status"]: row["count"] for row in status_counts}

        # definicja 3 kafelków – zawsze te same
        status_cards = [
            {
                "code": "NOWE",
                "label": "Status NOWE",
                "count": count_map.get("NOWE", 0),
            },
            {
                "code": "W_TOKU",
                "label": "Status W toku",
                "count": count_map.get("W_TOKU", 0),
            },
            {
                "code": "ROZWIAZANE",
                "label": "Status Rozwiazane",
                "count": count_map.get("Rozwiazane", 0),
            },
        ]

        context = {
            "zgloszenia": zgloszenia_qs,
            "status_cards": status_cards,
            "status_filter": status_filter,
            "kategoria_filter": kategoria_filter,
            "total_count": Zgloszenie.objects.count(),
        }
        return render(request, "dashboard.html", context)


class ZgloszenieCreateView(View):
    def get(self, request):
        form = ZgloszenieForm()
        return render(request, "zgloszenie_form.html", {"form": form})

    def post(self, request):
        form = ZgloszenieForm(request.POST)
        if form.is_valid():
            zgloszenie = form.save(commit=False)
            zgloszenie.zgloszone_przez = request.user
            zgloszenie.save()
            return redirect("helpdesk:zgloszenie_detail", pk=zgloszenie.pk)
        return render(request, "zgloszenie_form.html", {"form": form})


class ZgloszenieDetailView(View):
    def get(self, request, pk):
        zgloszenie = get_object_or_404(Zgloszenie, pk=pk)
        komentarze = zgloszenie.komentarze.all()
        form = KomentarzForm()
        return render(request, "zgloszenie_detail.html", {
            "zgloszenie": zgloszenie,
            "komentarze": komentarze,
            "form": form,
        })

    def post(self, request, pk):
        zgloszenie = get_object_or_404(Zgloszenie, pk=pk)
        form = KomentarzForm(request.POST)
        if form.is_valid():
            komentarz = form.save(commit=False)
            komentarz.zgloszenie = zgloszenie
            komentarz.autor = request.user
            komentarz.save()
            return redirect("helpdesk:zgloszenie_detail", pk=zgloszenie.pk)

        komentarze = zgloszenie.komentarze.all()
        return render(request, "zgloszenie_detail.html", {
            "zgloszenie": zgloszenie,
            "komentarze": komentarze,
            "form": form,
        })
