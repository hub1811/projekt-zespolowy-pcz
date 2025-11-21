from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.db.models import Count
from .models import Zgloszenie
from .forms import ZgloszenieForm, KomentarzForm


from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.db.models import Count

from .models import Zgloszenie
from .forms import ZgloszenieForm, KomentarzForm, PrzypiszZgloszenieForm


class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        status_filter = request.GET.get("status", "")
        kategoria_filter = request.GET.get("kategoria", "")

        user = request.user

        # === 1. LOGIKA UPRAWNIEŃ (POPRAWIONE NAZWY GRUP) ===
        is_manager = user.groups.filter(name='IT Manager').exists()
        is_pracownik_it = user.groups.filter(name='Pracownik IT').exists()

        # Domyślny queryset (pusty, zostanie nadpisany)
        zgloszenia_qs = Zgloszenie.objects.none()

        if is_manager:
            # IT Manager widzi wszystko
            zgloszenia_qs = Zgloszenie.objects.all()
        elif is_pracownik_it:
            # Pracownik IT widzi przypisane do siebie
            zgloszenia_qs = Zgloszenie.objects.filter(przypisane_do=user)
        else:
            # "Użytkownik" (i każdy inny) widzi tylko swoje
            zgloszenia_qs = Zgloszenie.objects.filter(zgloszone_przez=user)

        # === 2. FILTROWANIE (bez zmian) ===
        if status_filter:
            zgloszenia_qs = zgloszenia_qs.filter(status=status_filter)
        if kategoria_filter:
            zgloszenia_qs = zgloszenia_qs.filter(kategoria=kategoria_filter)

        zgloszenia_qs = zgloszenia_qs.order_by("-id")

        # === 3. STATYSTYKI (bez zmian) ===
        status_counts = Zgloszenie.objects.values("status").annotate(count=Count("pk"))
        count_map = {row["status"]: row["count"] for row in status_counts}

        status_cards = [
            {"code": "NOWE", "label": "Status NOWE", "count": count_map.get("NOWE", 0)},
            {"code": "W_TOKU", "label": "Status W toku", "count": count_map.get("W_TOKU", 0)},
            {"code": "ROZWIAZANE", "label": "Status Rozwiazane", "count": count_map.get("ROZWIAZANE", 0)},
        ]

        context = {
            "zgloszenia": zgloszenia_qs,
            "status_cards": status_cards,
            "status_filter": status_filter,
            "kategoria_filter": kategoria_filter,
            "total_count": zgloszenia_qs.count(),  # Lepiej liczyć przefiltrowane
            "is_manager": is_manager,  # Przekazujemy info o roli do template
        }
        return render(request, "dashboard.html", context)


class ZgloszenieCreateView(LoginRequiredMixin, View):
    # ... (bez zmian, kod jak wcześniej) ...
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


class ZgloszenieDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        zgloszenie = get_object_or_404(Zgloszenie, pk=pk)
        komentarze = zgloszenie.komentarze.all()
        form_komentarz = KomentarzForm()

        # === POPRAWKA NAZWY GRUPY ===
        is_manager = request.user.groups.filter(name='IT Manager').exists()

        form_przypisania = None
        if is_manager:
            form_przypisania = PrzypiszZgloszenieForm(instance=zgloszenie)

        return render(request, "zgloszenie_detail.html", {
            "zgloszenie": zgloszenie,
            "komentarze": komentarze,
            "form": form_komentarz,
            "form_przypisania": form_przypisania,
            "is_manager": is_manager,
        })

    def post(self, request, pk):
        # Obsługa dodawania komentarza (bez zmian)
        zgloszenie = get_object_or_404(Zgloszenie, pk=pk)
        form = KomentarzForm(request.POST)

        if form.is_valid():
            komentarz = form.save(commit=False)
            komentarz.zgloszenie = zgloszenie
            komentarz.autor = request.user
            komentarz.save()
            return redirect("helpdesk:zgloszenie_detail", pk=zgloszenie.pk)

        # Obsługa błędu walidacji - odtwarzamy kontekst
        komentarze = zgloszenie.komentarze.all()
        # === POPRAWKA NAZWY GRUPY ===
        is_manager = request.user.groups.filter(name='IT Manager').exists()
        form_przypisania = PrzypiszZgloszenieForm(instance=zgloszenie) if is_manager else None

        return render(request, "zgloszenie_detail.html", {
            "zgloszenie": zgloszenie,
            "komentarze": komentarze,
            "form": form,
            "form_przypisania": form_przypisania,
            "is_manager": is_manager,
        })


class ZgloszeniePrzypiszView(LoginRequiredMixin, View):
    def post(self, request, pk):
        zgloszenie = get_object_or_404(Zgloszenie, pk=pk)

        # === POPRAWKA NAZWY GRUPY ===
        # Zabezpieczenie: tylko IT Manager może wykonać tę akcję
        if not request.user.groups.filter(name='IT Manager').exists():
            # Jeśli ktoś próbuje oszukać, odsyłamy go z powrotem
            return redirect("helpdesk:zgloszenie_detail", pk=pk)

        form = PrzypiszZgloszenieForm(request.POST, instance=zgloszenie)
        if form.is_valid():
            form.save()

        return redirect("helpdesk:zgloszenie_detail", pk=pk)
