import asyncio
import json

import pandas as pd

from mecofarma.mecofarma_paralelo import scrap_urls_subcategorias

# try:
#     df_usuarios = pd.read_csv('usuarios.csv')
#
#     id_user_telegram = 467091700
#
#     df2 = df_usuarios[df_usuarios['id_usuario_telegram'] == 467091700]
#     if not df2.empty:
#         if bool(df2['ativo'].values[0]) is True:
#             print("pode seguir")
#     else:
#         print("gfsdfsdf")
#
#
# except FileNotFoundError as err:
#     print("Nao existe")

subs = [
    {
        'categoria': 'Farmácia',
        'subcategoria': 'Dor e Febre',
        'qtd_itens_subcategoria': 72,
        'link_subcategoria': 'https://www.mecofarma.com/pt/farmacia/dor-e-febre?p=1&product_list_limit=36'
    },
    {
        'categoria': 'Farmácia',
        'subcategoria': 'Dor e Febre',
        'qtd_itens_subcategoria': 72,
        'link_subcategoria': 'https://www.mecofarma.com/pt/farmacia/dor-e-febre?p=2&product_list_limit=36'
    }
]


def write_list_of_ngram_dicts(list_of_dicts, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        for dic in list_of_dicts:
            data = json.dumps(dic)
            file.write(data)
            file.write("\n")


# _produtos = scrap_urls_subcategorias(subs)
# lista_produtos = []
#
# l_produtos = [lp._result for lp in _produtos]
#
# for l_produto in l_produtos:
#     for produto in l_produto:
#         lista_produtos.append(produto)
#
# print(len(lista_produtos))

l3 = [
    {
        'ok': 1,
        'qui': 2
    },
    {
        'ok': 1,
        'qui': 2
    }

]
write_list_of_ngram_dicts(l3, 'teste.txt')
