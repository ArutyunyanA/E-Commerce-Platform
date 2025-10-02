from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from webshop.models import Product
from coupons.models import Coupon

class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='orders',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    stripe_id = models.CharField(max_length=250, blank=True)
    coupon = models.ForeignKey(Coupon, related_name='orders', null=True, blank=True, on_delete=models.SET_NULL)
    discount = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])


    class Meta:
        ordering = ['-created']
        indexes = [models.Index(fields=['-created'])]

    def __str__(self):
        return f"Order {self.id}"

    def get_stripe_url(self):
        if not self.stripe_id:
            # никаких ассоциированных платежей
            return ''
        if '_test_' in settings.STRIPE_SECRET_KEY:
            # путь stripe для тестовых платежей
            path = '/test/'
        else:
            # путь stripe для настоящих платежей
            path = '/'
        return f"https://dashboard.stripe.com{path}payments/{self.stripe_id}"

    def get_total_cost_before_discount(self) -> Decimal:
        return sum(item.get_cost() for item in self.items.all())

    def get_discount(self) -> Decimal:
        return self.get_total_cost_before_discount() * (Decimal(self.discount) / Decimal(100))

    def get_total_cost(self):
        return sum(item.get_discounted_cost(self.discount) for item in self.items.all())
    
    def get_vat_amount(self) -> Decimal: 
        return sum(item.get_vat_amount(self.discount) for item in self.items.all())
    
    def get_total_cost_incl_vat(self):
        return sum(item.get_total_cost_incl_vat(self.discount) for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    vat_rate = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("19.00"), help_text="VAT %")
    

    

    def __str__(self):
        return str(self.id)

    def get_cost(self) -> Decimal:
        return self.price * self.quantity

    def get_discounted_cost(self, discount_percent: int = 0) -> Decimal:
        cost = self.get_cost()
        if discount_percent:
            cost = cost * (Decimal(100) - Decimal(discount_percent)) / Decimal(100)
        return cost

    def get_vat_amount(self, discount_percent: int = 0) -> Decimal:
        return self.get_discounted_cost(discount_percent) * (self.vat_rate / Decimal(100))

    def get_total_cost_incl_vat(self, discount_percent: int = 0) -> Decimal:
        return self.get_discounted_cost(discount_percent) + self.get_vat_amount(discount_percent)

    def get_cost_with_discount_and_vat(self):
        cost = self.get_cost()
        discount = getattr(self.order, "discount", 0)  # % скидки
        if discount:
            cost = cost * (Decimal(100) - Decimal(discount)) / Decimal(100)
        return cost * (1 + self.vat_rate / Decimal(100))