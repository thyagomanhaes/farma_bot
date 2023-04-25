# -*- coding: utf-8 -*-
import logging
import time
from datetime import datetime
import pandas as pd
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from decouple import config

from appysaude.appysaude import scrap_pagina_produtos, exportar_produtos_para_excel, make_request
from appysaude.constants import BOTOES_APPYSAUDE, URL_LISTAR_PRODUTOS_APPY_SAUDE
from mecofarma.mecofarma import CATEGORIAS_MECOFARMA, transformar_lista_em_df
from mecofarma.constants import BOTOES_MECOFARMA, BOTOES_MENU_FARMA_BOT
import mecofarma.mecofarma_paralelo as mec_paralelo
import mecofarma.mecofarma as mec

logging.basicConfig(format='%(asctime)s : %(levelname)s => %(message)s', level=logging.INFO,
                    filename='farma_bot.log')

STRING_SESSION_BOT_DEV = config('STRING_SESSION_BOT_DEV')
FARMABOT_TELEGRAM_API_ID = config('FARMABOT_TELEGRAM_API_ID')
FARMABOT_TELEGRAM_API_HASH = config('FARMABOT_TELEGRAM_API_HASH')
BOT_TOKEN_GREENVEST_BOT_DEV = config('BOT_TOKEN_GREENVEST_BOT_DEV')

# Instanciando o bot a partir da string de sessão
farmabot_client = TelegramClient(
    StringSession(STRING_SESSION_BOT_DEV),
    int(FARMABOT_TELEGRAM_API_ID), 
    FARMABOT_TELEGRAM_API_HASH
).start(bot_token=BOT_TOKEN_GREENVEST_BOT_DEV)


@farmabot_client.on(events.CallbackQuery)
async def callback(event):
    print("EVENTO ", event)
    sender = await event.get_sender()

    if event.data in BOTOES_MENU_FARMA_BOT.keys():
        if event.data == b'botaoTodasCategorias':
            try:
                msg = "Muito bem!🤩 \nVocê escolheu <b>Todas as categorias</b>!\n\nO site possui mais de 5.000 produtos e este processo pode demorar 30 minutos ⏳"
                msg += "\n\nMas fica tranquilo! Assim que finalizar irei te avisar e será enviado um arquivo excel com todos os produtos coletados, tá? 😉"
                await event.respond(msg, parse_mode='html')

                await event.respond("Iniciando processo de coleta de dados.Por favor, aguarde... ⏳", parse_mode='html')

                start = time.time()
                products_list = mec_paralelo.executar_scrap_paralelo(CATEGORIAS_MECOFARMA)

                df_products = transformar_lista_em_df(lista_produtos=products_list)

                nome_arquivo = mec.exportar_produtos_para_excel(df_products, 'todas-as-categorias')

                sender = await event.get_sender()
                id_user_telegram = sender.id

                user = await farmabot_client.get_entity(id_user_telegram)

                end = time.time()
                total_time = round(end - start, 2)

                msg_sucesso = f"{len(products_list)} produtos coletados com sucesso em {total_time} segundos!"

                await event.respond(msg_sucesso, parse_mode='html')
                await event.respond("Ufa!😅 Coleta finalizada. Aqui está seu arquivo 👇", parse_mode='html')
                await farmabot_client.send_file(user, nome_arquivo)
                await event.respond("Até a próxima 👋🏻!\nSempre que quiser acessar o menu digite /mecofarma", parse_mode='html')

            except Exception as e:
                await event.respond(f"Ocorreu um erro ao realizar o scraping. Por favor, tente novamente em instantes",
                                    parse_mode='html')
        else:
            url_categoria = BOTOES_MENU_FARMA_BOT.get(event.data).get('link')
            nome_categoria = BOTOES_MENU_FARMA_BOT.get(event.data).get('nome')
            msg = f"Muito bem!🤩 \nVocê escolheu <b>{nome_categoria}</b>!\n\nO procesos de coleta de dados pode demorar alguns minutos ⏳"
            msg += f"\n\nMas fica tranquilo! Assim que finalizar irei te avisar e assim que o processo estiver finalizado te enviarei um arquivo excel com todos os produtos coletados, tá? 😉"
            await event.respond(msg, parse_mode='html')

            await event.respond("Iniciando processo de coleta de dados.Por favor, aguarde... ⏳", parse_mode='html')

            start_categoria = time.time()

            try:
                lista_url_categoria = []

                for categoria in CATEGORIAS_MECOFARMA:
                    if categoria.get('link') == url_categoria:
                        lista_url_categoria.append(categoria)
                        break

                products_list = mec_paralelo.executar_scrap_paralelo(lista_url_categoria)

                df = mec.transformar_lista_em_df(lista_produtos=products_list)

                nome_arquivo = mec.exportar_produtos_para_excel(df, nome_categoria)

                sender = await event.get_sender()
                id_user_telegram = sender.id

                user = await farmabot_client.get_entity(id_user_telegram)

                end = time.time()
                total_time = round(end - start_categoria, 2)

                msg_sucesso = f"Ufa!😅 Coleta finalizada!" \
                              f"\n\n{len(products_list)} produtos coletados com sucesso em {total_time} segundos!" \
                              f"\n\nAqui está seu arquivo 👇"

                await event.respond(msg_sucesso, parse_mode='html')
                await farmabot_client.send_file(user, nome_arquivo)
                await event.respond("Até a próxima 👋🏻!\nSempre que quiser acessar o menu digite /mecofarma",
                                    parse_mode='html')

            except Exception as e:
                print("Erro ao realizar scraping: ", e)
                await event.respond(f"Ocorreu um erro ao realizar o scraping. Por favor, tente novamente em instantes",
                                    parse_mode='html')

    if event.data == b'botaoIniciarAppySaude':
        try:
            start = time.time()
            await event.respond("Iniciando", parse_mode='html')

            access_token = 'xxx'
            page = make_request(URL_LISTAR_PRODUTOS_APPY_SAUDE, access_token)

            totaproducts_list = page.json()['TotalCount']
            await event.respond(f"Iniciando coleta de <b>{totaproducts_list}</b> produtos disponíveis", parse_mode='html')

            products_list = scrap_pagina_produtos(page, access_token)

            df_produtos = pd.DataFrame.from_dict(products_list)

            nome_arquivo = exportar_produtos_para_excel(df_produtos)

            user = await farmabot_client.get_entity(sender.id)

            end = time.time()
            total_time = round(end - start, 2)

            msg_sucesso = f"{len(products_list)} produtos coletados com sucesso em {total_time} segundos!"

            await event.respond(msg_sucesso, parse_mode='html')
            await event.respond("Ufa!😅 Coleta finalizada. Aqui está seu arquivo 👇", parse_mode='html')
            await farmabot_client.send_file(user, nome_arquivo)
        except Exception as e:
            print(e)
            await event.respond("Ocorreu um erro ao coletar dados para este siste. Por favor, tente novamente.",
                                parse_mode='html')


@farmabot_client.on(events.NewMessage(pattern='/mecofarma'))
async def mecofarma(event):
    await event.respond('🤖 Bem-vindo ao Web Scraping do site https://www.mecofarma.com')
    await event.respond('Escolha uma categoria para iniciar o processo de coleta de dados',
                        buttons=BOTOES_MECOFARMA)


@farmabot_client.on(events.NewMessage(pattern='/appysaude'))
async def appysaude(event):
    await event.respond('🤖 Bem-vindo ao Web Scraping do site https://www.appysaude.co.ao/home')
    await event.respond("Clique no botão abaixo para iniciar a coleta de dados", buttons=BOTOES_APPYSAUDE)


def main():
    print(f"[{datetime.now()}]: FarmaBot is ready ... Awaiting requests")
    farmabot_client.run_until_disconnected()


if __name__ == '__main__':
    main()
