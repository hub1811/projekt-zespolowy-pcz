from django.contrib import admin
from .models import Kategoria,Zgloszenie,Komentarz

# Register your models here.

@admin.register(Kategoria)
class KategoriaAdmin(admin.ModelAdmin):
    list_display = ('nazwa',)
    search_fields = ('nazwa',)


@admin.register(Zgloszenie)
class ZgloszenieAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'tytul',
        'status',
        'priorytet',
        'kategoria',
        'zgloszone_przez',
        'przypisane_do',
        'data_aktualizacji'
    )

    list_filter = (
        'status',
        'priorytet',
        'kategoria',
        'data_utworzenia',
        'data_aktualizacji'
    )

    search_fields = (
        'id',
        'tytul',
        'opis',
        'zgloszone_przez__username',
        'przypisane_do__username'
    )

    list_editable = ('status', 'priorytet', 'przypisane_do')

    date_hierarchy = 'data_utworzenia'

@admin.register(Komentarz)
class KomentarzAdmin(admin.ModelAdmin):
    list_display = (
        'zgloszenie',
        'autor',
        'data_dodania',
        'skrocona_tresc'
    )

    search_fields = (
        'tresc',
        'autor__username',
        'zgloszenie__tytul'
    )

    list_filter = ('data_dodania', 'autor')

    def skrocona_tresc(self, obj):
        """
        Metoda pomocnicza, aby wyświetlić tylko fragment
        komentarza na liście (pierwsze 50 znaków).
        """
        if len(obj.tresc) > 50:
            return obj.tresc[:50] + '...'
        return obj.tresc

    skrocona_tresc.short_description = 'Treść (skrót)'