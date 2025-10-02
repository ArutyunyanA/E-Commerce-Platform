import redis
from django.conf import settings
from .models import Product

# Соединение с Redis

r = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)

class Recommendation:
    def get_product_key(self, id):
        return f'product:{id}:purchase_with'

    def products_bought(self, products):
        product_ids = [p.id for p in products]
        for product_id in product_ids:
            for with_id in product_ids:
                # получить другие товары, купленные вместе с каждым товаром
                if product_id != with_id:
                    # Увеличиваем балл товара купленные вместе
                    r.zincrby(self.get_product_key(product_id), 1, with_id)
    
    def suggest_products_for(self, products, max_results=6):
        product_ids = [p.id for p in products]
        if len(products) == 1:
            suggestions = r.zrange(self.get_product_key(product_ids[0]), 0, -1, desc=True)[:max_results]
        else:
            # генерируем временный ключ
            flat_ids = ''.join([str(id) for id in product_ids])
            temp_key = f'temp_{flat_ids}'
            keys = [self.get_product_key(id) for id in product_ids]
            r.zunionstore(temp_key, keys)
            r.zrem(temp_key, *product_ids)
            suggestions = r.zrange(temp_key, 0, -1, desc=True)[:max_results]
            r.delete(temp_key)
        suggested_products_ids = [int(id) for id in suggestions]
        suggested_products = list(Product.objects.filter(id__in=suggested_products_ids))
        suggested_products.sort(key=lambda x: suggested_products_ids.index(x.id))
        return suggested_products

    def clear_purchase(self):
        for id in Product.objects.values_list('id', flat=True):
            r.delete(self.get_product_key(id))