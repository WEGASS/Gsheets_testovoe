from datetime import datetime
import pandas as pd
import gspread
import requests
import xmltodict
from gsheets.models import Contract


gc = gspread.service_account(filename='gsheets/script/service_account.json')
sh = gc.open_by_url(
    'https://docs.google.com/spreadsheets/d/1p3YOopCH996XAShh8Op7M6lb184rE7D5xjHJiYzmLNs/edit?usp=sharing')
worksheet = sh.worksheet("Лист1")


def get_exchange_rate():
    '''
    Returns today exchange rate of pair Rub-USD
    '''
    response = requests.get('https://www.cbr.ru/scripts/XML_daily.asp')
    data = xmltodict.parse(response.text)['ValCurs']['Valute']
    for valute in data:
        if valute['@ID'] == 'R01235':
            return float(valute['Value'].replace(',', '.'))


def get_table(worksheet):
    df = pd.DataFrame(worksheet.get_all_records())
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


def main():
    table = get_table(worksheet)
    refresh_table(table)
