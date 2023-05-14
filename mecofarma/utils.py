import os
import re
import json
from datetime import datetime

import asyncio
import phonenumbers
import requests


CANAL_NOTIFICACOES_BETFAIR = "1001412054755"


async def contar():
    print("Começou contagem")
    await asyncio.sleep(20)
    print("Terminou contagem")


async def do_something():
    print("Começou")
    await contar()
    await asyncio.sleep(15)
    print("terminou")


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


def send_message_to_telegram(message, channel):
    try:
        message_sent = requests.get(
            "https://api.telegram.org/bot896947138:AAH5NQ9aOajFKrRPXC8tlIX96rpjvgWbqJI/sendMessage?chat_id=-" + channel
            + "&text={}&parse_mode=html".format(
                message))
        return message_sent
    except Exception as error:
        print("Error sending menssage to Telegram: ", error)


async def exportar_produtos_para_excel(df, nome_categoria):
    filename_excel = f"mecofarma-{nome_categoria}-{datetime.now().date()}.xlsx"
    df_ordenado = df.sort_values(['categoria', 'subcategoria', 'nome'])

    path_mecofarma_files = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')
    df_ordenado.to_excel(f'{path_mecofarma_files}/{filename_excel}', index=False)

    return filename_excel
