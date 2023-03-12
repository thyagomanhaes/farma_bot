import concurrent.futures
import time
import requests

from typing import Dict, List
from bs4 import BeautifulSoup
from mecofarma.mecofarma import scrap_produtos


def make_request_categoria(categoria: Dict):
    response = requests.get(categoria['link'])
    soup = BeautifulSoup(response.text, 'html.parser')

    menu_lateral_subcategorias = soup.find('div', {'data-role': 'ln_content'})
    subcategorias = menu_lateral_subcategorias.find_all('li')

    lista_subcategorias = []

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

        for nr_pagina in range(int(total)):
            item_subcategoria = {
                'categoria': categoria['nome'],
                'subcategoria': nome_subcategoria,
                'link_subcategoria': f"{link_subcategoria}?p={nr_pagina + 1}&product_list_limit=36"
            }

            lista_subcategorias.append(item_subcategoria)

    return lista_subcategorias


def request_subcategoria(link_subcategoria, nome_categoria, subcategoria):
    lista_produtos = scrap_produtos(link_subcategoria, nome_categoria, subcategoria)
    return lista_produtos


def scrap_urls_subcategorias(urls_subcategorias):
    total = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        tasks = [executor.submit(request_subcategoria, categoria['link_subcategoria'], categoria['categoria'],
                                 categoria['subcategoria']) for categoria in urls_subcategorias]
        results = []
        for result in concurrent.futures.as_completed(tasks):
            results.append(result)

        total += results

    return total


def obtem_links_subcategorias(lista_categorias):
    urls_subcategorias = []

    for categoria in lista_categorias:
        links_subcategorias = make_request_categoria(categoria)
        urls_subcategorias += links_subcategorias

    return urls_subcategorias


def executar_scrap_paralelo(lista_categorias) -> List:
    start = time.time()

    urls_subcategorias = obtem_links_subcategorias(lista_categorias)
    print(f"{len(urls_subcategorias)} links de subcategorias")

    _produtos = scrap_urls_subcategorias(urls_subcategorias)

    lista_produtos = []

    l_produtos = [lp._result for lp in _produtos]

    for l_produto in l_produtos:
        for produto in l_produto:
            lista_produtos.append(produto)

    end = time.time()
    total_time = round(end - start, 2)
    print(f"{len(lista_produtos)} produtos coletados com sucesso em {total_time} segundos!")
    return lista_produtos
