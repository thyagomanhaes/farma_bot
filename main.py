# -*- coding: utf-8 -*-
import asyncio
import logging
import os
import sys
import time
from datetime import datetime

import pandas as pd
from decouple import config
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import PeerUser

import mecofarma.mecofarmax as mec
from appysaude.constants import BOTOES_APPYSAUDE
from constants import BOTAO_CADASTRO_FARMABOT, URL_BUSCA_POR_CNP
from mecofarma.constants import BOTOES_MECOFARMA, BOTOES_MENU_FARMA_BOT, BOTOES_ADMIN_MECOFARMA, BOTOES_ADMIN_FARMABOT
from mecofarma.utils import CANAL_NOTIFICACOES_BETFAIR, send_message_to_telegram
from utils import is_valid_name, is_valid_phone_number


logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler(sys.stdout)  # Where logged messages will output, in this case direct to console
formatter = logging.Formatter('[%(asctime)s : %(levelname)s] => %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)  # better to have too much log than not enough

FARMABOT_STRING_SESSION_BOT = config('FARMABOT_STRING_SESSION_BOT')
FARMABOT_TELEGRAM_API_ID = config('FARMABOT_TELEGRAM_API_ID')
FARMABOT_TELEGRAM_API_HASH = config('FARMABOT_TELEGRAM_API_HASH')
FARMABOT_BOT_TOKEN = config('FARMABOT_BOT_TOKEN')

# Creating a bot client from string session
farmabot_client = TelegramClient(
    StringSession(FARMABOT_STRING_SESSION_BOT),
    int(FARMABOT_TELEGRAM_API_ID),
    FARMABOT_TELEGRAM_API_HASH
).start(bot_token=FARMABOT_BOT_TOKEN)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_STATIC = os.path.join(APP_ROOT, 'static')

USUARIOS_FILE = 'usuarios.csv'


async def verify_user(sender):
    id_user_telegram = sender.id

    df_users = pd.read_csv(os.path.join(APP_STATIC, USUARIOS_FILE))
    df_user = df_users[df_users['id_usuario_telegram'] == id_user_telegram]

    if not df_user.empty:
        user = df_user.to_dict('records')[0]
        return user


async def read_csv_users():
    df_users = pd.read_csv(os.path.join(APP_STATIC, USUARIOS_FILE))
    return df_users


@farmabot_client.on(events.CallbackQuery)
async def callback(event):
    sender = await event.get_sender()
    logger.info(f"New event arrived from user {sender.id}: {event}")

    user = await verify_user(sender)
    logger.info(f"User from CSV file: {user}")
    if user is None:
        logger.info(f"User not found")
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
                        'nome': name,
                        'ativo': False,
                        'is_admin': False,
                        'data_expiracao': None
                    }
                    new_df = pd.DataFrame([new_user])

                    df_users = pd.read_csv(os.path.join(APP_STATIC, USUARIOS_FILE))

                    df_users = pd.concat([df_users, new_df], axis=0, ignore_index=True)

                    df_users.to_csv(os.path.join(APP_STATIC, USUARIOS_FILE), index=False)
                    await conv.send_message(f"Prazer em te conhecer, {name}!")
                    await conv.send_message('🕐 Cadastro realizado com sucesso! Fale com o ADM do FarmaBot para ativar sua conta')
                except asyncio.TimeoutError as timeout_error:
                    await conv.send_message('Ops!Devido a inatividade por mais de 5min, vamos finalizar seu '
                                            'atendimento! 👋🏻')
                    print("Erro TimeOut: ", timeout_error)
                except Exception as erro:
                    LINK_SUPORTE = "https://t.me/suportegreenvest"
                    print("Ocorreu um erro Genérico:", erro)
                    await conv.send_message('Ocorreu um erro ao realizar seu cadastro. Entre em contato com o suporte '
                                            'através do link para resolver o mais rápido possível. \n' + LINK_SUPORTE)
        else:
            await event.respond(
                "Você não possui cadastro no FarmaBot. Por favor, clique no botão para iniciar o cadastro.",
                buttons=BOTAO_CADASTRO_FARMABOT)
    elif user['ativo'] is False:
        logger.info(f"User {user} is inactive")
        await event.respond("Você não está ativo. Por favor, fale com o ADM do FarmaBot para ativar sua conta",
                            parse_mode='html')

    elif user['ativo'] is True:
        logger.info(f"User {user} is active and can use the bot")
        if event.data in [b'botaoListarUsuarios']:
            df_users = await read_csv_users()
            msg = "Nº | Nome | Ativo\n"

            for i, user in df_users.iterrows():
                username = user.get('nome')
                ativo = 'Sim ✅' if user.get('ativo') else 'Não ❌'
                nome = f"{i} | {username} | {ativo}\n"
                msg += nome

            await event.respond(msg)

        elif event.data in [b'botaoAtivarUsuarios', b'botaoDesativarUsuarios']:
            acao = '<b>Ativar</b>' if event.data == b'botaoAtivarUsuarios' else '<b>Desativar</b>'

            await event.respond(f'Qual usuário você deseja {acao}?', parse_mode='html')
            df_users = await read_csv_users()
            msg = "Nº | Nome | Ativo | Admin\n"

            for i, user in df_users.iterrows():
                username = user.get('nome')
                ativo = 'Sim ✅' if user.get('ativo') else 'Não ❌'
                admin2 = 'Sim ✅' if user.get('is_admin') else 'Não ❌'
                nome = f"{i} | {username} | {ativo} | {admin2}\n"
                msg += nome

            await event.respond(msg)
            chat_with_user = await farmabot_client.get_entity(PeerUser(sender.id))
            async with farmabot_client.conversation(chat_with_user, timeout=300) as conv:
                await conv.send_message('Digite o número correspondente')
                try:
                    name = await conv.get_response()
                    name = name.text
                    print("Nome: ", name)
                    indexes = [str(i) for i in range(df_users.shape[0])]
                    while name not in indexes:
                        await conv.send_message("Ops! O nome não está no formato correto. Por favor, digite um nome "
                                                "válido.")
                        name = await conv.get_response()
                        name = name.text

                    if event.data == b'botaoAtivarUsuarios':
                        df_users.at[int(name), 'ativo'] = True
                    elif event.data == b'botaoDesativarUsuarios':
                        df_users.at[int(name), 'ativo'] = False

                    df_users.to_csv(os.path.join(APP_STATIC, 'usuarios.csv'), index=False)
                    acao = 'ativado' if event.data == b'botaoAtivarUsuarios' else 'desativado'
                    await conv.send_message(f"Usuário {name} {acao} com sucesso!")
                finally:
                    print("ok")
        if event.data == b'botaoIniciarAppySaude':
            logger.info(f"Event {event.data} selected. Trying to get csv file...")
            try:
                id_user_telegram = sender.id
                user = await farmabot_client.get_entity(id_user_telegram)

                await event.respond("Aqui está seu arquivo 👇", parse_mode='html')

                path_appysaude_files = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'appysaude/files')
                arquivos = [file for file in os.listdir(path_appysaude_files) if
                            file.startswith('appysaude')]
                arquivos = sorted(arquivos)
                nome_ultimo_arquivo = arquivos[-1]
                nome_arquivo = f"{path_appysaude_files}/{nome_ultimo_arquivo}"
                await farmabot_client.send_file(user, nome_arquivo)
                logger.info(f"File {nome_arquivo} was sent with success to {id_user_telegram}")
            except Exception as e:
                logger.error(e)
                await event.respond(f"Ocorreu um erro ao buscar arquivo. Por favor, tente novamente em instantes",
                                    parse_mode='html')
        elif event.data in BOTOES_MENU_FARMA_BOT.keys():
            if event.data == b'botaoBuscaPorCNP':
                chat_with_user = await farmabot_client.get_entity(PeerUser(sender.id))
                async with farmabot_client.conversation(chat_with_user, timeout=300) as conv:
                    await conv.send_message(
                        '🤖 Por favor, envie um arquivo com a lista de CNPs nos formatos .csv ou .xlsx')
                    resposta_usuario = await conv.get_response()

                    while resposta_usuario.file is None:
                        await conv.send_message(
                            '🤖 Por favor, envie um arquivo. ')

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

                        start = time.time()

                        _produtos = await mec.scrap_urls_cnps(urls_cnps)

                        end = time.time()

                        total_time = round(end - start, 2)
                        logger.info(f"\nTempo para coletar dados de {len(urls_cnps)} urls no site: {total_time} segundos")

                        lista_produtos = []

                        l_produtos = [lp._result for lp in _produtos]

                        for l_produto in l_produtos:
                            for produto in l_produto:
                                lista_produtos.append(produto)

                        logger.info(f"Qtd produtos na Lista final: {len(lista_produtos)}")

                        l_final = await mec.transform_products_list(lista_produtos)

                        df = pd.DataFrame.from_records(l_final)

                        path_mecofarma_files = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                            'mecofarma/files')

                        df.to_csv(f'{path_mecofarma_files}/mecofarma-resultado-busca-por-cnp-{datetime.now().date()}.xlsx')

                        nome_arquivo = await mec.exportar_produtos_para_excel_cnp(df)

                        sender = await event.get_sender()
                        id_user_telegram = sender.id

                        user = await farmabot_client.get_entity(id_user_telegram)

                        await farmabot_client.send_file(user, nome_arquivo)
                        logger.info(f'Arquivo enviado com sucesso para o usuario {id_user_telegram}')
                    else:
                        await conv.send_message(
                            f'O arquivo precisa ter uma coluna chamada [codigo] ')
            elif event.data == b'botaoTodasCategorias':
                logger.info(f"Event {event.data} selected. Trying to get csv file...")
                try:
                    id_user_telegram = sender.id
                    user = await farmabot_client.get_entity(id_user_telegram)

                    await event.respond("Aqui está seu arquivo 👇", parse_mode='html')

                    path_mecofarma_files = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mecofarma/files')
                    arquivos = [file for file in os.listdir(path_mecofarma_files) if file.startswith('mecofarma-todas-as-categorias-2023')]
                    nome_ultimo_arquivo = arquivos[-1]
                    nome_arquivo = f"{path_mecofarma_files}/{nome_ultimo_arquivo}"
                    await farmabot_client.send_file(user, nome_arquivo)
                    logger.info(f"File {nome_arquivo} was sent with success to {id_user_telegram}")
                except Exception as e:
                    logger.error(e)
                    await event.respond(f"Ocorreu um erro ao buscar arquivo. Por favor, tente novamente em instantes",
                                        parse_mode='html')
            else:
                # TODO: Buscar por cada categoria
                pass


@farmabot_client.on(events.NewMessage(pattern='/mecofarma'))
async def mecofarma(event):
    sender = await event.get_sender()
    logger.info("/mecofarma requested")
    logger.info(f"New event arrived from user {sender.id}: {event}")
    send_message_to_telegram(f"New event arrived from user {sender.id}: {event}", CANAL_NOTIFICACOES_BETFAIR)
    user = await verify_user(sender)
    logger.info(f"User from CSV file: {user}")
    if user is None:
        logger.info(f"User not found")
        await event.respond(
            "Você não possui cadastro no FarmaBot. Por favor, clique no botão para iniciar o cadastro.",
            buttons=BOTAO_CADASTRO_FARMABOT)
    elif user['ativo'] is False:
        logger.info(f"User {user} is inactive")
        await event.respond("Você não está ativo. Por favor, fale com o ADM do FarmaBot para ativar sua conta",
                            parse_mode='html')
    else:
        await event.respond('🤖 Bem-vindo ao Web Scraping do site https://www.mecofarma.com')
        await event.respond('Escolha uma categoria para obter o arquivo mais recente dos dados coletados',
                            buttons=BOTOES_MECOFARMA)


@farmabot_client.on(events.NewMessage(pattern='/appysaude'))
async def appysaude(event):
    sender = await event.get_sender()
    logger.info("/appysaude requested")
    logger.info(f"New event arrived from user {sender.id}: {event}")
    send_message_to_telegram(f"[AppySaude] New event arrived from user {sender.id}: {event}", CANAL_NOTIFICACOES_BETFAIR)
    user = await verify_user(sender)
    logger.info(f"User from CSV file: {user}")
    if user is None:
        logger.info(f"User not found")
        await event.respond(
            "Você não possui cadastro no FarmaBot. Por favor, clique no botão para iniciar o cadastro.",
            buttons=BOTAO_CADASTRO_FARMABOT)
    elif user['ativo'] is False:
        logger.info(f"User {user} is inactive")
        await event.respond("Você não está ativo. Por favor, fale com o ADM do FarmaBot para ativar sua conta",
                            parse_mode='html')
    else:
        await event.respond('🤖 Bem-vindo ao Web Scraping do site https://www.appysaude.co.ao/home')
        await event.respond("Clique no botão abaixo para obter o último arquivo mais recente", buttons=BOTOES_APPYSAUDE)


@farmabot_client.on(events.NewMessage(pattern='/admin'))
async def admin(event):
    sender = await event.get_sender()
    logger.info("/admin requested")
    logger.info(f"New event arrived from user {sender.id}: {event}")
    user = await verify_user(sender)
    logger.info(f"User from CSV file: {user}")
    if user is not None and user['is_admin']:
        await event.respond('Olá adm! O que você deseja fazer?',
                            buttons=BOTOES_ADMIN_FARMABOT)
    else:
        await event.respond("Esta funcionalidade só está disponível para os ADMs do Farmabot.")


def main():
    logger.info(f"FarmaBot is ready ... Awaiting requests")
    farmabot_client.run_until_disconnected()


if __name__ == '__main__':
    import multiprocessing
    import platform

    logger.info(f"Plataform: {platform.system()}")
    logger.info(f"This machine has {multiprocessing.cpu_count()} CPU cores")
    main()
