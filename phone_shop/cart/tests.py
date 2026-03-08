from django.test import TestCase


class CartSessionTests(TestCase):
    def test_cart_pages_load_empty(self):
        resp = self.client.get('/cart/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Ihr Warenkorb ist leer')

    def test_add_to_session_and_display(self):
        # simulate adding an item to session
        session = self.client.session
        session['cart'] = {
            'p1': {'name': 'Test Product', 'price': '12.5', 'qty': 2, 'image': 'images/iphone17.png'}
        }
        session.save()
        resp = self.client.get('/cart/')
        self.assertContains(resp, 'Test Product')
        self.assertContains(resp, '$25.0')
