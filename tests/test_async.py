import httpx
import asyncio
import requests
from time import time
import mecofarma.mecofarma_paralelo as mec_paralelo
from mecofarma.mecofarmax import CATEGORIAS_MECOFARMA

subcategorias2 = [
    {
        'categoria': 'Farmácia',
        'subcategoria': 'Dor e Febre',
        'qtd_itens_subcategoria': 72,
        'link_subcategoria': 'https://www.mecofarma.com/pt/farmacia/dor-e-febre?p=1&product_list_limit=36'
    },
    {
        'categoria': 'Farmácia',
        'subcategoria': 'Dor e Febre',
        'qtd_itens_subcategoria': 72,
        'link_subcategoria': 'https://www.mecofarma.com/pt/farmacia/dor-e-febre?p=2&product_list_limit=36'
    }
]

def test_sync():
    _start = time()
    for i in range(50):
        print(i)
        requests.get("http://httpbin.org/delay/1")
    print(f"finished in: {time() - _start:.2f} seconds")
    # finished in: 52.21 seconds


async def main():
    _start = time()
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in subcategorias]
        for response_future in asyncio.as_completed(tasks):
            response = await response_future
        print(f"finished in: {time() - _start:.2f} seconds")


async def main2():
    subcategorias = await mec_paralelo.obtem_links_subcategorias(CATEGORIAS_MECOFARMA)
    # print(len(subcategorias2))

    _produtos = await mec_paralelo.scrape_subcategories(subcategorias)
    print(len(_produtos))


asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main2())
