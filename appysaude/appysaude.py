import os
from datetime import datetime
import concurrent.futures
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd

from utils import send_message_to_telegram, CANAL_NOTIFICACOES_BETFAIR


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
    lista = el['Fields']

    l_produtos = []

    for count, x in enumerate(lista):
        try:
            produto = {}
            print(
                f"{x['Name']} | {x['ShortDescriptionEn']} | {x['HealthEstName']} | {x['Price']} | {x['Province']} | {x['ProductId']}")

            produto['id'] = x['ProductId']
            name = x['Name']
            name = name.replace('\n', '')
            name = name.replace('\r', '')
            produto['nome'] = name
            descricao = x.get('ShortDescriptionEn')
            descricao = descricao.replace('\n', '')
            descricao = descricao.replace('\r', '')
            produto['descricao'] = descricao
            produto['nome_completo'] = name + " " + descricao
            produto['fornecedor'] = x.get('HealthEstName')
            produto['preco'] = x['Price']
            produto['provincia'] = x['Province']
            produto['url'] = url
            produto['date_scraping'] = datetime.now()

            l_produtos.append(produto)
        except TypeError as e:
            print(f"Erro de tipo {e}")

    return l_produtos


def scrap_urls_produtos(urls_produtos, access_token):
    total = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        tasks = [executor.submit(scrap_appysaude, url, access_token) for url in urls_produtos]
        results = []
        for result in concurrent.futures.as_completed(tasks):
            results.append(result)

        total += results

    return total


def scrap_pagina_produtos(page, access_token):
    count_total_products = page.json()['TotalCount']

    print(f"Total de produtos disponíveis: {count_total_products}")

    skips = [n for n in range(count_total_products) if n % 50 == 0]
    urls = [f"https://www.appysaude.co.ao/v1.0/products/productList?filter=&search=&skip={skip}&sort=3" for skip
            in skips]

    print(f"{len(urls)} links disponíveis para scraping")

    start = time.time()

    _produtos = scrap_urls_produtos(urls, access_token)

    lista_produtos = []

    l_produtos = [lp._result for lp in _produtos]

    for l_produto in l_produtos:
        for produto in l_produto:
            lista_produtos.append(produto)

    return lista_produtos


def iniciar_scraping():
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
        count_total_products = 500

        print(f"Total de produtos disponíveis: {count_total_products}")

        skips = [n for n in range(count_total_products) if n % 50 == 0]
        urls = [f"https://www.appysaude.co.ao/v1.0/products/productList?filter=&search=&skip={skip}&sort=3" for skip
                in skips]

        print(f"{len(urls)} links disponíveis para scraping")

        start = time.time()

        _produtos = scrap_urls_produtos(urls, access_token)

        lista_produtos = []

        l_produtos = [lp._result for lp in _produtos]

        for l_produto in l_produtos:
            for produto in l_produto:
                lista_produtos.append(produto)

        df_appysaude = pd.DataFrame.from_records(lista_produtos)
        path_appysaude_files = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')
        appysaude_filename = f'appysaude-{datetime.now().date()}'
        # df_appysaude.to_csv(f'{path_appysaude_files}/{appysaude_filename}.csv', encoding='utf-8-sig')
        df_appysaude.to_excel(f'{path_appysaude_files}/{appysaude_filename}.xlsx')

        end = time.time()

        total_time = round(end - start, 2)
        print(f"\nTempo para coletar {len(lista_produtos)} dados: {total_time} segundos")


if __name__ == '__main__':
    try:
        iniciar_scraping()
        send_message_to_telegram("Script Scraper AppySaude executado com sucesso", CANAL_NOTIFICACOES_BETFAIR)
    except Exception as e:
        send_message_to_telegram(f"Erro ao executar script Scraper AppySaude: {e}", CANAL_NOTIFICACOES_BETFAIR)
