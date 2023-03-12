import asyncio
import aiohttp
from bs4 import BeautifulSoup

pages = range(1, 3)
base_url = "https://scrapeme.live/shop/page"


def store_results(list_of_lists):
    pokemon_list = sum(list_of_lists, [])  # flatten lists

    with open("pokemon.csv", "w") as pokemon_file:
        # get dictionary keys for the CSV header
        fieldnames = pokemon_list[0].keys()
        file_writer = csv.DictWriter(pokemon_file, fieldnames=fieldnames)
        file_writer.writeheader()
        file_writer.writerows(pokemon_list)


async def extract_details(page, session):

    # similar to requests.get but with a different syntax
    async with session.get(f"{base_url}/{page}/") as response:
        # notice that we must await the .text() function
        soup = BeautifulSoup(await response.text(), "html.parser")

        pokemon_list = []

        for pokemon in soup.select(".product"):  # loop each product
            pokemon_list.append({
                "id": pokemon.find(class_="add_to_cart_button").get("data-product_id"),
                "name": pokemon.find("h2").text.strip(),
                "price": pokemon.find(class_="price").text.strip(),
                "url": pokemon.find(class_="woocommerce-loop-product__link").get("href"),
            })

        return pokemon_list


async def main():
    # create an aiohttp session and pass it to each function execution
    async with aiohttp.ClientSession() as session:
        tasks = [
            extract_details(page, session)
            for page in pages
        ]
        list_of_lists = await asyncio.gather(*tasks)
        store_results(list_of_lists)


asyncio.run(main())