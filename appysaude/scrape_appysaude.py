import os
from datetime import datetime
import concurrent.futures
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

from utils import send_message_to_telegram, CANAL_NOTIFICACOES_BETFAIR
import psycopg2

def exportar_produtos_para_excel(df):
    filename_excel = f"appysaude-{datetime.now().date()}.xlsx"
    df.to_excel(filename_excel, index=False)
    return filename_excel


def make_request(url, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
    }
    page = requests.get(url, headers=headers)

    return page


def scrap_appysaude(url, access_token):
    page = make_request(url, access_token)

    el = page.json()
    products = el['Fields']

    products_list = []
    print("URL: ", url)
    for item in products:
        try:
            produto = {}
            print(
                f"{item['Name']} | {item['ShortDescriptionEn']} | {item['HealthEstName']} | {item['Price']} | {item['Province']} | {item['ProductId']}")

            produto['id'] = item['ProductId']
            name = item['Name']
            name = name.replace('\n', '')
            name = name.replace('\r', '')
            produto['nome'] = name
            description = item.get('ShortDescriptionEn')

            if description is not None:
                description = description.replace('\n', '')
                description = description.replace('\r', '')
                produto['nome_completo'] = name + " " + description
            else:
                produto['nome_completo'] = name + " "

            produto['descricao'] = description

            produto['fornecedor'] = item.get('HealthEstName')
            produto['preco'] = item.get('Price')
            produto['provincia'] = item.get('Province')
            produto['url'] = url
            produto['date_scraping'] = datetime.now()

            products_list.append(produto)
        except TypeError as e:
            print(f"Erro de tipo {e}")

    return products_list


def scrap_urls_produtos(urls_produtos, access_token):
    total = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        tasks = [executor.submit(scrap_appysaude, url, access_token) for url in urls_produtos]
        results = []
        for result in concurrent.futures.as_completed(tasks):
            results.append(result)

        total += results

    return total


def scrape_appysaude():
    access_token = None
    print("\nAguarde enquanto o token é validado...")
    headers = {
        "Authorization": f"Bearer {access_token}",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
    }

    url1 = f"https://www.appysaude.co.ao/v1.0/products/productList?filter=&search=&skip=50&sort=3"
    page = requests.get(url1, headers=headers)
    if page.status_code == 401:
        print("Token Inválido! Por favor, tente novamente. Obs: Seu token expira 1 hora após ter feito o login.")
    elif page.status_code == 200:
        print("Token validado com sucesso!!!")
        print("Iniciando scraping dos produtos...")
        count_total_products = page.json()['TotalCount']
        # count_total_products = 500

        print(f"Total de produtos disponíveis: {count_total_products}")

        skips = [n for n in range(count_total_products) if n % 50 == 0]
        urls = [f"https://www.appysaude.co.ao/v1.0/products/productList?filter=&search=&skip={skip}&sort=3" for skip
                in skips]

        print(f"{len(urls)} links disponíveis para scraping")

        start = time.time()

        _produtos = scrap_urls_produtos(urls, access_token)

        products_total_list = []

        l_total_products = [lp._result for lp in _produtos]

        for l_products in l_total_products:
            if l_products is not None and len(l_products) > 0:
                for produto in l_products:
                    products_total_list.append(produto)

        df_appysaude = pd.DataFrame.from_records(products_total_list)
        path_appysaude_files = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')
        appysaude_filename = f'appysaude-{datetime.now().date()}'
        df_appysaude.to_csv(f'{path_appysaude_files}/{appysaude_filename}.csv', encoding='utf-8-sig')
        # df_appysaude.to_excel(f'{path_appysaude_files}/{appysaude_filename}.xlsx')

        end = time.time()
        print(f"Total de produtos disponíveis: {count_total_products}")
        total_time = round(end - start, 2)
        # send_message_to_telegram(f"\nTempo para coletar {len(lista_produtos)} dados: {total_time} segundos",
        #                          CANAL_NOTIFICACOES_BETFAIR)
        return products_total_list, total_time


class SavingToPostgresPipeline(object):
    def __init__(self):
        self.cur = None
        self.connection = None
        self.create_connection()

    def create_connection(self):
        self.connection = psycopg2.connect(
            host='',
            user='',
            password='',
            dbname=''
        )
        self.cur = self.connection.cursor()

    def process_item(self, item):
        self.cur.execute("""insert into table (x,x) values (%s,%s)""", (
            item["text"],
            item["x"]
        ))

        self.connection.commit()
        return item

    def close_connection(self):
        self.cur.close()
        self.connection.close()


if __name__ == '__main__':
    # try:
    send_message_to_telegram("Starting scraper AppySaude...", CANAL_NOTIFICACOES_BETFAIR)
    all_products, total_time = scrape_appysaude()
    if len(all_products) > 0:
        msg = f"Scraper AppySaude executed with no errors!\n"
        msg += f"Total of products collected: {len(all_products)}\n"
        msg += f"Total Time: {total_time} secs"
        send_message_to_telegram(msg, CANAL_NOTIFICACOES_BETFAIR)
    # except Exception as e:
    # send_message_to_telegram(f"Erro ao executar script Scraper AppySaude: {e}", CANAL_NOTIFICACOES_BETFAIR)
