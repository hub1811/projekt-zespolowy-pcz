from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Kategoria(models.Model):
    nazwa = models.CharField(max_length=100)

    def __str__(self):
        return self.nazwa

    class Meta:
        verbose_name = 'Kategoria'
        verbose_name_plural = 'Kategorie'


class Zgloszenie(models.Model):
        STATUS_CHOICES = [('NOWE', 'Nowe'),
                          ('W_TOKU', 'W toku'),
                          ('ROZWIAZANE', 'Rozwiązane'),
                          ]

        PRIORYTET_CHOICES = [('NISKI', 'Niski'),
                             ('SREDNI', 'Średni'),
                             ('WYSOKI', 'Wysoki'),
                             ]
        tytul = models.CharField(max_length=255)
        opis = models.TextField()

        status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOWE')
        priorytet = models.CharField(max_length=20, choices=PRIORYTET_CHOICES, default='SREDNI')
        kategoria = models.ForeignKey(Kategoria, on_delete=models.SET_NULL, null=True, blank=True)

        zgloszone_przez = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moje_zgloszenia')
        przypisane_do = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='przypisane_zgloszenia')

        data_utworzenia = models.DateTimeField(auto_now_add=True)
        data_aktualizacji = models.DateTimeField(auto_now=True)

        def __str__(self):
            return f"#{self.id} - {self.tytul}"

        class Meta:
            ordering = ['-data_utworzenia']
            verbose_name = 'Zgloszenie'
            verbose_name_plural = 'Zgloszenia'


class Komentarz(models.Model):
    zgloszenie = models.ForeignKey(Zgloszenie, on_delete=models.CASCADE, related_name='komentarze')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    tresc = models.TextField()
    data_dodania = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Komentarz od {self.autor.username} do {self.zgloszenie.tytul}"

    class Meta:
        ordering = ['data_dodania']
        verbose_name = 'Komentarz'
        verbose_name_plural = 'Komentarze'