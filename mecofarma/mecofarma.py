import os
import time

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

CATEGORIAS_MECOFARMA = [
    {
        "nome": "Farmácia",
        "link": "https://www.mecofarma.com/pt/farmacia"
    },
    {
        "nome": "Mamã e Bebé",
        "link": "https://www.mecofarma.com/pt/mam-e-bebe"
    },
    {
        "nome": "Saúde e Beleza",
        "link": "https://www.mecofarma.com/pt/saude-e-beleza"
    },
    {
        "nome": "Sexualidade",
        "link": "https://www.mecofarma.com/pt/sexualidade"
    },
    {
        "nome": "Ortopedia",
        "link": "https://www.mecofarma.com/pt/ortopedia"
    },
    {
        "nome": "Vida Saudável",
        "link": "https://www.mecofarma.com/pt/vida-saudavel"
    },
    {
        "nome": "Acessórios e Dispositivos Médicos",
        "link": "https://www.mecofarma.com/pt/acessorios-e-dispositivos-medicos"
    }
]

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


def exportar_produtos_para_excel(df, nome_categoria):
    filename_excel = f"mecofarma-{nome_categoria}-{datetime.now().date()}.xlsx"

    df_ordenado = df.sort_values(['categoria', 'subcategoria', 'nome'])

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


def scrap_detalhes_produto(url):
    soup2 = realiza_request(url)
    if soup2 is not None:
        print(f"Buscando detalhes em: {url}")
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

        # print(product_name, cnp, cnp_number, preco)
        return product_name, cnp, preco, ref


def scrap_pagina_produtos(url_pagina_produtos, cat, subcat):

    soup2 = realiza_request(url_pagina_produtos)

    if soup2 is not None:
        list_itens = soup2.find_all('li', {"class": "product-item"})

        produtos = []

        for li in list_itens:
            divs = li.find_all('div', {"class": "product-item-details"})

            div_product_categories = li.find('div', {"class": "product-categories"})
            cat_links = div_product_categories.find_all('a')

            div_product_item_info = li.find('div', {"class": "product-item-info"})

            links = div_product_item_info.find_all('a')

            div_unavailable = div_product_item_info.find('div', {"class": "unavailable"})

            status = "Disponível" if div_unavailable is None else "Indisponível"

            div_final_price = li.find('div', {"class": "price-final_price"})
            if div_final_price is not None:
                price = div_final_price.find('span', {"class": "price"}).text
            else:
                price = None

            subcat_name = cat_links[0].text.strip()
            cat_link = cat_links[0]['href']

            product_link = links[0]['href']

            if len(cat_links) > 1:
                subcat_name = cat_links[1].text.strip()
                subcat_link = cat_links[1]['href']

                if subcat_name == cat:
                    subcat_name = cat_links[0].text.strip()

            for count, div in enumerate(divs):

                product_name = div.find('a').text.strip()
                product_link = div.find('a')['href']
                print(f"\nColetando dados para o produto ({product_name}): {product_link}")
                product_name, cnp, preco, ref = scrap_detalhes_produto(product_link)

                date_scraping = datetime.now()

                produto = {}

                n_price = None
                cnp_number = None
                ref_number = None

                if price is not None:
                    n_price = price.split('\xa0AKZ')[0]

                if cnp is not None:
                    cnp_number = cnp.split('CNP: ')[1]
                if ref is not None:
                    ref_number = ref.split('REF: ')[1]

                # print(f"{cat_name} | {product_name} | {cnp} | {ref} | {preco} | {date_scraping}")
                print(f"{cat} | {subcat} | {product_name} | {n_price} | {cnp_number} | {ref_number} | {status} | {date_scraping}")
                produto['categoria'] = cat
                produto['subcategoria'] = subcat
                produto['nome'] = product_name
                produto['cnp'] = cnp_number
                produto['ref'] = ref_number
                produto['preco'] = n_price
                produto['status'] = status
                produto['fornecedor'] = "mecofarma"
                produto['data_scraping'] = date_scraping
                produto['link_produto'] = product_link

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
                    f"Iniciando coleta da subcategoria {nome_subcategoria} ({qtd_itens_subcategoria})...", parse_mode='html')

                # if nome_subcategoria == 'Afecções da Pele':
                lista_produtos = scrap_produtos(link_subcategoria, nome_categoria, nome_subcategoria)
                lista_produtos_categoria += lista_produtos

        # print(f"\nTotal de Itens disponíveis para categoria {nome_categoria}: {total_itens_categoria}")

    return lista_produtos_categoria, metadados_categoria


def scrap_produtos(url_subcategoria, cat, subcat):
    # print("Iniciando scrap produtos")
    # soup = realiza_request(f"{url_categoria}?product_list_limit=36")

    soup = realiza_request(url_subcategoria)
    page_itens = soup.find('ul', {'class': 'pages-items'})

    lista_final_produtos = []

    lista_final_produtos = scrap_pagina_produtos(f"{url_subcategoria}", cat, subcat)

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
        l_produtos = scrap_categoria(url_categoria=opcao["link"], nome_categoria=opcao["nome"])

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

        l_produtos = scrap_categoria(url_categoria=link_opcao, nome_categoria=nome_opcao)

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
