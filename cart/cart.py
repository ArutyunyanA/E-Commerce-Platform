from decimal import Decimal
from django.conf import settings
from webshop.models import Product
from coupons.models import Coupon


"""
Инициализация корзины.
"""
class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # сохранить пустую корзину в сеансе
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        # cохраняем текущий купон
        self.coupon_id = self.session.get('coupon_id')

    @property
    def coupon(self):
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id)
            except Coupon.DoesNotExist:
                pass
        return None

    def __iter__(self):
        # Прокрутить товарные позиции в цикле
        # и получить товары из базы данных.
        product_ids = self.cart.keys()
        # получаем объекты product и добавляем их в корзину
        products = Product.objects.filter(id__in=product_ids)
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        discount_ratio = (self.get_discount() / self.get_total_price()) if self.get_total_price() > 0 else Decimal("0.00")
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['quantity'] = int(item['quantity'])
            product = item['product']
            item['vat_rate'] = product.vat_rate
            discounted_price = item['price'] * item['quantity'] * (1 - discount_ratio)
            item['vat_amount'] = discounted_price * (item['vat_rate'] / Decimal(100))
            item['total_price_excl_vat'] = discounted_price
            item['total_price_incl_vat'] = discounted_price + item['vat_amount']
            yield item

    def __len__(self):
        # Подсчитаем все товарные позиции в корзине
        return sum(item['quantity'] for item in self.cart.values())


    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def get_discount(self):
        if self.coupon:
            return (self.coupon.discount / Decimal(100) * self.get_total_price())
        return Decimal(0)

    def get_total_price_after_discount(self):
        return self.get_total_price() - self.get_discount()

    def get_vat_amount(self):
        total_vat = Decimal("0.00")
        total_price_before_discount = self.get_total_price()
        discount_ratio = (self.get_discount() / total_price_before_discount) if total_price_before_discount > 0 else Decimal("0.00")

        for item in self.__iter__():
            # Цена товара после пропорциональной скидки
            discounted_price = item['price'] * item['quantity'] * (1 - discount_ratio)
            item_vat = discounted_price * (item['vat_rate'] / Decimal("100"))
            total_vat += item_vat

        return total_vat


    def get_total_incl_vat(self):
        return self.get_total_price_after_discount() + self.get_vat_amount()

    def add(self, product, quantity=1, override_quantity=False):
        # Добавить товар в корзину либо обновить его количество.
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product):
        # Удалить товар из корзины
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        # Удаляем корзину из сеанса
        del self.session[settings.CART_SESSION_ID]
        self.save()