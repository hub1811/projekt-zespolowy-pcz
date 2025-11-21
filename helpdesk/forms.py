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


# helpdesk/forms.py
from django import forms
from django.contrib.auth.models import User, Group
from .models import Zgloszenie, Komentarz

# ... (ZgloszenieForm i KomentarzForm bez zmian) ...

class PrzypiszZgloszenieForm(forms.ModelForm):
    class Meta:
        model = Zgloszenie
        fields = ['przypisane_do']
        labels = {
            'przypisane_do': 'Wybierz pracownika IT'
        }
        widgets = {
            'przypisane_do': forms.Select(attrs={'class': 'form-select'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            grupa_it = Group.objects.get(name='Pracownik IT')
            self.fields['przypisane_do'].queryset = User.objects.filter(groups=grupa_it)
        except Group.DoesNotExist:
            self.fields['przypisane_do'].queryset = User.objects.none()