import asyncio
import time

import aiohttp
from bs4 import BeautifulSoup

pages = [n for n in range(43582) if n % 50 == 0]

base_url = "https://scrapeme.live/shop/page"
# pages = range(1, 49) # max page (48) + 1


async def extract_details(page, session):
    # similar to requests.get but with a different syntax
    # async with session.get(f"{base_url}/{page}/") as response:
    async with session.get(f"https://www.appysaude.co.ao/v1.0/products/productList?filter=&search=&skip={page}&sort=3") as response:
        # notice that we must await the .text() function
        # soup = BeautifulSoup(await response.text(), "html.parser")

        # soup = BeautifulSoup(page.text, 'html.parser')

        pokemon_list = []
        el = await response.json()
        # print(el)

        if el.get('Fields') is not None:
            count_total_products = el['TotalCount']
            lista = el['Fields']
            print(lista)
            pokemon_list.append(lista)

    return pokemon_list


async def main():
    # create an aiohttp session and pass it to each function execution
    async with aiohttp.ClientSession() as session:
        tasks = [
            extract_details(page, session)
            for page in pages
        ]
        list_of_lists = await asyncio.gather(*tasks)
    # store_results(list_of_lists)
    # print(list_of_lists)

start = time.time()
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncio.run(main())
end = time.time()

total_time = end - start
print(f"{total_time} sec")
