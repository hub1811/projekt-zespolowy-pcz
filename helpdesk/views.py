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
from .forms import ZgloszenieForm, KomentarzForm, PrzypiszZgloszenieForm, ZmienStatusForm


class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        status_filter = request.GET.get("status", "")
        kategoria_filter = request.GET.get("kategoria", "")
        sort_field = request.GET.get("sort", "id")
        sort_dir = request.GET.get("dir", "desc").lower()

        allowed_sorts = {
            "id": "id",
            "tytul": "tytul",
            "kategoria": "kategoria",
            "status": "status",
            "priorytet": "priorytet",
            "data": "data_utworzenia",
        }

        if sort_field not in allowed_sorts:
            sort_field = "id"
        if sort_dir not in ("asc", "desc"):
            sort_dir = "desc"
        order_expr = allowed_sorts[sort_field]
        if sort_dir == "desc":
            order_expr = f"-{order_expr}"

        user = request.user

        # === 1. LOGIKA UPRAWNIEŃ ===
        # Najpierw ustalamy, CO użytkownik może widzieć
        is_manager = user.groups.filter(name='IT Manager').exists()
        is_pracownik_it = user.groups.filter(name='Pracownik IT').exists()

        # Bazowy QuerySet (pusty)
        zgloszenia_qs = Zgloszenie.objects.none()

        if is_manager:
            # Manager widzi wszystko
            zgloszenia_qs = Zgloszenie.objects.all()
        elif is_pracownik_it:
            # Pracownik IT widzi przypisane do siebie
            zgloszenia_qs = Zgloszenie.objects.filter(przypisane_do=user)
        else:
            # Zwykły użytkownik widzi tylko swoje
            zgloszenia_qs = Zgloszenie.objects.filter(zgloszone_przez=user)

        # === 2. STATYSTYKI (PRZENIESIONE TUTAJ) ===
        # Obliczamy statystyki NA BAZIE przefiltrowanej listy (zgloszenia_qs),
        # a nie wszystkich obiektów w bazie.

        # Całkowita liczba zgłoszeń (dla tego użytkownika)
        total_count = zgloszenia_qs.count()

        # Zliczanie po statusach
        status_counts = zgloszenia_qs.values("status").annotate(count=Count("pk"))
        count_map = {row["status"]: row["count"] for row in status_counts}

        # Definicja kafelków
        status_cards = [
            {
                "label": "Nowe",
                "count": count_map.get("NOWE", 0),
                "color": "primary"  # Opcjonalnie do kolorowania
            },
            {
                "label": "W toku",
                "count": count_map.get("W_TOKU", 0),
                "color": "warning"
            },
            {
                "label": "Rozwiązane",
                "count": count_map.get("ROZWIAZANE", 0),  # Pamiętaj o dokładnej nazwie statusu z bazy!
                "color": "success"
            },
        ]

        # === 3. FILTROWANIE LISTY (Dla tabeli na dole) ===
        # Filtrowanie po parametrach z paska adresu (np. ?status=NOWE)
        # robimy DOPIERO PO obliczeniu statystyk, żeby kafelki zawsze pokazywały
        # ogólny stan konta użytkownika, a nie zmieniały się po kliknięciu w filtr.

        zgloszenia_do_wyswietlenia = zgloszenia_qs

        if status_filter:
            zgloszenia_do_wyswietlenia = zgloszenia_do_wyswietlenia.filter(status=status_filter)
        if kategoria_filter:
            zgloszenia_do_wyswietlenia = zgloszenia_do_wyswietlenia.filter(kategoria=kategoria_filter)

        zgloszenia_do_wyswietlenia = zgloszenia_do_wyswietlenia.order_by(order_expr)

        context = {
            # Do tabeli przekazujemy listę po dodatkowych filtrach
            "zgloszenia": zgloszenia_do_wyswietlenia,

            # Do kafelków i licznika przekazujemy dane sprzed filtrów statusu/kategorii
            "status_cards": status_cards,
            "total_count": total_count,

            "status_filter": status_filter,
            "kategoria_filter": kategoria_filter,
            "is_manager": is_manager,
            "sort_field": sort_field,
            "sort_dir": sort_dir,
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

        # Sprawdzamy grupy
        is_manager = request.user.groups.filter(name='IT Manager').exists()
        is_pracownik_it = request.user.groups.filter(name='Pracownik IT').exists()

        # "Staff" to ktoś, kto może zmieniać status (Manager LUB Pracownik IT)
        is_staff = is_manager or is_pracownik_it

        form_przypisania = None
        form_status = None

        if is_manager:
            form_przypisania = PrzypiszZgloszenieForm(instance=zgloszenie)

        if is_staff:
            form_status = ZmienStatusForm(instance=zgloszenie)

        # Sprawdzamy czy zgłoszenie jest zamknięte (do blokowania komentarzy)
        czy_zamkniete = zgloszenie.status in ['ROZWIAZANE', 'ZAMKNIETE']

        return render(request, "zgloszenie_detail.html", {
            "zgloszenie": zgloszenie,
            "komentarze": komentarze,
            "form": form_komentarz,
            "form_przypisania": form_przypisania,
            "form_status": form_status,  # NOWE: Formularz zmiany statusu
            "is_manager": is_manager,
            "is_staff": is_staff,  # NOWE: Flaga dla IT
            "czy_zamkniete": czy_zamkniete,  # NOWE: Flaga blokady
        })

    def post(self, request, pk):
        zgloszenie = get_object_or_404(Zgloszenie, pk=pk)

        # === ZABEZPIECZENIE ===
        # Jeśli zgłoszenie jest rozwiązane, nie pozwalamy dodać komentarza
        if zgloszenie.status in ['ROZWIAZANE', 'ZAMKNIETE']:
            return redirect("helpdesk:zgloszenie_detail", pk=zgloszenie.pk)

        form = KomentarzForm(request.POST)
        if form.is_valid():
            komentarz = form.save(commit=False)
            komentarz.zgloszenie = zgloszenie
            komentarz.autor = request.user
            komentarz.save()
            return redirect("helpdesk:zgloszenie_detail", pk=zgloszenie.pk)

        # ... (kod obsługi błędów taki sam jak wcześniej,
        # tylko pamiętaj o dodaniu zmiennych form_status, is_staff itp.) ...
        # Dla uproszczenia, przy błędzie formularza zwykle robi się redirect lub pełny render
        return redirect("helpdesk:zgloszenie_detail", pk=zgloszenie.pk)

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


class ZgloszenieStatusView(LoginRequiredMixin, View):
    def post(self, request, pk):
        zgloszenie = get_object_or_404(Zgloszenie, pk=pk)

        # Sprawdzamy czy user to IT (Manager lub Pracownik)
        is_staff = request.user.groups.filter(name__in=['IT Manager', 'Pracownik IT']).exists()

        if not is_staff:
            return redirect("helpdesk:zgloszenie_detail", pk=pk)

        form = ZmienStatusForm(request.POST, instance=zgloszenie)
        if form.is_valid():
            form.save()

        return redirect("helpdesk:zgloszenie_detail", pk=pk)
