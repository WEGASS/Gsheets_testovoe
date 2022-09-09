from django.db import models


class Contract(models.Model):
    number = models.IntegerField(verbose_name='заказ №')
    price = models.FloatField(verbose_name='стоимость,$')
    delivery_date = models.DateField(verbose_name='срок поставки')
    price_in_rub = models.FloatField(verbose_name='стоимость в руб.')

    # Function for comparing two objects
    def __eq__(self, other):
        values = [(k, v) for k, v in self.__dict__.items() if k != '_state']
        other_values = [(k, v) for k, v in other.__dict__.items() if k != '_state']
        return values == other_values