import requests

URL_SALVAR_EMPRESA = "http://localhost:8000/api/v1/empresas"
URL_NOTA_FISCAL = "http://localhost:8000/api/v1/notasfiscais"
URL_ITEM_NOTA_FISCAL = "http://localhost:8000/api/v1/itens-notas-fiscais"


def salvar_empresa(dados_empresa: dict):
    response = requests.post(url=URL_SALVAR_EMPRESA, json=dados_empresa)

    if response.status_code == 201:
        print("Produto salvo com sucesso!")
    else:
        print("Erro ao salvar no banco:", response.status_code)

    return response


def consultar_empresa(cnpj_empresa: str):
    response = requests.get(url=f"{URL_SALVAR_EMPRESA}/{cnpj_empresa}")

    if response.status_code == 200:
        print("Empresa já existe")
    else:
        print("Erro ao salvar no banco:", response.status_code)

    return response


def consultar_nota_fiscal(chave_acesso: str):
    response = requests.get(url=f"{URL_NOTA_FISCAL}/{chave_acesso}")

    if response.status_code == 200:
        print(f"Nota Fiscal {chave_acesso} já existe")
    else:
        print("Erro ao salvar no banco:", response.status_code, chave_acesso)

    return response


def salvar_item_nota_fiscal(item_nota_fiscal: dict):
    response = requests.post(url=URL_ITEM_NOTA_FISCAL, json=item_nota_fiscal)

    if response.status_code == 201:
        print("Produto salvo com sucesso!")
    else:
        print("Erro ao salvar no banco:", response.status_code)

    return response


def salvar_nota_fiscal(nota_fiscal: dict):

    response = requests.post(url=URL_NOTA_FISCAL, json=nota_fiscal)

    if response.status_code == 201:
        print(f"{nota_fiscal} salva com sucesso!")
    else:
        print("Erro ao salvar nota fiscal no banco:", response.status_code, nota_fiscal, URL_NOTA_FISCAL)

    return response
