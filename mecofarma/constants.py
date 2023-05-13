from enum import Enum
from telethon import Button

NOME_ARQUIVO_TEMPORARIO = 'todas-as-categorias-temp'
NOME_ARQUIVO_FINAL = 'todas-as-categorias'

HTML_PARSER = 'html.parser'


class CategoriasMecofarma(Enum):
    SEXUALIDADE = 'Sexualidade'


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

BOTOES_ADMIN_MECOFARMA = [
    [Button.inline('💊 Farmácia', 'botaoFarmacia')],
    [Button.inline('🤱 Mamã e Bebé', 'botaoMamaebebe')],
    [Button.inline('💄 Saúde e Beleza', 'botaoSaudeeBeleza')],
    [Button.inline('⚧ Sexualidade', 'botaoSexualidade')],
    [Button.inline('🦴 Ortopedia', 'botaoOrtopedia')],
    [Button.inline('🏃 Vida Saudável', 'botaoVidaSaudavel')],
    [Button.inline('Todas as Categorias', 'botaoTodasCategorias')],
    [Button.inline('🔎 Busca por CNP', 'botaoBuscaPorCNP')],
    [Button.inline('Gerenciar Usuários', 'botaoGerenciarUsuarios')],
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
