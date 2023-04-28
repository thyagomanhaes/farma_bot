from telethon import Button

'''
    await conv.send_message('choose', buttons=[[Button.inline('Yes'), Button.inline('No')]])

    await conv.send_message('<b> Want More ? </b>', parse_mode='html', buttons=[
        [Button.text('Yes', resize=True, single_use=True),
         Button.text('No', resize=True, single_use=True)],
        [Button.text('More', resize=True, single_use=True)]])
    await conv.send_message('🤖 Ops, não recebi nenhum arquivo!')
'''

URL_BUSCA_POR_CNP = "https://www.mecofarma.com/pt/search/ajax/suggest/?q="

BOTAO_CADASTRO_FARMABOT = [
    [Button.inline('Cadastrar', 'botaoCadastroFarmaBot')],
]

BOTAO_AREA_ADMIN = [
    [Button.inline('ÁREA ADMINISTRATIVA', 'botaoCadastroFarmaBot')],
]

BOTOES = [
    [Button.text('Yes', resize=True, single_use=True),
     Button.text('No', resize=True, single_use=True)],
    [Button.text('More', resize=True, single_use=True)]]
