import asyncio
import concurrent.futures
import datetime
import time

import httpx
import requests

from typing import Dict, List
from bs4 import BeautifulSoup
from mecofarmax import scrap_produtos, scrap_pagina_produtos

import aiohttp
import threading


async def make_request_categoria(categoria: Dict):
    async with aiohttp.ClientSession(trust_env=True) as session:
        async with session.get(categoria['link'], ssl=False) as resp:
            body = await resp.text()
            # if we use requests will block here until web server responds
            # response = requests.get(categoria['link'])
            soup = BeautifulSoup(body, 'html.parser')

            menu_lateral_subcategorias = soup.find('div', {'data-role': 'ln_content'})
            subcategorias = menu_lateral_subcategorias.find_all('li')

            lista_subcategorias = []
            total_itens = 0

            for sub in subcategorias:
                link_subcategoria = sub.find('a')['href']
                nomes_subcategoria = sub.find('a').text
                nome_subcategoria = nomes_subcategoria.split('\n')[1].strip()
                qtd_itens_subcategoria = nomes_subcategoria.split('\n')[2].strip()

                qtd_itens_subcategoria = int(qtd_itens_subcategoria)

                total_paginas = (qtd_itens_subcategoria / 36)
                mod_paginas = qtd_itens_subcategoria % 36

                if mod_paginas == 0:
                    total = int(total_paginas)
                else:
                    total = 1 if qtd_itens_subcategoria < 36 else int(total_paginas) + 1
                print(f"{nome_subcategoria} ({qtd_itens_subcategoria})")
                total_itens += qtd_itens_subcategoria

                for nr_pagina in range(int(total)):
                    item_subcategoria = {
                        'categoria': categoria['nome'],
                        'subcategoria': nome_subcategoria,
                        'qtd_itens_subcategoria': qtd_itens_subcategoria,
                        'link_subcategoria': f"{link_subcategoria}?p={nr_pagina + 1}&product_list_limit=36"
                    }

                    lista_subcategorias.append(item_subcategoria)

    return lista_subcategorias


async def request_subcategoria(link_subcategoria, nome_categoria, subcategoria):
    lista_produtos = await scrap_produtos(link_subcategoria, nome_categoria, subcategoria)
    return lista_produtos


async def request_subcategory(client, link_subcategoria, categoria, subcategoria):
    response = await client.get(link_subcategoria)
    soup = BeautifulSoup(response.text, 'html.parser')
    print(f"Request to {link_subcategoria}")
    if soup is not None:
        products = await scrap_pagina_produtos(link_subcategoria, categoria, subcategoria, False)
        return products

    return soup


def request_por_cnp(url_cnp: str):

    response_page = requests.get(url_cnp)
    lista_produtos = response_page.json()
    if len(lista_produtos) > 0:
        print(f"Existe: {url_cnp}")
        for produto in lista_produtos:
            produto['cnp'] = url_cnp.split('?q=')[1]
        return lista_produtos

    print(f"Não existe: {url_cnp}")
    return []


async def scrap_subcategorias(urls_subcategorias):
    for categoria in urls_subcategorias:
        await scrap_pagina_produtos(categoria['link_subcategoria'],
                                    categoria['categoria'], categoria['subcategoria'], False)


async def scrap_urls_subcategorias(subcategorias):
    total = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        tasks = [executor.submit(request_subcategoria, categoria['link_subcategoria'], categoria['categoria'],
                                 categoria['subcategoria']) for categoria in subcategorias]
        results = []
        for result in concurrent.futures.as_completed(tasks):
            results.append(result)

        total += results

    return total


async def scrape_subcategories(subcategories):
    """
    Scrap products from URLs subcategories
    :param subcategories:
    :return:
    """
    results = []
    _start = time.time()

    async with aiohttp.ClientSession(trust_env=True) as session:
        for categoria in subcategories:
            async with session.get(categoria['link_subcategoria'], ssl=False) as resp:
                body = await resp.text()

    async with httpx.AsyncClient() as client:
        async_tasks = [request_subcategory(
            client, categoria['link_subcategoria'],
            categoria['categoria'], categoria['subcategoria']) for categoria in subcategories]

        for result in asyncio.as_completed(async_tasks):
            response = await result
            results.append(response)
    print(f"Coleta de produtos finalizada em {time.time() - _start:.2f}")
    return results


def scrap_urls_cnps(urls_cnps):
    total = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        tasks = [executor.submit(request_por_cnp, url_cnp) for url_cnp in urls_cnps]
        results = []
        for result in concurrent.futures.as_completed(tasks):
            results.append(result)

        total += results

    return total


async def obtem_links_subcategorias(lista_categorias):
    urls_subcategorias = []
    _start = time.time()
    for categoria in lista_categorias:
        links_subcategorias = await make_request_categoria(categoria)
        urls_subcategorias += links_subcategorias
    # print("Coletando dados em 10s...")
    # await asyncio.sleep(10)
    print(f"Completed scrap subcategory links in {time.time() - _start:.2f}")
    return urls_subcategorias


async def executar_scrap_paralelo(lista_categorias) -> List:
    # start = time.time()

    urls_subcategorias = await obtem_links_subcategorias(lista_categorias)
    print(f"{len(urls_subcategorias)} links de subcategorias")

    # _produtos = scrap_urls_subcategorias(urls_subcategorias)
    #
    # lista_produtos = []
    #
    # l_produtos = [lp._result for lp in _produtos]
    #
    # for l_produto in l_produtos:
    #     for produto in l_produto:
    #         lista_produtos.append(produto)
    #
    # end = time.time()
    # total_time = round(end - start, 2)
    # print(f"{len(lista_produtos)} produtos coletados com sucesso em {total_time} segundos!")
    return urls_subcategorias


def salvar_produtos_no_banco(lista_produtos):

    for produto in lista_produtos:
        dt_str = produto['data_scraping'].strftime("%Y-%m-%d %H:%M:%S")
        # TODO: Tratar o escape do price "18\xa0078,50"
        produto = {
            "category": produto['categoria'],
            "subcategory": produto['subcategoria'],
            "name": produto['nome'],
            "cnp": produto['cnp'],
            "ref": produto['ref'],
            "price": 5.50,
            "status": produto['status'],
            "date_scraping": dt_str,
            "url_product": produto['link_produto'],
            "creator_id": 1
        }

        salvar_produto(produto)


def salvar_produto(produto):
    url_db = "http://localhost:8000/api/v1/products"

    try:
        response = requests.post(url=url_db, json=produto)

        if response.status_code == 201:
            print("Produto salvo com sucesso!")
        else:
            print("Tentando salvar no banco:", produto)

    except Exception as e:
        print(e)


def transform_products_list(products: List) -> List:
    lista_final_produtos = []

    '''
        a url pode vir assim: 'https://www.mecofarma.com/pt/catalog/product/view/id/83727/'
        tem que consultar a página para buscar a REF
    '''
    if len(products) > 0:
        for produto in products:
            search_type = produto.get('type')
            title = produto.get('title')
            image = produto.get('image')
            url = produto.get('url')
            price_div = produto.get('price')
            soup_div_price = BeautifulSoup(price_div, 'html.parser')
            spans = soup_div_price.find_all("span")
            cnp = produto.get('cnp')

            if 'catalog/product/view' in url:
                ref_number = scrap_pagina_produtos(url, None, None, True)
            else:
                ref_number = url.split('pt/')[1]

            price = None
            for span in spans:
                if span.attrs.get('data-price-amount') is not None:
                    price = span.attrs.get('data-price-amount')
                    break

            forma_terapeutica = produto.get('forma_terapeutica')
            print(title, price, forma_terapeutica)
            produto_final = {
                'nome': title,
                'preco': price,
                'cnp': cnp,
                'ref': ref_number,
                'link_produto': url,
                'date_scraping': datetime.datetime.now()
            }
            lista_final_produtos.append(produto_final)

    return lista_final_produtos
