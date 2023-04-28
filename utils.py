import re
import json

import asyncio
from bs4 import BeautifulSoup
import aiohttp
import phonenumbers

import mecofarma.mecofarma_paralelo as mec_paralelo


async def contar():
    print("Começou contagem")
    await asyncio.sleep(20)
    print("Terminou contagem")


async def do_something():
    print("Começou")
    await contar()
    await asyncio.sleep(15)
    print("terminou")


async def get_page(session, url, cat, subcat):
    async with session.get(url, ssl=False) as r:
        texto = await r.text()
        soup = BeautifulSoup(texto, 'html.parser')

        pds = await mec_paralelo.scrap_pagina_produtos(soup, cat, subcat, only_ref=False)
        return pds


async def get_all(session, urls):
    tasks = []
    for url in urls:
        task = asyncio.create_task(get_page(session, url['link_subcategoria'], url['categoria'],
                                            url['subcategoria']))
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    return results


async def main3(urls):
    async with aiohttp.ClientSession() as session:
        data = await get_all(session, urls)
        return data


async def write_list_of_ngram_dicts(list_of_dicts, filename):
    async with open(filename, 'w', encoding='utf-8') as file:
        for dic in list_of_dicts:
            data = json.dumps(dic)
            file.write(data)
            file.write("\n")


def is_valid_name(name):
    regex = "^[a-záàâãéèêíïóôõöúçñÁÀÂÃÉÈÍÏÓÔÕÖÚÇÑ]+\s[a-záàâãéèêíïóôõöúçñÁÀÂÃÉÈÍÏÓÔÕÖÚÇÑ]+$"
    check_name = re.search(regex, name, re.IGNORECASE)
    return check_name


def is_valid_phone_number(phone_number):
    try:
        phone = phonenumbers.parse(phone_number, None)
        return phonenumbers.is_possible_number(phone) and phonenumbers.is_valid_number(phone)
    except Exception as error:
        print("Erro ao validar número do Telefone", error)
