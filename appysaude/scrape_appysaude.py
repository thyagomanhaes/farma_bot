import os
import sys
import logging
import time
from datetime import datetime

import concurrent.futures
import requests
import pandas as pd

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler(sys.stdout)  # Where logged messages will output, in this case direct to console
formatter = logging.Formatter('[%(asctime)s : %(levelname)s] => %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)  # better to have too much log than not enough

URL_APPYSAUDE = f"https://www.appysaude.co.ao/v1.0/products/productList?filter=&search=&skip=50&sort=3"


def export_products_to_excel(df):
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


def scrape_appysaude_page(url, access_token):
    page = make_request(url, access_token)

    el = page.json()
    products = el['Fields']

    products_list = []
    print("URL: ", url)
    for item in products:
        try:
            product = {}
            print(
                f"{item['Name']} | {item['ShortDescriptionEn']} | {item['HealthEstName']} | {item['Price']} | {item['Province']} | {item['ProductId']}")

            product['id'] = item['ProductId']
            name = item['Name']
            name = name.replace('\n', '')
            name = name.replace('\r', '')
            product['nome'] = name
            description = item.get('ShortDescriptionEn')

            if description is not None:
                description = description.replace('\n', '')
                description = description.replace('\r', '')
                product['nome_completo'] = name + " " + description
            else:
                product['nome_completo'] = name + " "

            product['descricao'] = description

            product['fornecedor'] = item.get('HealthEstName')
            product['preco'] = item.get('Price')
            product['provincia'] = item.get('Province')
            product['url'] = url
            product['date_scraping'] = datetime.now()

            products_list.append(product)
        except TypeError as typeErrorExp:
            print(f"Erro de tipo: {typeErrorExp}")

    return products_list


def scrap_products_urls(urls_produtos, access_token):
    total = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        tasks = [executor.submit(scrape_appysaude_page, url, access_token) for url in urls_produtos]
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

    page = requests.get(URL_APPYSAUDE, headers=headers)

    if page.status_code == 401:
        print("Token Inválido! Por favor, tente novamente. Obs: Seu token expira 1 hora após ter feito o login.")
    elif page.status_code == 200:

        print("Token validado com sucesso!!!")
        print("Iniciando scraping dos produtos...")
        # count_total_products = page.json()['TotalCount']
        count_total_products = 50

        print(f"Total de produtos disponíveis: {count_total_products}")

        skips = [n for n in range(count_total_products) if n % 50 == 0]
        urls = [f"https://www.appysaude.co.ao/v1.0/products/productList?filter=&search=&skip={skip}&sort=3" for skip
                in skips]

        print(f"{len(urls)} links disponíveis para scraping")

        start = time.time()

        _products = scrap_products_urls(urls, access_token)

        products_total_list = []

        l_total_products = [lp._result for lp in _products]

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
        total_time_to_scrape = round(end - start, 2)

        return products_total_list, total_time_to_scrape


def check_if_files_folder_exists():
    path_appysaude_files = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')

    if os.path.exists(path_appysaude_files):
        logger.info(f"Folder exists: {path_appysaude_files}")
    else:
        os.makedirs(path_appysaude_files)
        logger.info(f"Created folder: {path_appysaude_files}")


if __name__ == '__main__':
    try:
        check_if_files_folder_exists()
        logger.info("Starting scraper AppySaude...")
        all_products, total_time = scrape_appysaude()
        if len(all_products) > 0:
            msg = f"\nScraper AppySaude executed with no errors!\n"
            msg += f"Total of products collected: {len(all_products)}\n"
            msg += f"Total Time: {total_time} secs"
            logger.info(msg)
    except Exception as e:
        logger.error(f"Erro ao executar script Scraper AppySaude: {e}")
