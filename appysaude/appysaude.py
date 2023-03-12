from datetime import datetime
import concurrent.futures
import requests
from bs4 import BeautifulSoup
import time
import pandas as pd


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
            produto['nome'] = x['Name']
            produto['descricao'] = x.get('ShortDescriptionEn')
            produto['nome_completo'] = x.get('Name') + " " + x.get('ShortDescriptionEn')
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
    while access_token is None:
        access_token = input("Informe o token da sua sessão no site Appysaude:\n")


        print("\nAguarde enquanto o token é validado...")
        headers = {
            "Authorization": f"Bearer {access_token}",
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
        }

        url1 = f"https://www.appysaude.co.ao/v1.0/products/productList?filter=&search=&skip=50&sort=3"
        page = requests.get(url1, headers=headers)
        if page.status_code == 401:
            print("Token Inválido! Por favor, tente novamente. Obs: Seu token expira 1 hora após ter feito o login.")
            access_token = None
        elif page.status_code == 200:
            print("Token validado com sucesso!!!")

            print("Iniciando scraping dos produtos...")
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

            print(lista_produtos)

            df = pd.DataFrame.from_dict(lista_produtos)
            df.to_csv('scrap_appsaude.csv', encoding='utf-8-sig')

            end = time.time()

            total_time = round(end - start, 2)
            print(f"\nTempo para coletar dados: {total_time} segundos")


if __name__ == '__main__':
    iniciar_scraping()
