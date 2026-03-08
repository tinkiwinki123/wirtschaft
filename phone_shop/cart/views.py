from django.shortcuts import render, redirect, get_object_or_404
from django.utils.dateparse import parse_datetime
from django.contrib import messages
from shop.models import Product, Booking  # Добавил импорт Booking
from decimal import Decimal, ROUND_UP

def _get_cart(session):
    if 'cart' not in session:
        session['cart'] = {}
    return session['cart']

def calculate_price(product, action_type, start=None, end=None):
    """Возвращает (цена, название_тарифа) с округлением времени вверх"""
    if action_type == 'buy':
        return product.preis_kauf or Decimal('0.00'), "Kauf"
    if action_type == 'repair':
        return product.preis_service or Decimal('0.00'), "Reparatur"
    if action_type == 'leasing':
        return product.preis_leasing or Decimal('0.00'), "Leasing (monatlich)"
    
    if not start or not end:
        raise ValueError("Zeitraum fehlt.")

    duration = end - start
    total_hours = Decimal(duration.total_seconds()) / 3600
    
    if total_hours <= 0:
        raise ValueError("Enddatum muss nach Startdatum liegen.")

    # 1. НЕДЕЛЬНЫЙ ТАРИФ (от 168 часов)
    if total_hours >= 168 and product.preis_woche:
        weeks = Decimal(total_hours / 168).quantize(Decimal('1'), rounding=ROUND_UP)
        return (weeks * product.preis_woche), "Wochenmiete"

    # 2. ДНЕВНОЙ ТАРИФ (от 24 часов)
    if total_hours >= 24 and product.preis_tag:
        days = Decimal(total_hours / 24).quantize(Decimal('1'), rounding=ROUND_UP)
        return (days * product.preis_tag), "Tagesmiete"

    # 3. ПОЧАСОВОЙ ТАРИФ (до 24 часов)
    if product.preis_stunde:
        billable_hours = Decimal(total_hours).quantize(Decimal('1'), rounding=ROUND_UP)
        return (billable_hours * product.preis_stunde), "Stundenmiete"
    
    return product.preis_tag or Decimal('0.00'), "Tagesmiete"

def cart_add(request):
    product = get_object_or_404(Product, id=request.POST.get('product_id'))
    action_type = request.POST.get('action_type')
    
    start_str = request.POST.get('start')
    end_str = request.POST.get('end')
    start = parse_datetime(start_str) if start_str else None
    end = parse_datetime(end_str) if end_str else None

    try:
        # Считаем цену (просто для отображения в корзине)
        price, rate_name = calculate_price(product, action_type, start, end)
        
        # !!! УДАЛЕНО: Booking.objects.create(...) !!!
        # Мы больше не пишем в базу на этом этапе.
        
    except ValueError as e:
        messages.error(request, str(e))
        return redirect('shop')

    cart = _get_cart(request.session)
    time_suffix = f"_{start_str}" if start_str else ""
    key = f"{product.id}_{action_type}{time_suffix}"
    
    cart[key] = {
        'product_id': product.id,
        'name': product.name,
        'price': str(price),
        'rate_name': rate_name,
        'action_type': action_type,
        'start': start_str,
        'end': end_str,
    }
    request.session.modified = True
    messages.success(request, f"{product.name} wurde hinzugefügt!")
    return redirect('cart:detail')

def cart_detail(request):
    cart = _get_cart(request.session)
    total_price = sum(Decimal(item['price']) for item in cart.values())
    
    return render(request, 'cart/cart.html', {
        'cart': cart, 
        'total_price': total_price
    })

def cart_remove(request):
    key = request.POST.get('key')
    cart = _get_cart(request.session)
    if key in cart:
        del cart[key]
        request.session.modified = True
    return redirect('cart:detail')

def checkout(request):
    cart = _get_cart(request.session)
    
    if not cart:
        messages.error(request, "Ваша корзина пуста.")
        return redirect('shop')

    # --- ТЕПЕРЬ ЗАПИСЫВАЕМ В БАЗУ ЗДЕСЬ (ПРИ ОФОРМЛЕНИИ) ---
    for key, item in cart.items():
        product = get_object_or_404(Product, id=item['product_id'])
        
        # Создаем запись в Booking только для тех, кто реально нажал "Забронировать"
        Booking.objects.create(
            product=product,
            user=request.user if request.user.is_authenticated else None,
            start_date=parse_datetime(item['start']) if item['start'] else None,
            end_date=parse_datetime(item['end']) if item['end'] else None,
            action_type=item['action_type']
        )

    # Очищаем корзину после того, как всё сохранили
    request.session['cart'] = {}
    request.session.modified = True
    
    return render(request, 'cart/checkout.html')