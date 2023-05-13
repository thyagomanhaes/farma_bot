# -*- coding: utf-8 -*-
import asyncio
from datetime import datetime
import logging
import os
import sys
import time

import aiohttp
import pandas as pd
from bs4 import BeautifulSoup

import mecofarmax as mec
from constants import HTML_PARSER, NOME_ARQUIVO_TEMPORARIO
from utils import send_message_to_telegram, CANAL_NOTIFICACOES_BETFAIR

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler(sys.stdout)  # Where logged messages will output, in this case direct to console
formatter = logging.Formatter('[%(asctime)s : %(levelname)s] => %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)  # better to have too much log than not enough

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_STATIC = os.path.join(APP_ROOT, '../static')


async def get_subcategories_from_file(filename) -> list:
    df_subcategories = pd.read_csv(os.path.join(APP_STATIC, filename),
                                   usecols=['categoria', 'subcategoria', 'qtd_itens_subcategoria', 'link_subcategoria'])
    subcategories: list = df_subcategories.to_dict('records')
    return subcategories


async def scrape_subcategory(subcategory):
    async with aiohttp.ClientSession() as session:
        async with session.get(subcategory['link_subcategoria'], ssl=False) as response:
            webpage = await response.text()
            soup = BeautifulSoup(webpage, HTML_PARSER)

            products = []
            list_itens = soup.find_all('li', {"class": "product-item"})
            for li in list_itens:
                div_product_item_info = li.find('div', {"class": "product-item-info"})
                product_item_link = div_product_item_info.find('a', {'class': 'product-item-link'})

                div_unavailable = div_product_item_info.find('div', {"class": "unavailable"})
                status = "Disponível" if div_unavailable is None else "Indisponível"

                div_final_price = li.find('div', {"class": "price-final_price"})
                if div_final_price is not None:
                    price = div_final_price.find('span', {"class": "price"}).text
                else:
                    price = None

                product_name = product_item_link.text.strip()
                product_link = product_item_link['href']

                product = {
                    'categoria': subcategory['categoria'],
                    'subcategoria': subcategory['subcategoria'],
                    'nome': product_name,
                    'cnp': None,
                    'ref': None,
                    'preco': price,
                    'status': status,
                    'fornecedor': "mecofarma",
                    'data_scraping': datetime.now(),
                    'link_produto': product_link
                }
                logger.info(f"Product found: {product}")
                products.append(product)
            return products


async def scrape_subcategories():
    """
    Scrap data from subcategories links in mecofarma.com
    :return:
    """
    subcategories = await get_subcategories_from_file('subcategorias.csv')

    tasks = []
    _start = time.time()
    for subcategory in subcategories:
        task = asyncio.create_task(scrape_subcategory(subcategory))
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    logger.info(f'Scraping of {len(subcategories)} subcategories URLs finished')

    products = []
    for l_produto in results:
        for produto in l_produto:
            products.append(produto)

    if len(products) > 0:
        df_products = pd.DataFrame.from_records(products)
        filename = await mec.exportar_produtos_para_excel(df_products, NOME_ARQUIVO_TEMPORARIO)
        logger.info(f"Arquivo {filename} gerado em {time.time() - _start:.2f} seg com {len(products)} produtos.")


async def bound_fetch(sem, product, session):
    async with sem:
        updated_product = await fetch(product, session)
        return updated_product


async def scrape_products_details():
    path_mecofarma_files = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')
    df_produtos = pd.read_excel(
        f"{path_mecofarma_files}/mecofarma-{NOME_ARQUIVO_TEMPORARIO}-{datetime.now().date()}.xlsx")

    products = df_produtos.to_dict('records')

    tasks = []
    sem = asyncio.Semaphore(100)

    _start = time.time()
    async with aiohttp.ClientSession() as session:
        for product in products:
            task = asyncio.ensure_future(bound_fetch(sem, product, session))
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        final_products = []
        for result in results:
            if isinstance(result, dict):
                final_products.append(result)

        df_products = pd.DataFrame.from_records(final_products)

        nome_arquivo = await mec.exportar_produtos_para_excel(df_products, 'todas-as-categorias')
        print(f"Arquivo {nome_arquivo} gerado com {len(final_products)} produtos em {time.time() - _start:.2f} seg")


async def fetch(product, session):
    async with session.get(product['link_produto'], ssl=False) as response:
        text = await response.text()
        logger.info(f"Searching product details in ({product['link_produto']})")
        soup = BeautifulSoup(text, HTML_PARSER)

        if soup is not None:

            product_name = soup.find('h1', {"class": "page-title"}).text.strip()
            cnp = soup.find('span', {"class": "cnp"})
            if cnp is not None:
                cnp = cnp.text.strip()
                cnp_number = cnp.split('CNP: ')[1]
            else:
                cnp_number = None

            ref = soup.find('span', {"class": "sku"})
            ref = ref.text.strip() if ref is not None else None

            if cnp is not None:
                cnp_number = cnp.split('CNP: ')[1]
            if ref is not None:
                ref_number = ref.split('REF: ')[1]

            logger.info(f"Details of {product_name} found: {cnp_number} | {ref_number}")
            product['cnp'] = cnp_number
            product['ref'] = ref_number

            return product


if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(scrape_subcategories())
        logger.info("Scraping of subcategories finished")
        time.sleep(1)
        logger.info("Starting scrape of products to get more info of each one")
        loop.run_until_complete(scrape_products_details())
        send_message_to_telegram("scraper_mecofarma executado com sucesso!", CANAL_NOTIFICACOES_BETFAIR)
    except Exception as e:
        send_message_to_telegram(f"Erro ao executar script Scraper AppySaude: {e}", CANAL_NOTIFICACOES_BETFAIR)
