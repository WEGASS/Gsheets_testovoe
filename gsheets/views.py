import json
from django.shortcuts import render
from django.db.models import Sum
from .models import Contract


def index(request):
    contracts = Contract.objects.order_by('pk')
    dates = Contract.objects.order_by('delivery_date').values('delivery_date').annotate(Sum('price'))
    price_sum = Contract.objects.aggregate(Sum('price')).get('price__sum')
    context = {
        'contracts': contracts,
        'dates': dates,
        'price_sum': price_sum,
    }
    return render(request, 'index.html', context=context)
