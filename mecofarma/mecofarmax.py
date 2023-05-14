import asyncio
import concurrent
import os
import time
from typing import List

import aiohttp
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd

opcoes = {
    "1": {
        "nome": "Farmácia",
        "link": "https://www.mecofarma.com/pt/farmacia"
    },
    "2": {
        "nome": "Mamã e Bebé",
        "link": "https://www.mecofarma.com/pt/mam-e-bebe"
    },
    "3": {
        "nome": "Saúde e Beleza",
        "link": "https://www.mecofarma.com/pt/saude-e-beleza"
    },
    "4": {
        "nome": "Sexualidade",
        "link": "https://www.mecofarma.com/pt/sexualidade"
    },
    "5": {
        "nome": "Ortopedia",
        "link": "https://www.mecofarma.com/pt/ortopedia"
    },
    "6": {
        "nome": "Vida Saudável",
        "link": "https://www.mecofarma.com/pt/vida-saudavel"
    },
    "7": {
        "nome": "Acesspiruis e Dispositivos Médicos",
        "link": "https://www.mecofarma.com/pt/acessorios-e-dispositivos-medicos"
    }
}

LINK_EXEMPLO_PRODUTO = "https://www.mecofarma.com/pt/023751"


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


async def exportar_produtos_para_excel_cnp(df_cnp):
    filename_excel = f"mecofarma-resultado-busca-por-cnp-{datetime.now().date()}.xlsx"
    df_ordenado = df_cnp.sort_values(['nome'])
    df_ordenado.to_excel(filename_excel, index=False)

    return filename_excel


def resumo_df(df_gerado):
    df_agrupado = df_gerado.groupby(['subcategoria']).count()
    print(df_agrupado)


def realiza_request(url):
    time.sleep(0.01)
    # print(f"\nRealizando request para: {url}")
    page = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'})
    webpage = page.text

    soup = BeautifulSoup(webpage, 'html.parser')
    return soup


async def scrap_detalhes_produto(url):

    async with aiohttp.ClientSession() as session:
        async with session.get(url, ssl=False) as response:
            response = await response.text()
            soup2 = BeautifulSoup(response, 'html.parser')

            if soup2 is not None:
                print(f"Buscando detalhes do produto em: {url}")
                product_name = soup2.find('h1', {"class": "page-title"}).text.strip()
                cnp = soup2.find('span', {"class": "cnp"})
                if cnp is not None:
                    cnp = cnp.text.strip()
                    cnp_number = cnp.split('CNP: ')[1]
                else:
                    cnp_number = None

                ref = soup2.find('span', {"class": "sku"})

                ref = ref.text.strip() if ref is not None else None

                final_price = soup2.find('div', {"class": "price-final_price"})

                if final_price is not None:
                    final_price = final_price.text.strip()
                    preco = final_price.split('\n')[0]
                else:
                    preco = None

                print(product_name, cnp, cnp_number, preco)
                return cnp, preco, ref

    return None, None, None


async def scrap_pagina_produtos(url_pagina_produtos, cat, subcat, only_ref=False) -> List:
    produtos = []

    async with aiohttp.ClientSession() as session:
        async with session.get(url_pagina_produtos, ssl=False) as response:
            response = await response.text()

            soup2 = BeautifulSoup(response, 'html.parser')

            if soup2 is not None:
                list_itens = soup2.find_all('li', {"class": "product-item"})

                if only_ref:
                    div_p = soup2.find('div', {"class": "product-main-attributes"})
                    if div_p is not None:
                        div_p = div_p.text.strip()
                        if 'REF' in div_p:
                            ref_number = div_p.split('REF: ')[1]
                            return ref_number

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

                    await asyncio.sleep(2)
                    # cnp, preco, ref = await scrap_detalhes_produto(product_link)
                    cnp, preco, ref = None, None, None

                    n_price = None
                    cnp_number = None
                    ref_number = None

                    if price is not None:
                        n_price = price.split('\xa0AKZ')[0]

                    if cnp is not None:
                        cnp_number = cnp.split('CNP: ')[1]
                    if ref is not None:
                        ref_number = ref.split('REF: ')[1]

                    produto = {
                        'categoria': cat,
                        'subcategoria': subcat,
                        'nome': product_name,
                        'cnp': cnp_number,
                        'ref': ref_number,
                        'preco': n_price,
                        'status': status,
                        'fornecedor': "mecofarma",
                        'data_scraping': datetime.now(),
                        'link_produto': product_link
                    }
                    print(produto)

                    produtos.append(produto)

    return produtos


def scrap_por_termo_busca(termo):
    url = f'https://www.mecofarma.com/pt/catalogsearch/result/?q={termo}'

    soup = realiza_request(url)

    subcategorias_itens = soup.find('ol', {'class': 'items'})

    if len(subcategorias_itens) > 0:
        for item in subcategorias_itens:
            print(item.text)


def scrap_busca_por_ref(numero_ref):
    url = f"https://www.mecofarma.com/pt/{numero_ref}"
    print("url busca", url)
    soup = realiza_request(url)

    print(soup)

    subcategorias_itens = soup.find('ol', {'class': 'items'})

    if len(subcategorias_itens) > 0:
        for item in subcategorias_itens:
            print(item.text)


def obtem_quantitativos_categoria(subcategorias):
    metadados = {}
    total_itens_categoria = 0

    for sub in subcategorias:
        link_subcategoria = sub.find('a')['href']
        nomes_subcategoria = sub.find('a').text
        nome_subcategoria = nomes_subcategoria.split('\n')[1].strip()
        qtd_itens_subcategoria = nomes_subcategoria.split('\n')[2].strip()
        total_itens_categoria += int(qtd_itens_subcategoria)

    # metadados['nome_subcategoria'] = nome_subcategoria
    # metadados['qtd_itens_subcategoria'] = qtd_itens_subcategoria
    metadados['total_itens_categoria'] = total_itens_categoria

    return metadados


async def scrap_categoria(url_categoria, nome_categoria, event, apenas_metadados=False):
    soup = realiza_request(url_categoria)

    subcategorias_itens = soup.find('ol', {'class': 'items'})

    menu_lateral_subcategorias = soup.find('div', {'data-role': 'ln_content'})

    subcategorias = menu_lateral_subcategorias.find_all('li')

    lista_produtos_categoria = []
    metadados_categoria = {}

    if len(subcategorias) > 0:
        total_itens_categoria = 0
        qtd_itens_subcategoria = 0

        if apenas_metadados:
            metadados_categoria = obtem_quantitativos_categoria(subcategorias)
        else:
            for sub in subcategorias:
                link_subcategoria = sub.find('a')['href']
                nomes_subcategoria = sub.find('a').text
                nome_subcategoria = nomes_subcategoria.split('\n')[1].strip()
                qtd_itens_subcategoria = nomes_subcategoria.split('\n')[2].strip()
                total_itens_categoria += int(qtd_itens_subcategoria)
                print(f"{nome_subcategoria} ({qtd_itens_subcategoria}) {link_subcategoria}")

                await event.respond(
                    f"Iniciando coleta da subcategoria {nome_subcategoria} ({qtd_itens_subcategoria})...",
                    parse_mode='html')

                # if nome_subcategoria == 'Afecções da Pele':
                lista_produtos = scrap_produtos(link_subcategoria, nome_categoria, nome_subcategoria)
                lista_produtos_categoria += lista_produtos

        # print(f"\nTotal de Itens disponíveis para categoria {nome_categoria}: {total_itens_categoria}")

    return lista_produtos_categoria, metadados_categoria


async def scrap_produtos(url_subcategoria, cat, subcat):
    # print("Iniciando scrap produtos")
    # soup = realiza_request(f"{url_categoria}?product_list_limit=36")

    # soup = realiza_request(url_subcategoria)
    # page_itens = soup.find('ul', {'class': 'pages-items'})

    lista_final_produtos = []

    try:
        lista_final_produtos = await scrap_pagina_produtos(f"{url_subcategoria}", cat, subcat)
    except Exception as e:
        print(e)
    # if page_itens is not None:
    #     current = page_itens.find('li', {'class': 'current'})
    #     next_page = page_itens.find('li', {'class': 'pages-item-next'})
    #     previous_page = page_itens.find('li', {'class': 'pages-item-previous'})
    #
    #     pag = 1
    #
    #     while next_page is not None:
    #
    #         link_next_page = next_page.find('a')['href']
    #
    #         soup = realiza_request(f"{link_next_page}")
    #
    #         page_itens = soup.find('ul', {'class': 'pages-items'})
    #         previous_page = page_itens.find('li', {'class': 'pages-item-previous'})
    #         link_previous_page = previous_page.find('a')['href']
    #
    #         print(f"\n{bcolors.HEADER}====== Categoria ({cat}) | Página Nº{pag} ======> {link_previous_page}")
    #         lista_produtos = scrap_pagina_produtos(f"{link_previous_page}", cat, subcat)
    #
    #         lista_final_produtos = lista_final_produtos + lista_produtos
    #
    #         page_itens = soup.find('ul', {'class': 'pages-items'})
    #
    #         current = page_itens.find('li', {'class': 'current'})
    #         next_page = page_itens.find('li', {'class': 'pages-item-next'})
    #         pag = pag + 1
    #
    #         if next_page is None:
    #             url = link_previous_page.split('?')[0]
    #             url = f"{url}?p={pag}"
    #             url = f"{url}&product_list_limit=36"
    #             lista_produtos = scrap_pagina_produtos(url, cat, subcat)
    #             lista_final_produtos = lista_final_produtos + lista_produtos
    # else:
    #     lista_produtos = scrap_pagina_produtos(f"{url_categoria}?product_list_limit=36", cat, subcat)
    #     lista_final_produtos += lista_produtos

    return lista_final_produtos


def scrap_categorias():
    for key, opcao in opcoes.items():
        print(opcao)
        l_produtos = scrap_categoria(opcao["link"], opcao["nome"], None)

        try:
            df = transformar_lista_em_df(lista_produtos=l_produtos)
            agora = datetime.now()
            agora_str = agora.strftime("%d-%m-%Y")

            print(f"{df.shape[0]} coletados com sucesso!")
            opcao = opcao["nome"]
            salvar_csv(df, f"produtos_{opcao}_{agora_str}")
        except Exception as error:
            print("Erro ao salvar para csv: ", error)


def transformar_lista_em_df(lista_produtos):
    return pd.DataFrame.from_dict(lista_produtos)


def salvar_csv(df, nome_arquivo):
    app_root = os.path.dirname(os.path.abspath(__file__))
    df.to_csv(f'{app_root}/{nome_arquivo}.csv', encoding='utf-8-sig')
    print(f'Arquivo {app_root}/{nome_arquivo}.csv salvo com sucesso!')


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


async def scrap_urls_cnps(urls_cnps):
    total = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        tasks = [executor.submit(request_por_cnp, url_cnp) for url_cnp in urls_cnps]
        results = []
        for result in concurrent.futures.as_completed(tasks):
            results.append(result)

        total += results

    return total


async def transform_products_list(products: List) -> List:
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
                ref_number = await scrap_pagina_produtos(url, None, None, True)
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
                'date_scraping': datetime.now()
            }
            lista_final_produtos.append(produto_final)

    return lista_final_produtos

if __name__ == "__main__":
    start = time.time()

    print("==== WEBSCRAPING MECOFARMA ======")
    print("\nPor favor, selecione uma das categorias abaixo para iniciar a coleta de dados:")
    print(f"1. FARMÁCIA")
    print(f"2. MAMÃ E BEBÉ")
    print(f"3. SAÚDE E BELEZA")
    print(f"4. SEXUALIDADE")
    print(f"5. ORTOPEDIA")
    print(f"6. VIDA SAUDÁVEL")
    print(f"7. ACESSÓRIOS E DISPOSITIVOS MÉDICOS")
    print(f"8. Todas as categorias")
    numero = input("Qual categoria deseja fazer scraping? \n")

    while numero not in ["1", "2", "3", "4", "5", "6", "7", "8"]:
        print(f"\nOpção Inválida. Por favor escolha uma das opções possíveis")
        print(f"1. FARMÁCIA")
        print(f"2. MAMÃ E BEBÉ")
        print(f"3. SAÚDE E BELEZA")
        print(f"4. SEXUALIDADE")
        print(f"5. ORTOPEDIA")
        print(f"6. VIDA SAUDÁVEL")
        print(f"7. ACESSÓRIOS E DISPOSITIVOS MÉDICOS")
        print(f"8. Todas as categorias")
        numero = input("Qual categoria deseja fazer scraping? \n")

    if numero == "8":
        print('Opção escolhida: 8. Todas as Categorias', )
        scrap_categorias()
    elif numero == "9":
        print('Opção escolhida: 9. Busca por termo', )
        scrap_por_termo_busca('losatran')
    else:
        nome_opcao = opcoes[numero]["nome"]
        link_opcao = opcoes[numero]['link']
        print(f'Opção escolhida: {nome_opcao} - {link_opcao}')
        print(f'Aguarde enquanto inicia-se a coleta de dados para esta categoria...')

        l_produtos = scrap_categoria(link_opcao, nome_opcao, None)

        try:
            df = transformar_lista_em_df(lista_produtos=l_produtos)
            agora = datetime.now()
            agora_str = agora.strftime("%d-%m-%Y")
            salvar_csv(df, f"produtos_{nome_opcao}_{agora_str}")
        except Exception as error:
            print("Erro ao salvar para csv: ", error)

    end = time.time()
    total_time = round(end - start, 2)
    print(f"\nTempo para coletar dados: {total_time} segundos")
