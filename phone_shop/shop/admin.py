from django.contrib import admin
from .models import Product, Booking

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'category', 
        'preis_kauf', 
        'leihbar', 
        'verkaufbar', 
        'ist_service',
        'leasing_available' # Добавил лизинг в список для удобства
    )
    list_filter = ('category', 'leihbar', 'verkaufbar', 'ist_service', 'leasing_available')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('product', 'action_type', 'start_date', 'end_date', 'user', 'created_at')
    list_filter = ('action_type', 'created_at', 'product')
    search_fields = ('product__name', 'user__username')
    readonly_fields = ('created_at',)