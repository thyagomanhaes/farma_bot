# -*- coding: utf-8 -*-
import asyncio
import logging
import os
import sys
import time
from datetime import datetime
from typing import List

import pandas as pd
from telethon import TelegramClient, events, Button
from telethon.sessions import StringSession
from decouple import config
from telethon.tl.types import PeerUser

from appysaude.appysaude import scrap_pagina_produtos, exportar_produtos_para_excel, make_request
from appysaude.constants import BOTOES_APPYSAUDE, URL_LISTAR_PRODUTOS_APPY_SAUDE
from constants import BOTAO_CADASTRO_FARMABOT, BOTAO_AREA_ADMIN, URL_BUSCA_POR_CNP
from mecofarma import mecofarma_paralelo
from mecofarma.mecofarma import CATEGORIAS_MECOFARMA, transformar_lista_em_df
from mecofarma.constants import BOTOES_MECOFARMA, BOTOES_MENU_FARMA_BOT
import mecofarma.mecofarma_paralelo as mec_paralelo
import mecofarma.mecofarma as mec

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler(sys.stdout)  # Where logged messages will output, in this case direct to console
formatter = logging.Formatter('[%(asctime)s : %(levelname)s] => %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG) # better to have too much log than not enough

GREENVESTBOT_DEV_STRING_SESSION_BOT = config('GREENVESTBOT_DEV_STRING_SESSION_BOT')
FARMABOT_TELEGRAM_API_ID = config('FARMABOT_TELEGRAM_API_ID')
FARMABOT_TELEGRAM_API_HASH = config('FARMABOT_TELEGRAM_API_HASH')
GREENVESTBOT_DEV_BOT_TOKEN = config('GREENVESTBOT_DEV_BOT_TOKEN')

# Creating a bot cliente from string session
farmabot_client = TelegramClient(
    StringSession(GREENVESTBOT_DEV_STRING_SESSION_BOT),
    int(FARMABOT_TELEGRAM_API_ID),
    FARMABOT_TELEGRAM_API_HASH
).start(bot_token=GREENVESTBOT_DEV_BOT_TOKEN)


@farmabot_client.on(events.CallbackQuery)
async def callback(event):
    sender = await event.get_sender()
    logger.info(f"New event arrived from user {sender.id}: {event}")

    id_user_telegram = sender.id
    status_usuario = 'INATIVO'
    df_usuarios = pd.read_csv('files/usuarios.csv')
    df2 = df_usuarios[df_usuarios['id_usuario_telegram'] == id_user_telegram]
    if not df2.empty:
        # if bool(df2['is_admin'].values[0]) is True:
        #     await event.respond('Area ADMIN', buttons=BOTAO_AREA_ADMIN)
        #     return

        if bool(df2['ativo'].values[0]) is True:
            await event.respond('PODE SEGUIR')
            status_usuario = 'ATIVO'
        else:
            await event.respond('Você não possui permissão para acessar o bot. Fale com o adm.')
            return
    else:
        await event.respond('Usuário não cadastrado. Por favor realize o cadastro pelo botão abaixo',
                            buttons=BOTAO_CADASTRO_FARMABOT)

    if event.data == b'botaoCadastroFarmaBot':
        await event.respond('Vamos iniciar o cadastro')
        chat_with_user = await farmabot_client.get_entity(PeerUser(sender.id))
        async with farmabot_client.conversation(chat_with_user, timeout=300) as conv:

            try:
                await conv.send_message('🤖 Verificamos que você ainda não possui cadastro em nosso sistema.')
                await conv.send_message('Para realizar o cadastro, por favor, informe seu nome')
                await conv.send_message('O nome deve ser informado no seguinte padrão: João Silva, apenas Nome('
                                        'espaço)Sobrenome')
                name = await conv.get_response()
                name = name.text
                print("Nome: ", name)

                while not is_valid_name(name):
                    await conv.send_message("Ops! O nome não está no formato correto. Por favor, digite um nome "
                                            "válido.")
                    name = await conv.get_response()
                    name = name.text

                await conv.send_message('Falta pouco! Agora precisamos que informe seu número de Tel. no '
                                        'formato: +55DDDXXXXXXXXX')
                await conv.send_message('Por exemplo, se seu número de Tel. é (79) 99878-1950, Você digita '
                                        'assim:  +5579998781950')
                phone_number_user = await conv.get_response()
                phone_number_user = phone_number_user.text

                while not is_valid_phone_number(phone_number_user):
                    await conv.send_message("Este número de Tel. não está no formato correto! Por favor, tente "
                                            "novamente")
                    phone_number_user = await conv.get_response()
                    phone_number_user = phone_number_user.text
                    is_valid_phone_number(phone_number_user)

                print("Dados do usuario: ", name, sender.id, phone_number_user)
                new_user = {
                    'id_usuario_telegram': sender.id,
                    'numero_tel': phone_number_user,
                    'ativo': False,
                    'is_admin': False,
                    'data_expiracao': None
                }
                new_df = pd.DataFrame([new_user])
                df_usuarios = pd.concat([df_usuarios, new_df], axis=0, ignore_index=True)

                # df_usuarios = df_usuarios.append(new_user, ignore_index=True)
                df_usuarios.to_csv('usuarios.csv')
                await conv.send_message(f"Prazer em te conhecer, {name}{phone_number_user}")
                await conv.send_message('🕐 Cadastrado com sucesso!...')
            except asyncio.TimeoutError as timeout_error:
                await conv.send_message('Ops!Devido a inatividade por mais de 5min, vamos finalizar seu '
                                        'atendimento! 👋🏻')
                print("Erro TimeOut: ", timeout_error)
            except Exception as erro:
                LINK_SUPORTE = "https://t.me/suportegreenvest"
                print("Ocorreu um erro Genérico:", erro)
                await conv.send_message('Ocorreu um erro ao realizar seu cadastro. Entre em contato com o suporte '
                                        'através do link para resolver o mais rápido possível. \n' + LINK_SUPORTE)

    elif event.data in BOTOES_MENU_FARMA_BOT.keys() and status_usuario == 'ATIVO':
        if event.data == b'botaoBuscaPorCNP':
            chat_with_user = await farmabot_client.get_entity(PeerUser(sender.id))
            async with farmabot_client.conversation(chat_with_user, timeout=300) as conv:
                await conv.send_message('🤖 Por favor, envie o arquivo com a lista de CNPs nos formatos .csv ou .xlsx')
                resposta_usuario = await conv.get_response()

                while resposta_usuario.file is None:
                    await conv.send_message(
                        '🤖 Por favor, envie o arquivo com a lista de CNPs nos formatos .csv ou .xlsx')

                    resposta_usuario = await conv.get_response()

                # TODO: Verificar se o arquivo enviado está nos formatos exigidos
                sent_filename = resposta_usuario.file.name
                print(sent_filename)

                current_path = os.getcwd()
                arquivo_ja_existe = os.path.exists(current_path + "\\" + sent_filename)

                if not arquivo_ja_existe:
                    arquivo_enviado = await farmabot_client.download_media(resposta_usuario, sent_filename)

                else:
                    arquivo_enviado = sent_filename

                df_enviado = pd.read_excel(arquivo_enviado)

                if 'codigo' in df_enviado.columns:
                    lista_cnps = list(df_enviado['codigo'])
                    await conv.send_message(
                        f'🤖 Arquivo recebido com sucesso! Aguarde enquanto faço a coleta de dados de '
                        f'{len(lista_cnps)} CNPs informados no arquivo')

                    urls_cnps = [f'{URL_BUSCA_POR_CNP}{cnp}' for cnp in lista_cnps]

                    print(len(urls_cnps))

                    start = time.time()
                    try:
                        _produtos = mecofarma_paralelo.scrap_urls_cnps(urls_cnps)
                    except Exception as e:
                        print(e)

                    end = time.time()

                    total_time = round(end - start, 2)
                    print(f"\nTempo para coletar dados de {len(urls_cnps)} urls no site: {total_time} segundos")

                    lista_produtos = []

                    l_produtos = [lp._result for lp in _produtos]

                    for l_produto in l_produtos:
                        for produto in l_produto:
                            lista_produtos.append(produto)

                    print("Qtd produtos na Lista final: ", len(lista_produtos))

                    l_final = mecofarma_paralelo.transform_products_list(lista_produtos)

                    df = pd.DataFrame.from_dict(l_final)

                    nome_arquivo = mec.exportar_produtos_para_excel(df, '', True)

                    sender = await event.get_sender()
                    id_user_telegram = sender.id

                    user = await farmabot_client.get_entity(id_user_telegram)

                    await farmabot_client.send_file(user, nome_arquivo)

                    print("Recebido")
                    print(df_enviado)
        elif event.data == b'botaoTodasCategorias':
            try:
                msg = "Muito bem!🤩 \nVocê escolheu <b>Todas as categorias</b>!\n\nO site possui mais de 5.000 " \
                      "produtos e este processo pode demorar alguns minutos ⏳ "
                msg += "\n\nMas fica tranquilo! Após finalizado o processo, você será notificado e receberá um " \
                       "arquivo excel com todos os produtos coletados, tá? 😉 "
                await event.respond(msg, parse_mode='html')
                await event.respond("Iniciando processo de coleta de dados. Buscando todas as URLs de subcategorias."
                                    "Por favor, aguarde... ⏳", parse_mode='html')

                subcategorias: List = await mec_paralelo.obtem_links_subcategorias(CATEGORIAS_MECOFARMA)

                # subcategorias = [1, 2]
                if len(subcategorias) > 0:
                    # dft = pd.DataFrame.from_dict(subcategorias)
                    # dft.to_csv('subcategorias.csv')
                    # xx = dft.groupby(['categoria', 'subcategoria'])['qtd_itens_subcategoria'].mean()
                    # agrupado = xx.to_frame()
                    # total_itens = int(agrupado['qtd_itens_subcategoria'].sum())
                    # total_itens = 2
                    # await event.respond(f"Opa! {len(subcategorias)} URLs encontradas e {total_itens} produtos disponíveis")
                    await event.respond(f"Por favor, aguarde enquanto é feito o scraping...")

                    # subcategorias = [
                    #     {
                    #         'categoria': 'Farmácia',
                    #         'subcategoria': 'Dor e Febre',
                    #         'qtd_itens_subcategoria': 72,
                    #         'link_subcategoria': 'https://www.mecofarma.com/pt/farmacia/dor-e-febre?p=1&product_list_limit=36'
                    #     },
                    #     {
                    #         'categoria': 'Farmácia',
                    #         'subcategoria': 'Dor e Febre',
                    #         'qtd_itens_subcategoria': 72,
                    #         'link_subcategoria': 'https://www.mecofarma.com/pt/farmacia/dor-e-febre?p=2&product_list_limit=36'
                    #     }
                    # ]

                    start = time.time()
                    _produtos = await mec_paralelo.scrape_subcategories(subcategorias)
                    lista_produtos = []
                    for l_produto in _produtos:
                        for produto in l_produto:
                            lista_produtos.append(produto)

                    end = time.time()
                    total_time = end - start

                    if len(lista_produtos) > 0:
                        await event.respond(f"Coleta finalizada em {total_time} segundos com {len(lista_produtos)}")
                        df_products = pd.DataFrame.from_dict(lista_produtos)

                        nome_arquivo = await mec.exportar_produtos_para_excel(df_products, 'todas-as-categorias')

                        sender = await event.get_sender()
                        id_user_telegram = sender.id

                        user = await farmabot_client.get_entity(id_user_telegram)

                        msg_sucesso = f"{len(_produtos)} produtos coletados com sucesso em {total_time} segundos!"

                        await event.respond(msg_sucesso, parse_mode='html')
                        await event.respond("Ufa!😅 Coleta finalizada. Aqui está seu arquivo 👇", parse_mode='html')
                        await farmabot_client.send_file(user, nome_arquivo)
                        await event.respond("Até a próxima 👋🏻!\nSempre que quiser acessar o menu digite /mecofarma",
                                            parse_mode='html')
                    else:
                        await event.respond(f"Deu ruim")
                else:
                    await event.respond(f"Não consegui encontrar nenhuma URL de subcategoria disponível no site")

                    # lista_produtos = []
                    #
                    # l_produtos = [lp._result for lp in _produtos]
                    #
                    # for l_produto in l_produtos:
                    #     for produto in l_produto:
                    #         lista_produtos.append(produto)
                    #
                    # # end = time.time()
                    # # total_time = round(end - start, 2)
                    # print(f"{len(lista_produtos)} produtos coletados!")

                #
                # df_products = transformar_lista_em_df(lista_produtos=products_list)
                #
                # nome_arquivo = mec.exportar_produtos_para_excel(df_products, 'todas-as-categorias')
                #
                # sender = await event.get_sender()
                # id_user_telegram = sender.id
                #
                # user = await farmabot_client.get_entity(id_user_telegram)
                #
                # end = time.time()
                # total_time = round(end - start, 2)
                #
                # msg_sucesso = f"{len(products_list)} produtos coletados com sucesso em {total_time} segundos!"
                #
                # await event.respond(msg_sucesso, parse_mode='html')
                # await event.respond("Ufa!😅 Coleta finalizada. Aqui está seu arquivo 👇", parse_mode='html')
                # await farmabot_client.send_file(user, nome_arquivo)
                # await event.respond("Até a próxima 👋🏻!\nSempre que quiser acessar o menu digite /mecofarma", parse_mode='html')

            except Exception as e:
                logger.error(e)
                await event.respond(f"Ocorreu um erro ao realizar o scraping. Por favor, tente novamente em instantes",
                                    parse_mode='html')
        else:
            url_categoria = BOTOES_MENU_FARMA_BOT.get(event.data).get('link')
            nome_categoria = BOTOES_MENU_FARMA_BOT.get(event.data).get('nome')
            msg = f"Muito bem!🤩 \nVocê escolheu <b>{nome_categoria}</b>!\n\nO processo de coleta de dados pode demorar alguns minutos ⏳"
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

                products_list = await mec_paralelo.executar_scrap_paralelo(lista_url_categoria)

                # mec_paralelo.salvar_produtos_no_banco(products_list)
                # BUSCA POR CNP
                # https: // www.mecofarma.com / pt / search / ajax / suggest /?q = 8776450 & _ = 1681140062896

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

    elif event.data == b'botaoIniciarAppySaude':
        try:
            start = time.time()
            await event.respond("Iniciando", parse_mode='html')

            access_token = 'xxx'
            page = make_request(URL_LISTAR_PRODUTOS_APPY_SAUDE, access_token)

            totaproducts_list = page.json()['TotalCount']
            await event.respond(f"Iniciando coleta de <b>{totaproducts_list}</b> produtos disponíveis",
                                parse_mode='html')

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
    logger.info("/mecofarma requested")
    await event.respond('🤖 Bem-vindo ao Web Scraping do site https://www.mecofarma.com')
    await event.respond('Escolha uma categoria para iniciar o processo de coleta de dados',
                        buttons=BOTOES_MECOFARMA)


@farmabot_client.on(events.NewMessage(pattern='/appysaude'))
async def appysaude(event):
    logger.info("/appysaude requested")
    await event.respond('🤖 Bem-vindo ao Web Scraping do site https://www.appysaude.co.ao/home')
    await event.respond("Clique no botão abaixo para iniciar a coleta de dados", buttons=BOTOES_APPYSAUDE)


def main():
    logger.info(f"FarmaBot is ready ... Awaiting requests")
    farmabot_client.run_until_disconnected()


if __name__ == '__main__':
    import multiprocessing
    import platform

    logger.info(f"Plataform: {platform.system()}")
    logger.info(f"This machine has {multiprocessing.cpu_count()} CPU cores")
    main()
