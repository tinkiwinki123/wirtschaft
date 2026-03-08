from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Mountainbikes', 'Mountainbikes'),
        ('TrekkingFahrräder', 'Trekking Fahrräder'),
        ('Kinderfahrräder', 'Kinderfahrräder'),
        ('Bestandteile', 'Bestandteile'),
        ('Ausrüstung', 'Ausrüstung'),
        ('Reparatur', 'Reparatur'),
    ]

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField(blank=True, null=True, verbose_name="Beschreibung")
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name="Bild")
    slug = models.SlugField(unique=True, blank=True)

    # Logik-Flags
    leihbar = models.BooleanField(default=False, verbose_name="Verleihbar")
    verkaufbar = models.BooleanField(default=False, verbose_name="Verkaufbar")
    ist_service = models.BooleanField(default=False, verbose_name="Ist Reparatur/Service")

    # Preise
    preis_kauf = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Kaufpreis")
    preis_stunde = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Preis pro Stunde")
    preis_tag = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Preis pro Tag")
    preis_woche = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Preis pro Woche")
    preis_service = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Servicepreis")
    leasing_available = models.BooleanField(default=False, verbose_name="Verfügbar für Leasing")
    preis_leasing = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Leasing pro Monat")
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# Новая таблица бронирований
class Booking(models.Model):
    ACTION_CHOICES = [
        ('rent', 'Mieten'),
        ('buy', 'Kaufen'),
        ('repair', 'Reparatur'),
        ('leasing', 'Leasing'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bookings', verbose_name="Produkt")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Kunde")
    start_date = models.DateTimeField(verbose_name="Von", null=True, blank=True)
    end_date = models.DateTimeField(verbose_name="Bis", null=True, blank=True)
    action_type = models.CharField(max_length=10, choices=ACTION_CHOICES, verbose_name="Typ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Erstellt am")

    class Meta:
        verbose_name = "Buchung"
        verbose_name_plural = "Buchungen"

    def __str__(self):
        return f"{self.product.name} - {self.action_type}"