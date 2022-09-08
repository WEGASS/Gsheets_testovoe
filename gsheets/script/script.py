import os
import time
from datetime import datetime
import pandas as pd
import gspread
import requests
import schedule
import xmltodict
from gsheets.models import Contract

gc = gspread.service_account(filename='gsheets/script/service_account.json')
sh = gc.open_by_url(os.getenv('GSHEETS_URL'))
worksheet = sh.worksheet(os.getenv('GSHEETS_LIST'))


def get_exchange_rate():
    """
    Returns today exchange rate of pair Rub-USD
    """
    response = requests.get('https://www.cbr.ru/scripts/XML_daily.asp')
    data = xmltodict.parse(response.text)['ValCurs']['Valute']
    for valute in data:
        if valute['@ID'] == 'R01235':
            return float(valute['Value'].replace(',', '.'))


def cached(func):
    """
    Wrapper for saving last list of orders with overdue (to avoid resending)
    """
    cache = {'order_list': []}

    def wrapper(orders_list):
        if set(list(orders_list)) != set(list(cache['order_list'])):
            cache['order_list'] = orders_list
            func(orders_list)
        else:
            return
    return wrapper


@cached
def telegram_bot_sendtext(orders_list):
    """
    Send all orders with overdue in Telegram chat
    """
    bot_token = os.getenv('BOT_TOKEN')
    url = 'https://api.telegram.org/bot' + bot_token + '/sendMessage'
    bot_chat_id = os.getenv('CHAT_ID')
    bot_message = 'Сроки поставок вышли у следующих заказов: \n' + '\n'.join([str(n) for n in orders_list])
    params = {'chat_id': bot_chat_id,
              'parse_mode': 'Markdown',
              'text': bot_message
              }
    response = requests.get(url, params=params)
    return response.json()['ok']


def get_overdue():
    """
    Get all orders with overdue
    """
    overdue_list = Contract.objects.filter(delivery_date__lt=datetime.now().date()).values_list('number', flat=True)
    return overdue_list


def get_table(sheet):
    df = pd.DataFrame(sheet.get_all_records())
    return df


def refresh_table(df):
    exchange_rate = get_exchange_rate()
    # Get or create record in db
    for i, df_product in df.iterrows():
        price_in_rub = df.loc[i, 'стоимость,$'] * exchange_rate
        contract, created = Contract.objects.get_or_create(
            id=df.loc[i, '№'],
            defaults={
                'id': df.loc[i, '№'],
                'number': df.loc[i, 'заказ №'],
                'price': df.loc[i, 'стоимость,$'],
                'delivery_date': datetime.strptime(df.loc[i, 'срок поставки'], '%d.%m.%Y').strftime('%Y-%m-%d'),
                'price_in_rub': price_in_rub,
            }
        )
        # Change record in db if something changed in GoogleSheets
        if contract.number != df.loc[i, 'заказ №'] or contract.price != df.loc[
            i, 'стоимость,$'] or contract.delivery_date != df.loc[
            i, 'срок поставки'] or contract.price_in_rub != price_in_rub:
            contract.number = df.loc[i, 'заказ №']
            contract.price = df.loc[i, 'стоимость,$']
            contract.delivery_date = datetime.strptime(df.loc[i, 'срок поставки'], '%d.%m.%Y').strftime('%Y-%m-%d')
            contract.price_in_rub = price_in_rub
            contract.save()
    # Delete old records
    numbers = list(df['№'].values)
    Contract.objects.exclude(id__in=numbers).delete()
    print(f"End syncing with GoogleSheets in {datetime.now()}")


def do_all():
    table = get_table(worksheet)
    refresh_table(table)
    try:
        telegram_bot_sendtext(get_overdue())
    except Exception as error:
        print('Error with TG credentials')
        print(error)


def main():
    do_all()
    schedule.every(int(os.getenv('SCHEDULE_TIME'))).minutes.do(do_all)  # Run every 'n' minutes
    while True:
        schedule.run_pending()
        time.sleep(1)
