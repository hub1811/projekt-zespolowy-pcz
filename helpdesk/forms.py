from django import forms
from .models import Zgloszenie, Komentarz


class ZgloszenieForm(forms.ModelForm):
    class Meta:
        model = Zgloszenie
        # Jeśli u Ciebie pola nazywają się trochę inaczej – zmień tylko listę poniżej.
        fields = ['tytul', 'opis', 'kategoria', 'priorytet']
        # awaryjnie możesz dać:
        # fields = '__all__'


class KomentarzForm(forms.ModelForm):
    class Meta:
        model = Komentarz
        fields = ['tresc']
