from enum import Enum
from telethon import Button


class CategoriasMecofarma(Enum):
    SEXUALIDADE = 'Sexualidade'


class Chaves(str, Enum):
    API_ID = 3494250
    API_HASH = 'd3ada71e2f13b6701f420f0190e109dc'
    BOT_TOKEN = '896947138:AAH5NQ9aOajFKrRPXC8tlIX96rpjvgWbqJI'
    STRING_SESSION_BOT_DEV = '1AZWarzYBu04XImIE5wg5um5Wu6d1qxsVJuB4Nc-YL-WAZEYRUCAA76yLYMrY5jcIr6nqPGc56PS_lGWm7zEPQapy0iSjseCsRjDJXnVRc6k-tFwrlZfgi5KYQCtBJDBQZGShlmEUjLQFZy_s9DXYD7zokoZPYpjuzUJGeRCBuGevFMLRRd_CnPwaGpdDcKoNEluN4_aU_QQkjV0woaTjsITPRs9lzjd5mvkpd7Cbb2_tUCnw8sk-gCO_vClaz9Zd13TaTlqAooUxiKj6CbjW3rlv-u7OG8hEReNxbgycpvHfAonQiO5wMIsRWw6kTE1M4iBeAjrluFYP1i5R6wLxHPHfhPWpdGs='
    STRING_SESSION_BOT = "1AZWarzYBu3igFaQKgDJk9Cz0oQhVrx83lvPBGKLjOhiyiDUgXgZsKqtGbLlR7D3NGhswfiUSeaQDAhJWMsshuP0aNdurZOF8zhdSiabrQgGMtzJ8tysOvGhCcsy9_VusQMmpUCmyBqWOzEa9zl8fpsiePZlV-MlBd7myLNmNnlZZBq-MJpRf3gluV_ecXYLDRGWaQtl7vohKPm5MrL50hpkyEJomcKZnTsxDb594ewbT_o65FTSqOfZECZTMYZTyok3wleEDtMIoDqQOTbW4h_9BW2qLmDHMqPLKdKxW1R0GH0FUr8KsRmH3IUeX0YwiYTdo7uxZBKFtlR9etDda0lH-_jYr_lc="
    STRING_SESSION_SUPORTE_TELEGRAM = '1AZWarzgBu6VigJ8hfmgCI1yqITx5GY5667Vhez6t6k59lFm9Luccs7mG2-ZmM6BoW-C2IZhnrhM-3MFldDeST4OOgVNsQuNVUBnw5Llq8UorMTBfpbdnERkwWgg1RBOUpm_LsM1y9cux-KCT_RleiygMTiTOgwv1_w6wNVyx9jQOhUkTDFQcefVY7gJ1BkhqGJdlBwudUjKR-5-stk1BqHY-4HbE36N1MkFoSOfiVT9OSJ_-Nfza6FvzM4axh8P5vaMYR0WRUouS_5QX-0kRNM8aodV8oEFSy-HhJ54j8CvaSyX_JraOK_Ae88twJCiX-7x9nD_8Oyhr42OXA_ye3y7FfmswrRY='
    API_ID_TELEGRAM_SUPORTE = 3963044
    API_HASH_SUPORTE = '775d698043bd44e95e4a7eb11ad9b3ba'
    BOT_TOKEN_GREENVEST_BOT_DEV = '1827184808:AAEsY5rtxiRGTw--Q1KVp1V9ohy44JAOqiU'


BOTOES_MECOFARMA = [
    [Button.inline('💊 Farmácia', 'botaoFarmacia')],
    [Button.inline('🤱 Mamã e Bebé', 'botaoMamaebebe')],
    [Button.inline('💄 Saúde e Beleza', 'botaoSaudeeBeleza')],
    [Button.inline('⚧ Sexualidade', 'botaoSexualidade')],
    [Button.inline('🦴 Ortopedia', 'botaoOrtopedia')],
    [Button.inline('🏃 Vida Saudável', 'botaoVidaSaudavel')],
    [Button.inline('Todas as Categorias', 'botaoTodasCategorias')],
    [Button.inline('🔎 Busca por CNP', 'botaoBuscaPorCNP')],
]

BOTOES_MENU_FARMA_BOT = {
    b'botaoFarmacia': {
        "nome": "Farmácia",
        "link": "https://www.mecofarma.com/pt/farmacia"
    },
    b'botaoMamaebebe': {
        "nome": "Mamã e Bebé",
        "link": "https://www.mecofarma.com/pt/mam-e-bebe"
    },
    b'botaoSaudeeBeleza': {
        "nome": "Saúde e Beleza",
        "link": "https://www.mecofarma.com/pt/saude-e-beleza"
    },
    b'botaoSexualidade': {
        "nome": "Sexualidade",
        "link": "https://www.mecofarma.com/pt/sexualidade"
    },
    b'botaoOrtopedia': {
        "nome": "Ortopedia",
        "link": "https://www.mecofarma.com/pt/ortopedia"
    },
    b'botaoVidaSaudavel': {
         "nome": "Vida Saudável",
         "link": "https://www.mecofarma.com/pt/vida-saudavel"
     },
    b'botaoAcessorios': {
         "nome": "Acessórios e Dispositivos Médicos",
         "link": "https://www.mecofarma.com/pt/acessorios-e-dispositivos-medicos"
     },
    b'botaoTodasCategorias': {
        "nome": "Todas as Categorias",
        "link": "https://www.mecofarma.com"
    },
    b'botaoBuscaPorRef': {
        "nome": "Busca por REF",
        "link": "https://www.mecofarma.com/pt/saude-e-beleza"
    },
    b'botaoBuscaPorCNP': {
        "nome": "Busca por CNP",
        "link": ""
    }
}
