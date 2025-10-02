from celery import shared_task
from django.core.mail import send_mail
from .models import Order

@shared_task
def order_created(order_id):
    # Задание на отправку электронной почты с успешным статусом заказа
    order = Order.objects.get(id=order_id)
    subject = f"Order number: #{order_id}"
    message = f"Dear {order.first_name},\n\n" \
    f"You have succesfully placed an order." \
    f"Your Order ID: {order.id}."
    mail_sent = send_mail(subject, message, 'admin@webshop.com', [order.email])
    return mail_sent