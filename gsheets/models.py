from django.db import models


class Contract(models.Model):
    number = models.IntegerField(verbose_name='заказ №')
    price = models.FloatField(verbose_name='стоимость,$')
    delivery_date = models.DateField(verbose_name='срок поставки')
    price_in_rub = models.FloatField(verbose_name='стоимость в руб.')
